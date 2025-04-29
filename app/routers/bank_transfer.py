from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.models.bank_transfer import BankTransfer as BankTransferModel
from app.schemas.bank_transfer import BankTransferRead, BankTransferCreate
from app.database.database import get_db

router = APIRouter(prefix="/bank_transfers", tags=["Bank Transfers"])

@router.get("/", response_model=list[BankTransferRead])
def list_transfers(db: Session = Depends(get_db)):
    transfers = db.execute(select(BankTransferModel)).scalars().all()
    return transfers

@router.post("/", response_model=BankTransferRead)
def create_transfer(transfer: BankTransferCreate, db: Session = Depends(get_db)):
    new_transfer = BankTransferModel(**transfer.model_dump())
    db.add(new_transfer)
    db.commit()
    db.refresh(new_transfer)
    return new_transfer