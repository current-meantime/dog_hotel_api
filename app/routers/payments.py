from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.models.payment import Payment as PaymentModel
from app.models.stay import Stay
from app.schemas.payment import PaymentCreate, PaymentRead
from app.database.database import get_db

router = APIRouter(prefix="/payments", tags=["Payments"])

@router.get("/", response_model=list[PaymentRead])
def search_payments(
    stay_id: int = None,
    is_paid: bool = None,
    overdue_only: bool = None,
    db: Session = Depends(get_db),
):
    query = select(PaymentModel)

    if stay_id is not None:
        query = query.where(PaymentModel.stay_id == stay_id)

    if is_paid is not None:
        query = query.where(PaymentModel.is_paid == is_paid)

    if overdue_only:
        query = query.where(PaymentModel.overdue_30_days > 0)

    payments = db.execute(query).scalars().all()
    return payments

@router.get("/{payment_id}", response_model=PaymentRead)
def get_payment(payment_id: int, db: Session = Depends(get_db)):
    payment = db.execute(
        select(PaymentModel).where(PaymentModel.id == payment_id)
    ).scalars().first()
    
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")
    
    return payment

@router.post("/", response_model=PaymentRead)
def create_payment(payment_create: PaymentCreate, db: Session = Depends(get_db)):
    stay = db.execute(select(Stay).where(Stay.id == payment_create.stay_id)).scalars().first()
    if not stay:
        raise HTTPException(status_code=404, detail="Stay not found")

    payment = PaymentModel(
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
