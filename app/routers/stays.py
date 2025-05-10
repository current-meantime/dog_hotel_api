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

router = APIRouter(prefix="/stays", tags=["Stays"])
log = logging.getLogger(__name__)

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
    log.info(
        f"Searching stays with filters: min_days={min_days}, max_days={max_days}, "
        f"status={status}, year={year}, month={month}, day={day}, "
        f"start_date_from={start_date_from}, start_date_to={start_date_to}, "
        f"dog_id={dog_id}, owner_id={owner_id}"
    )
    
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
    log.info(f"Fetching stay with id: {stay_id}")
    existing_stay = db.execute(
        select(StayModel).where(StayModel.id == stay_id)
    ).scalars().first()

    if not existing_stay:
        log.warning(f"Stay with id {stay_id} not found")
        raise HTTPException(status_code=404, detail="Stay not found")
    
    return existing_stay

@router.post("/", response_model=StayRead)
def create_stay(stay_data: StayCreate, db: Session = Depends(get_db)):
    log.info(f"Creating new stay for dog_id: {stay_data.dog_id}, owner_id: {stay_data.owner_id}")
    
    # Validate dates
    if stay_data.end_date < stay_data.start_date:
        log.warning(f"Invalid dates: end_date {stay_data.end_date} before start_date {stay_data.start_date}")
        raise HTTPException(
            status_code=400,
            detail="End date cannot be earlier than start date"
        )
    
    # Check for overlapping stays
    overlapping_stay = db.execute(
        select(StayModel).where(
            StayModel.dog_id == stay_data.dog_id,
            StayModel.start_date <= stay_data.end_date,
            StayModel.end_date >= stay_data.start_date
        )
    ).scalars().first()
    
    if overlapping_stay:
        log.warning(
            f"Overlapping stay found for dog_id: {stay_data.dog_id}, "
            f"owner_id: {stay_data.owner_id}, dates: {stay_data.start_date} - {stay_data.end_date}"
        )
        raise HTTPException(
            status_code=400, 
            detail="Overlapping stay exists for this dog and owner"
        )

    try:
        new_stay = StayModel(**stay_data.model_dump())
        db.add(new_stay)
        db.commit()
        db.refresh(new_stay)
        
        payment = PaymentModel(
            stay_id=new_stay.id,
            is_paid=False,
            is_overdue=0,
            overdue_days=0
        )
        payment.amount = payment.calculate_amount(db)
        db.add(payment)
        db.commit()
        db.refresh(payment)
        
        log.info(f"Successfully created stay {new_stay.id} with payment {payment.id}")
        return new_stay
        
    except Exception as e:
        db.rollback()
        log.error(f"Error creating stay: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error creating stay: {str(e)}")

@router.put("/{stay_id}", response_model=StayRead)
def update_stay(stay_id: int, update_data: StayUpdate, db: Session = Depends(get_db)):
    log.info(f"Updating stay {stay_id}")
    existing_stay = db.execute(
        select(StayModel).where(StayModel.id == stay_id)
    ).scalars().first()

    if not existing_stay:
        log.warning(f"Update failed: Stay with ID {stay_id} not found.")
        raise HTTPException(status_code=404, detail="Stay doesn't exist")

    # Ustal nowe daty (z danych aktualizacji lub obecnych z bazy)
    new_start = update_data.start_date or existing_stay.start_date
    new_end = update_data.end_date or existing_stay.end_date

    # Walidacja dat
    if new_end < new_start:
        log.warning(f"Invalid date update for stay {stay_id}: start={new_start}, end={new_end}")
        raise HTTPException(status_code=400, detail="End date cannot be earlier than start date.")

    try:
        for key, value in update_data.model_dump(exclude_unset=True).items():
            setattr(existing_stay, key, value)

        db.commit()
        db.refresh(existing_stay)

        log.info(f"Stay {stay_id} successfully updated.")
        return existing_stay

    except Exception as e:
        db.rollback()
        log.error(f"Error updating stay {stay_id}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to update stay.")


@router.delete("/{stay_id}", response_model=StayRead)
def delete_dog(stay_id, db: Session=Depends(get_db)):
    log.info(f"Attempting to delete stay {stay_id}")
    existing_stay = db.execute(
        select(StayModel).where(StayModel.id == stay_id)
    ).scalars().first()

    if not existing_stay:
        log.warning(f"Stay {stay_id} not found for deletion")
        raise HTTPException(status_code=400, detail="Stay does not exist")
    
    try:
        db.delete(existing_stay)
        db.commit()
        log.info(f"Successfully deleted stay {stay_id}")
        return existing_stay
    except Exception as e:
        log.error(f"Error deleting stay {stay_id}: {str(e)}", exc_info=True)
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to delete stay")



