from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.services.update_payments_from_transfers import process_bank_transfers

router = APIRouter(prefix="/scheduler", tags=["Scheduler"])

@router.post("/run-bank-transfer-scheduler")
def run_scheduler_endpoint(db: Session = Depends(get_db)):
    process_bank_transfers(db)
    return {"detail": "Bank transfer scheduler ran successfully"}