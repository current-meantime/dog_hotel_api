from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.models.owner import Owner as OwnerModel
from app.models.payment import Payment as PaymentModel
from app.models.stay import Stay as StayModel
from app.schemas.owner import OwnerRead, OwnerCreate, OwnerUpdate
from app.database.database import get_db
from typing import Optional

router = APIRouter(prefix="/owners", tags=["Owners"])

@router.get("/filter", response_model=list[OwnerRead])
def filter_owners(
    fullname: Optional[str] = None,
    email: Optional[str] = None,
    phone_number: Optional[int] = None,
    unpaid: Optional[bool] = None,
    overdue: Optional[bool] = None,
    db: Session = Depends(get_db)
):
    stmt = select(OwnerModel)

    if fullname:
        stmt = stmt.where(OwnerModel.fullname.ilike(fullname.strip().lower())) #TODO: spr czy w dog router też jest ilike
        
    if email:
        stmt = stmt.where(OwnerModel.email.ilike(email.strip().lower()))
        
    if phone_number:
        stmt = stmt.where(OwnerModel.phone_number == phone_number)

    if unpaid or overdue:
        stmt = stmt.join(StayModel, StayModel.owner_id == OwnerModel.id).join(
            PaymentModel, PaymentModel.stay_id == StayModel.id
        )
        if unpaid:
            stmt = stmt.where(PaymentModel.is_paid == False)
        if overdue:
            stmt = stmt.where(PaymentModel.is_overdue > 0)

    owners = db.execute(stmt).scalars().all()

    if not owners:
        raise HTTPException(status_code=404, detail="No owners matched the given filters")

    return owners

@router.get("/{owner_id}", response_model=OwnerRead)
def get_owner_by_id(owner_id, db: Session=Depends(get_db)):
    existing_owner = db.execute(
        select(OwnerModel).where(OwnerModel.id == owner_id)
    ).scalars().first()

    if not existing_owner:
        raise HTTPException(status_code=404, detail="Owner not found")
    
    return existing_owner


@router.put("/{owner_id}", response_model=OwnerRead)
def update_owner(owner_id: int, update_data: OwnerUpdate, db: Session = Depends(get_db)):
    # Znajdujemy istniejącego właściciela
    existing_owner = db.execute(
        select(OwnerModel).where(OwnerModel.id == owner_id)
    ).scalars().first()

    if not existing_owner:
        raise HTTPException(status_code=400, detail="Owner doesn't exist")

    # Sprawdzamy, czy email nie jest już zajęty przez innego właściciela
    if update_data.email:
        existing_email = db.execute(
            select(OwnerModel).where(OwnerModel.email == update_data.email).where(OwnerModel.id != owner_id)
        ).scalars().first()

        if existing_email:
            raise HTTPException(status_code=400, detail="Owner with this email already exists")

    # Sprawdzamy, czy numer telefonu nie jest już zajęty przez innego właściciela
    if update_data.phone_number:  # Dodajemy sprawdzenie numeru telefonu tylko jeśli jest podany
        existing_phone_number = db.execute(
            select(OwnerModel).where(OwnerModel.phone_number == update_data.phone_number).where(OwnerModel.id != owner_id)
        ).scalars().first()

        if existing_phone_number:
            raise HTTPException(status_code=400, detail="Owner with this phone number already exists")

    # Aktualizujemy dane właściciela
    for key, value in update_data.model_dump(exclude_unset=True).items():  # Używamy exclude_unset, by ignorować puste dane
        setattr(existing_owner, key, value)

    db.commit()
    db.refresh(existing_owner)

    return existing_owner

@router.post("/", response_model=OwnerRead)
def create_owner(owner_data: OwnerCreate, db: Session=Depends(get_db)):
    existing_email = db.execute(
        select(OwnerModel).where(OwnerModel.email == owner_data.email)
    ).scalars().first()

    if existing_email:
        raise HTTPException(status_code=400, detail="Owner with this email already exists")
    
    existing_phone_number = db.execute(
        select(OwnerModel).where(OwnerModel.email == owner_data.email)
    ).scalars().first()

    if existing_phone_number:
        raise HTTPException(status_code=400, detail="Owner with this phone_number already exists")
    
    new_owner = OwnerModel(**owner_data.model_dump())
    db.add(new_owner)
    db.commit()
    db.refresh(new_owner)

    return new_owner

@router.delete("/{owner_id}", response_model=OwnerRead)
def delete_owner(owner_id, db: Session=Depends(get_db)):
    existing_owner = db.execute(
        select(OwnerModel).where(OwnerModel.id == owner_id)
    ).scalars().first()

    if not existing_owner:
        raise HTTPException(status_code=400, detail="Owner does not exist")
    
    db.delete(existing_owner)
    db.commit()

    return existing_owner