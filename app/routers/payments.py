from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.models.payment import Payment as PaymentModel
from app.models.stay import Stay as StayModel
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
    owner_id: Optional[int] = None,
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
        
    if owner_id is not None:
        stmt = stmt.where(StayModel.owner_id == owner_id)

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

@router.post("/", response_model=PaymentRead)
def create_payment(payment_create: PaymentCreate, db: Session = Depends(get_db)):
    stay = db.execute(select(StayModel).where(StayModel.id == payment_create.stay_id)).scalars().first()
    if not stay:
        raise HTTPException(status_code=404, detail="Stay not found")
    
    existing_payment = db.execute(
        select(PaymentModel).where(
            PaymentModel.stay_id == payment_create.stay_id
        )
    ).scalars().first()
    
    if existing_payment:
        raise HTTPException(status_code=400, detail="Payment already exists for this stay")

    payment = PaymentModel(
    stay_id=stay.id,
    is_paid=payment_create.is_paid,
    is_overdue=payment_create.is_overdue,
    overdue_days=payment_create.overdue_days
)
    
    # Wyliczamy kwotę na podstawie metody calculate_amount
    payment.amount = payment.calculate_amount(db)

    db.add(payment)
    db.commit()
    db.refresh(payment)
    return payment

@router.put("/{payment_id}", response_model=PaymentRead)
def update_payment(payment_id: int, payment_update: PaymentCreate, db: Session = Depends(get_db)):
    # Sprawdzenie, czy płatność istnieje
    existing_payment = db.execute(
        select(PaymentModel).where(PaymentModel.id == payment_id)
    ).scalars().first()

    if not existing_payment:
        raise HTTPException(status_code=404, detail="Payment not found")
    
    # Sprawdzenie, czy stay istnieje
    stay = db.execute(select(StayModel).where(StayModel.id == payment_update.stay_id)).scalars().first()
    if not stay:
        raise HTTPException(status_code=404, detail="Stay not found")

    # Aktualizacja pól płatności
    existing_payment.stay_id = stay.id
    existing_payment.is_paid = payment_update.is_paid
    existing_payment.is_overdue = payment_update.is_overdue
    existing_payment.overdue_days = payment_update.overdue_days

    # Ponowne obliczenie kwoty, jeśli jest to wymagane
    existing_payment.amount = existing_payment.calculate_amount(db)

    # Zapisz zmiany do bazy danych
    db.commit()
    db.refresh(existing_payment)

    return existing_payment


@router.delete("/{payment_id}", response_model=PaymentRead)
def delete_payment(payment_id, db: Session=Depends(get_db)):
    existing_payment = db.execute(
        select(PaymentModel).where(PaymentModel.id == payment_id)
    ).scalars().first()

    if not existing_payment:
        raise HTTPException(status_code=400, detail="Stay does not exist")
    
    db.delete(existing_payment)
    db.commit()

    return existing_payment
