from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import extract, select, func
from app.models.stay import Stay as StayModel
from app.models.owner import Owner as OwnerModel
from app.models.dog import Dog as DogModel  
from app.schemas.stay import StayRead, StayCreate, StayUpdate
from app.database.database import get_db
from datetime import date, timedelta
from typing import Optional

router = APIRouter(prefix="/stays", tags=["Stays"])

@router.get("/", response_model=list[StayRead])
def search_stays(
    min_days: Optional[int] = None,
    max_days: Optional[int] = None,
    status: Optional[str] = None, # "upcoming", "ongoing", "ending_soon"
    db: Session = Depends(get_db)
):
    query = select(StayModel)

    today = date.today()

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

    if min_days is not None:
        query = query.where(
            func.julianday(StayModel.end_date) - func.julianday(StayModel.start_date) + 1 >= min_days
        )

    if max_days is not None:
        query = query.where(
            func.julianday(StayModel.end_date) - func.julianday(StayModel.start_date) + 1 <= max_days
        )

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

@router.get("/by-year/{year}", response_model=list[StayRead])
def get_stays_by_year(year: int, db: Session = Depends(get_db)):
    stays = db.execute(
        select(StayModel).where(extract('year', StayModel.start_date) == year)
    ).scalars().all()

    if not stays:
        raise HTTPException(status_code=404, detail="No stays found for the given year")
    
    return stays

@router.get("/by-year-month/{year}/{month}", response_model=list[StayRead])
def get_stays_by_year_month(year: int, month: int, db: Session = Depends(get_db)):
    stays = db.execute(
        select(StayModel).where(
            extract('year', StayModel.start_date) == year,
            extract('month', StayModel.start_date) == month
        )
    ).scalars().all()

    if not stays:
        raise HTTPException(status_code=404, detail="No stays found for the given year and month")
    
    return stays

@router.get("/by-month-day/{month}/{day}", response_model=list[StayRead])
def get_stays_by_month_day(month: int, day: int, db: Session = Depends(get_db)):
    stays = db.execute(
        select(StayModel).where(
            extract('month', StayModel.start_date) == month,
            extract('day', StayModel.start_date) == day
        )
    ).scalars().all()

    if not stays:
        raise HTTPException(status_code=404, detail="No stays found for the given month and day")
    
    return stays

@router.get("/by-exact-date/{year}/{month}/{day}", response_model=list[StayRead])
def get_stays_by_exact_date(year: int, month: int, day: int, db: Session = Depends(get_db)):
    try:
        target_date = date(year, month, day)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date")

    stays = db.execute(
        select(StayModel).where(StayModel.start_date == target_date)
    ).scalars().all()

    if not stays:
        raise HTTPException(status_code=404, detail="No stays found for the given exact date")
    
    return stays

@router.post("/", response_model=StayRead) #TODO: add date validation or check if it's by default validated in pydantic model
def create_stay(stay_data: StayCreate, db: Session=Depends(get_db)):
    # Sprawdzamy, czy właściciel istnieje
    owner = db.execute(
        select(OwnerModel).where(OwnerModel.id == stay_data.owner_id)
    ).scalars().first()
    if not owner:
        raise HTTPException(status_code=400, detail="Owner does not exist")
    dog = db.execute(
        select(DogModel).where(DogModel.id == stay_data.dog_id)
    ).scalars().first()
    if not dog:
        raise HTTPException(status_code=400, detail="Dog does not exist")
    
    # sprawdzamy czy wpisywane daty nie istnieją już dla tego psa i tego właściciela, czyli czy stay to nie duplikat
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
    
    new_stay = StayModel(**stay_data.model_dump())
    db.add(new_stay)
    db.commit()
    db.refresh(new_stay)

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




