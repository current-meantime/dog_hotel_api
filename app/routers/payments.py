from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.models.payment import Payment as PaymentModel
from app.models.stay import Stay as StayModel
from app.schemas.payment import PaymentCreate, PaymentRead
from app.database.database import get_db
from typing import Optional
import logging

router = APIRouter(prefix="/payments", tags=["Payments"])
log = logging.getLogger(__name__)

@router.get("/", response_model=list[PaymentRead])
def search_payments(
    stay_id: Optional[bool] = None,
    is_paid: Optional[bool] = None,
    is_overdue: Optional[bool] = None,
    is_overdue_30_days: Optional[bool] = None,
    owner_id: Optional[int] = None,
    db: Session = Depends(get_db),
):
    log.info(f"Searching payments with filters: stay_id={stay_id}, is_paid={is_paid}, is_overdue={is_overdue}, is_overdue_30_days={is_overdue_30_days}, owner_id={owner_id}")

    stmt = select(PaymentModel)

    if stay_id is not None:
        stmt = stmt.where(PaymentModel.stay_id == stay_id)

    if is_paid is not None:
        stmt = stmt.where(PaymentModel.is_paid == is_paid)

    if is_overdue is not None:
        stmt = stmt.where(PaymentModel.is_overdue == is_overdue)

    if is_overdue_30_days:
        stmt = stmt.where(PaymentModel.overdue_days >= 30)
        
    if owner_id is not None:
        stmt = stmt.where(StayModel.owner_id == owner_id)

    payments = db.execute(stmt).scalars().all()
    return payments


@router.get("/{payment_id}", response_model=PaymentRead)
def get_payment(payment_id: int, db: Session = Depends(get_db)):
    log.info(f"Fetching payment with id: {payment_id}")
    payment = db.execute(
        select(PaymentModel).where(PaymentModel.id == payment_id)
    ).scalars().first()
    
    if not payment:
        log.warning(f"Payment with id {payment_id} not found")
        raise HTTPException(status_code=404, detail="Payment not found")
    
    return payment

@router.post("/", response_model=PaymentRead)
def create_payment(payment_create: PaymentCreate, db: Session = Depends(get_db)):
    log.info(f"Creating new payment for stay_id: {payment_create.stay_id}")
    
    stay = db.execute(select(StayModel).where(StayModel.id == payment_create.stay_id)).scalars().first()
    if not stay:
        log.error(f"Stay with id {payment_create.stay_id} not found")
        raise HTTPException(status_code=404, detail="Stay not found")
    
    existing_payment = db.execute(
        select(PaymentModel).where(PaymentModel.stay_id == payment_create.stay_id)
    ).scalars().first()
    
    if existing_payment:
        log.warning(f"Payment already exists for stay {payment_create.stay_id}")
        raise HTTPException(status_code=400, detail="Payment already exists for this stay")

    try:
        payment = PaymentModel(
            stay_id=stay.id,
            is_paid=payment_create.is_paid,
            is_overdue=payment_create.is_overdue,
            overdue_days=payment_create.overdue_days
        )
        payment.amount = payment.calculate_amount(db)
        db.add(payment)
        db.commit()
        db.refresh(payment)
        log.info(f"Successfully created payment {payment.id} for stay {stay.id}")
        return payment
    except Exception as e:
        log.error(f"Error creating payment for stay {stay.id}: {str(e)}", exc_info=True)
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{payment_id}", response_model=PaymentRead)
def update_payment(payment_id: int, payment_update: PaymentCreate, db: Session = Depends(get_db)):
    log.info(f"Updating payment {payment_id}")
    
    existing_payment = db.execute(
        select(PaymentModel).where(PaymentModel.id == payment_id)
    ).scalars().first()

    if not existing_payment:
        log.warning(f"Payment {payment_id} not found for update")
        raise HTTPException(status_code=404, detail="Payment not found")
    
    stay = db.execute(select(StayModel).where(StayModel.id == payment_update.stay_id)).scalars().first()
    if not stay:
        log.error(f"Stay {payment_update.stay_id} not found for payment update")
        raise HTTPException(status_code=404, detail="Stay not found")

    try:
        existing_payment.stay_id = stay.id
        existing_payment.is_paid = payment_update.is_paid
        existing_payment.is_overdue = payment_update.is_overdue
        existing_payment.overdue_days = payment_update.overdue_days
        existing_payment.amount = existing_payment.calculate_amount(db)
        
        db.commit()
        db.refresh(existing_payment)
        log.info(f"Successfully updated payment {payment_id}")
        return existing_payment
    except Exception as e:
        log.error(f"Error updating payment {payment_id}: {str(e)}", exc_info=True)
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to update payment")

@router.delete("/{payment_id}", response_model=PaymentRead)
def delete_payment(payment_id, db: Session=Depends(get_db)):
    log.info(f"Attempting to delete payment {payment_id}")
    
    existing_payment = db.execute(
        select(PaymentModel).where(PaymentModel.id == payment_id)
    ).scalars().first()

    if not existing_payment:
        log.warning(f"Payment {payment_id} not found for deletion")
        raise HTTPException(status_code=400, detail="Payment does not exist")
    
    try:
        db.delete(existing_payment)
        db.commit()
        log.info(f"Successfully deleted payment {payment_id}")
        return existing_payment
    except Exception as e:
        log.error(f"Error deleting payment {payment_id}: {str(e)}", exc_info=True)
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to delete payment")