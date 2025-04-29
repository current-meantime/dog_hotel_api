from fastapi import FastAPI
from app.database.database import Base, engine, Session
from app.services.update_dog_ages import update_dog_ages
from apscheduler.schedulers.background import BackgroundScheduler
from app.routers import dogs, owners, payments, stays
import logging
from app.routers import bank_transfers
from app.routers import bank_transfer_scheduler
from app.services.update_payments_from_transfers import process_bank_transfers

from app.models import owner, dog, stay, payment  # do not remove, they need to be initialized before create_all()

Base.metadata.create_all(bind=engine)

app = FastAPI()

app.include_router(dogs.router)
app.include_router(owners.router)
app.include_router(payments.router)
app.include_router(stays.router)
app.include_router(bank_transfers.router)
app.include_router(bank_transfer_scheduler.router)


# Funkcja do uruchomienia aktualizacji raz w roku
def scheduled_update():
    print("Scheduled update triggered.")  # Debugging print
    logging.getLogger("update_logger").info("Scheduled update triggered.")
    db = Session(bind=engine)
    update_dog_ages(db)
    process_bank_transfers(db)  # <--- uruchamiamy automatyczne dopasowanie przelewów
    db.close()

# Scheduler
scheduler = BackgroundScheduler()
scheduler.add_job(scheduled_update, 'interval', seconds=200)  # change to days=1
scheduler.start()

@app.on_event("shutdown")
def shutdown():
    scheduler.shutdown()
    
# adding a comment to check somthing out in git