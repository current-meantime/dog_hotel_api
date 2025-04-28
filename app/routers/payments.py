from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.models.payment import Payment
from app.models.stay import Stay
from app.schemas.payment import PaymentCreate, PaymentRead
from app.database.database import get_db

router = APIRouter(prefix="/payments", tags=["Payments"])

@router.get("/payments", response_model=list[PaymentRead])
def read_payments(db: Session = Depends(get_db)):
    payments = db.execute(
        select(Payment)
    ).scalars().all()
    return payments

@router.get("/payments/{payment_id}", response_model=PaymentRead)
def get_payment(payment_id: int, db: Session = Depends(get_db)):
    payment = db.execute(
        select(Payment).where(Payment.id == payment_id)
    ).scalars().first()
    
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")
    
    return payment

@router.get("/unpaid", response_model=list[PaymentRead])
def get_unpaid_payments(db: Session = Depends(get_db)):
    unpaid_payments = db.execute(
        select(Payment).where(Payment.is_paid == False)
    ).scalars().all()
    
    return unpaid_payments

@router.get("/overdue", response_model=list[PaymentRead])
def get_overdue_payments(db: Session = Depends(get_db)):
    overdue_payments = db.execute(
        select(Payment).where(Payment.overdue_30_days > 0)
    ).scalars().all()
    
    return overdue_payments

@router.post("/payments", response_model=PaymentRead) #TODO: wywoływać tę funkcję automatycznie przy tworzeniu stay
def create_payment(payment_create: PaymentCreate, db: Session = Depends(get_db)):
    stay = db.execute(select(Stay).where(Stay.id == payment_create.stay_id)).scalars().first()
    if not stay:
        raise HTTPException(status_code=404, detail="Stay not found")

    payment = Payment(
        stay_id=stay.id,
        is_paid=payment_create.is_paid,
        overdue_30_days=payment_create.overdue_30_days
    )
    
    # Wyliczamy kwotę na podstawie metody calculate_amount
    payment.amount = payment.calculate_amount()

    db.add(payment)
    db.commit()
    db.refresh(payment)
    return payment
