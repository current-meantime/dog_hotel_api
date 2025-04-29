from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import extract, select, func
from app.models.stay import Stay as StayModel
from app.models.owner import Owner as OwnerModel
from app.models.payment import Payment as PaymentModel
from app.models.dog import Dog as DogModel  
from app.schemas.stay import StayRead, StayCreate, StayUpdate
from app.database.database import get_db
from datetime import date, timedelta
from typing import Optional
import logging

log = logging.getLogger("stays_logger")
log.setLevel(logging.INFO)

router = APIRouter(prefix="/stays", tags=["Stays"])

@router.get("/", response_model=list[StayRead])
def search_stays(
    min_days: Optional[int] = None,
    max_days: Optional[int] = None,
    status: Optional[str] = None, # "upcoming", "ongoing", "ending_soon"
    year: Optional[int] = None,
    month: Optional[int] = None,
    day: Optional[int] = None,
    start_date_from: Optional[date] = None,
    start_date_to: Optional[date] = None,
    dog_id: Optional[int] = None,
    owner_id: Optional[int] = None,
    db: Session = Depends(get_db),
):
    query = select(StayModel)
    today = date.today()

    # Filtruj status (upcoming, ongoing, ending_soon)
    if status:
        if status == "upcoming":
            query = query.where(StayModel.start_date > today)
        elif status == "ongoing":
            query = query.where(
                StayModel.start_date <= today,
                StayModel.end_date >= today
            )
        elif status == "ending_soon":
            soon = today + timedelta(days=7)
            query = query.where(
                StayModel.end_date >= today,
                StayModel.end_date <= soon
            )
        else:
            raise HTTPException(status_code=400, detail="Invalid status value")

    # Filtruj po długości pobytu
    if min_days is not None:
        query = query.where(
            func.julianday(StayModel.end_date) - func.julianday(StayModel.start_date) + 1 >= min_days
        )
    if max_days is not None:
        query = query.where(
            func.julianday(StayModel.end_date) - func.julianday(StayModel.start_date) + 1 <= max_days
        )

    # Filtruj po dacie rozpoczęcia
    if year:
        query = query.where(extract('year', StayModel.start_date) == year)
    if month:
        query = query.where(extract('month', StayModel.start_date) == month)
    if day:
        query = query.where(extract('day', StayModel.start_date) == day)

    if start_date_from:
        query = query.where(StayModel.start_date >= start_date_from)
    if start_date_to:
        query = query.where(StayModel.start_date <= start_date_to)
        
    if dog_id is not None:
        query = query.where(StayModel.dog_id == dog_id)

    if owner_id is not None:
        query = query.where(StayModel.owner_id == owner_id)

    stays = db.execute(query).scalars().all()

    return stays

@router.get("/{stay_id}", response_model=StayRead)
def get_stay(stay_id, db: Session=Depends(get_db)):
    existing_stay = db.execute(
        select(StayModel).where(StayModel.id == stay_id)
    ).scalars().first()

    if not existing_stay:
        raise HTTPException(status_code=404, detail="Stay not found")
    
    return existing_stay

@router.post("/", response_model=StayRead) #TODO: add date validation or check if it's by default validated in pydantic model
def create_stay(stay_data: StayCreate, db: Session = Depends(get_db)):
    # Sprawdzamy, czy właściciel istnieje
    owner = db.execute(
        select(OwnerModel).where(OwnerModel.id == stay_data.owner_id)
    ).scalars().first()
    if not owner:
        raise HTTPException(status_code=400, detail="Owner does not exist")

    # Sprawdzamy, czy pies istnieje
    dog = db.execute(
        select(DogModel).where(DogModel.id == stay_data.dog_id)
    ).scalars().first()
    if not dog:
        raise HTTPException(status_code=400, detail="Dog does not exist")

    # Sprawdzamy, czy nie istnieje nakładający się pobyt
    overlapping_stay = db.execute(
        select(StayModel).where(
            StayModel.dog_id == stay_data.dog_id,
            StayModel.owner_id == stay_data.owner_id,
            StayModel.start_date <= stay_data.end_date,
            StayModel.end_date >= stay_data.start_date
        )
    ).scalars().first()
    if overlapping_stay:
        raise HTTPException(status_code=400, detail="Overlapping stay exists for this dog and owner")

    # Tworzymy nowy pobyt
    new_stay = StayModel(**stay_data.model_dump())
    db.add(new_stay)
    db.commit()
    db.refresh(new_stay)

    # Tworzymy płatność dla tego pobytu
    payment = PaymentModel(
        stay_id=new_stay.id,
        is_paid=False,
        is_overdue=0,
        overdue_days=0
        
    )
    
    try:
        payment.amount = payment.calculate_amount(db)
    except Exception as e:
        db.rollback()
        log.error(f"Error calculating payment: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error calculating payment: {str(e)}")

    db.add(payment)
    db.commit()
    db.refresh(payment)

    return new_stay

@router.put("/{stay_id}", response_model=StayRead)
def update_stay(stay_id: int, update_data: StayUpdate, db: Session = Depends(get_db)):
    existing_stay = db.execute(
        select(StayModel).where(StayModel.id == stay_id)
    ).scalars().first()

    if not existing_stay:
        raise HTTPException(status_code=400, detail="Stay doesn't exist")

    # Aktualizujemy dane pobytu
    for key, value in update_data.model_dump(exclude_unset=True).items():
        setattr(existing_stay, key, value)
        
    db.commit()
    db.refresh(existing_stay)
    
    return existing_stay

@router.delete("/{stay_id}", response_model=StayRead)
def delete_dog(stay_id, db: Session=Depends(get_db)):
    existing_stay = db.execute(
        select(StayModel).where(StayModel.id == stay_id)
    ).scalars().first()

    if not existing_stay:
        raise HTTPException(status_code=400, detail="Stay does not exist")
    
    db.delete(existing_stay)
    db.commit()

    return existing_stay




