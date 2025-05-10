from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.models.bank_transfer import BankTransfer as BankTransferModel
from app.schemas.bank_transfer import BankTransferRead, BankTransferCreate, BankTransferUpdate
from app.database.database import get_db
from typing import Optional
import logging

router = APIRouter(prefix="/bank_transfers", tags=["Bank Transfers"])
log = logging.getLogger(__name__)

@router.get("/", response_model=list[BankTransferRead])
def list_transfers(
    sender_name: Optional[str] = None,
    matched: Optional[bool] = None,
    db: Session = Depends(get_db)
):
    log.info(f"Searching transfers with filters: sender_name={sender_name}, matched={matched}")
    stmt = select(BankTransferModel)

    if sender_name:
        stmt = stmt.where(BankTransferModel.sender_name.ilike(f"%{sender_name.strip().lower()}%"))

    if matched is not None:
        if matched:
            stmt = stmt.where(BankTransferModel.matched_payment_id.is_not(None))
        else:
            stmt = stmt.where(BankTransferModel.matched_payment_id.is_(None))
        log.debug(f"Filtering by matched status: {matched}")

    transfers = db.execute(stmt).scalars().all()
    return transfers

@router.get("/{transfer_id}", response_model=BankTransferRead)
def get_transfer(transfer_id: int, db: Session = Depends(get_db)):
    log.info(f"Fetching bank transfer with id: {transfer_id}")
    transfer = db.execute(
        select(BankTransferModel).where(BankTransferModel.id == transfer_id)
    ).scalars().first()
    
    if not transfer:
        log.warning(f"Bank transfer with id {transfer_id} not found")
        raise HTTPException(status_code=404, detail="Bank transfer not found")
    
    return transfer

@router.post("/", response_model=BankTransferRead)
def create_transfer(transfer: BankTransferCreate, db: Session = Depends(get_db)):
    log.info(f"Creating new bank transfer from {transfer.sender_name}")
    try:
        new_transfer = BankTransferModel(**transfer.model_dump())
        db.add(new_transfer)
        db.commit()
        db.refresh(new_transfer)
        log.info(f"Successfully created bank transfer {new_transfer.id}")
        return new_transfer
    except Exception as e:
        log.error(f"Error creating bank transfer: {str(e)}", exc_info=True)
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to create bank transfer")

@router.put("/{transfer_id}", response_model=BankTransferRead)
def update_transfer(
    transfer_id: int, 
    update_data: BankTransferUpdate, 
    db: Session = Depends(get_db)
):
    log.info(f"Updating bank transfer {transfer_id}")
    
    existing_transfer = db.execute(
        select(BankTransferModel).where(BankTransferModel.id == transfer_id)
    ).scalars().first()

    if not existing_transfer:
        log.warning(f"Bank transfer {transfer_id} not found for update")
        raise HTTPException(status_code=404, detail="Bank transfer not found")

    try:
        for key, value in update_data.model_dump(exclude_unset=True).items():
            setattr(existing_transfer, key, value)

        db.commit()
        db.refresh(existing_transfer)
        log.info(f"Successfully updated bank transfer {transfer_id}")
        return existing_transfer
    except Exception as e:
        log.error(f"Error updating bank transfer {transfer_id}: {str(e)}", exc_info=True)
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to update bank transfer")

@router.delete("/{transfer_id}", response_model=BankTransferRead)
def delete_transfer(transfer_id: int, db: Session = Depends(get_db)):
    log.info(f"Attempting to delete bank transfer {transfer_id}")
    
    existing_transfer = db.execute(
        select(BankTransferModel).where(BankTransferModel.id == transfer_id)
    ).scalars().first()

    if not existing_transfer:
        log.warning(f"Bank transfer {transfer_id} not found for deletion")
        raise HTTPException(status_code=404, detail="Bank transfer not found")
    
    try:
        db.delete(existing_transfer)
        db.commit()
        log.info(f"Successfully deleted bank transfer {transfer_id}")
        return existing_transfer
    except Exception as e:
        log.error(f"Error deleting bank transfer {transfer_id}: {str(e)}", exc_info=True)
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to delete bank transfer")