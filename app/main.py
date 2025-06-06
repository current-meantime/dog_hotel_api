from fastapi import FastAPI
from app.database.database import Base, engine, Session
from app.services.update_dog_ages import update_dog_ages
from apscheduler.schedulers.background import BackgroundScheduler
from app.routers import dogs, owners, payments, stays
import logging
from app.routers import bank_transfers
from app.routers import bank_transfer_scheduler
from app.services.update_payments_from_transfers import update_payments_from_transfers
from app.utils.logging_config import setup_logging

from app.models.owner import Owner
from app.models.dog import Dog
from app.models.stay import Stay
from app.models.payment import Payment
from app.models.bank_transfer import BankTransfer

setup_logging()

Base.metadata.create_all(bind=engine)

app = FastAPI()

app.include_router(dogs.router)
app.include_router(owners.router)
app.include_router(payments.router)
app.include_router(stays.router)
app.include_router(bank_transfers.router)
app.include_router(bank_transfer_scheduler.router)

@app.get("/")
def read_root():
    return {"message": "Welcome to the Dog Hotel API"}

# Funkcja do uruchomienia aktualizacji raz w roku
def scheduled_update():
    print("Scheduled update triggered.")  # Debugging print
    logging.getLogger("update_logger").info("Scheduled update triggered.")
    db = Session(bind=engine)
    update_dog_ages(db)
    update_payments_from_transfers(db)  # <--- uruchamiamy automatyczne dopasowanie przelewów
    db.close()

# Scheduler
scheduler = BackgroundScheduler()
scheduler.add_job(scheduled_update, 'interval', seconds=200)  # change to days=1
scheduler.start()

@app.on_event("shutdown")
def shutdown():
    scheduler.shutdown()