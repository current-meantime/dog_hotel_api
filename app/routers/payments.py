from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.models.payment import Payment as PaymentModel
from app.models.stay import Stay
from app.schemas.payment import PaymentCreate, PaymentRead
from app.database.database import get_db
from typing import Optional

router = APIRouter(prefix="/payments", tags=["Payments"])

@router.get("/", response_model=list[PaymentRead])
def search_payments(
    stay_id: Optional[bool] = None,
    is_paid: Optional[bool] = None,
    is_overdue: Optional[bool] = None,
    is_overdue_30_days: Optional[bool] = None,
    db: Session = Depends(get_db),
):
    stmt = select(PaymentModel)

    if stay_id is not None:
        stmt = stmt.where(PaymentModel.stay_id == stay_id)

    if is_paid is not None:
        stmt = stmt.where(PaymentModel.is_paid == is_paid)

    if is_overdue is not None:
        stmt = stmt.where(PaymentModel.is_overdue == is_overdue)

    if is_overdue_30_days:
        stmt = stmt.where(PaymentModel.overdue_days >= 30)

    payments = db.execute(stmt).scalars().all()
    return payments


@router.get("/{payment_id}", response_model=PaymentRead)
def get_payment(payment_id: int, db: Session = Depends(get_db)):
    payment = db.execute(
        select(PaymentModel).where(PaymentModel.id == payment_id)
    ).scalars().first()
    
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")
    
    return payment

@router.post("/", response_model=PaymentRead) #TODO: wywoływać tę funkcję automatycznie przy tworzeniu stay
def create_payment(payment_create: PaymentCreate, db: Session = Depends(get_db)):
    stay = db.execute(select(Stay).where(Stay.id == payment_create.stay_id)).scalars().first()
    if not stay:
        raise HTTPException(status_code=404, detail="Stay not found")

    payment = PaymentModel(
    stay_id=stay.id,
    is_paid=payment_create.is_paid,
    is_overdue=payment_create.is_overdue,
    overdue_days=payment_create.overdue_days
)
    
    # Wyliczamy kwotę na podstawie metody calculate_amount
    payment.amount = payment.calculate_amount()

    db.add(payment)
    db.commit()
    db.refresh(payment)
    return payment

@router.delete("/{payment_id}", response_model=PaymentRead)
def delete_dog(payment_id, db: Session=Depends(get_db)):
    existing_payment = db.execute(
        select(PaymentModel).where(PaymentModel.id == payment_id)
    ).scalars().first()

    if not existing_payment:
        raise HTTPException(status_code=400, detail="Stay does not exist")
    
    db.delete(existing_payment)
    db.commit()

    return existing_payment
