from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.models.owner import Owner as OwnerModel
from app.models.payment import Payment as PaymentModel
from app.models.stay import Stay as StayModel
from app.schemas.owner import OwnerRead, OwnerCreate, OwnerUpdate
from app.database.database import get_db
from typing import Optional
import logging

router = APIRouter(prefix="/owners", tags=["Owners"])
log = logging.getLogger(__name__)

@router.get("/", response_model=list[OwnerRead])
def search_owners(
    fullname: Optional[str] = None,
    email: Optional[str] = None,
    phone_number: Optional[int] = None,
    unpaid: Optional[bool] = None,
    overdue: Optional[bool] = None,
    bank_account: Optional[int] = None,
    db: Session = Depends(get_db)
):
    log.info(
        f"Searching owners with filters: fullname={fullname}, email={email}, "
        f"phone_number={phone_number}, unpaid={unpaid}, overdue={overdue}, "
        f"bank_account={bank_account}"
    )
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
            
    if bank_account:
        stmt = stmt.where(OwnerModel.bank_account == bank_account)

    owners = db.execute(stmt).scalars().all()

    return owners

@router.get("/{owner_id}", response_model=OwnerRead)
def get_owner_by_id(owner_id, db: Session=Depends(get_db)):
    log.info(f"Fetching owner with id: {owner_id}")
    existing_owner = db.execute(
        select(OwnerModel).where(OwnerModel.id == owner_id)
    ).scalars().first()

    if not existing_owner:
        log.warning(f"Owner with id {owner_id} not found")
        raise HTTPException(status_code=404, detail="Owner not found")
    
    return existing_owner


@router.put("/{owner_id}", response_model=OwnerRead)
def update_owner(owner_id: int, update_data: OwnerUpdate, db: Session = Depends(get_db)):
    log.info(f"Updating owner {owner_id}")
    
    existing_owner = db.execute(
        select(OwnerModel).where(OwnerModel.id == owner_id)
    ).scalars().first()

    if not existing_owner:
        log.warning(f"Owner {owner_id} not found for update")
        raise HTTPException(status_code=400, detail="Owner doesn't exist")

    if update_data.email:
        log.debug(f"Checking if email {update_data.email} is available")
        existing_email = db.execute(
            select(OwnerModel).where(OwnerModel.email == update_data.email).where(OwnerModel.id != owner_id)
        ).scalars().first()

        if existing_email:
            log.warning(f"Email {update_data.email} already in use by another owner")
            raise HTTPException(status_code=400, detail="Owner with this email already exists")

    if update_data.phone_number:
        log.debug(f"Checking if phone number {update_data.phone_number} is available")
        existing_phone_number = db.execute(
            select(OwnerModel).where(OwnerModel.phone_number == update_data.phone_number).where(OwnerModel.id != owner_id)
        ).scalars().first()

        if existing_phone_number:
            log.warning(f"Phone number {update_data.phone_number} already in use by another owner")
            raise HTTPException(status_code=400, detail="Owner with this phone number already exists")

    try:
        for key, value in update_data.model_dump(exclude_unset=True).items():
            setattr(existing_owner, key, value)

        db.commit()
        db.refresh(existing_owner)
        log.info(f"Successfully updated owner {owner_id}")
        return existing_owner
    except Exception as e:
        log.error(f"Error updating owner {owner_id}: {str(e)}", exc_info=True)
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to update owner")

@router.post("/", response_model=OwnerRead)
def create_owner(owner_data: OwnerCreate, db: Session=Depends(get_db)):
    log.info(f"Creating new owner with email: {owner_data.email}")
    
    existing_email = db.execute(
        select(OwnerModel).where(OwnerModel.email == owner_data.email)
    ).scalars().first()

    if existing_email:
        log.warning(f"Owner with email {owner_data.email} already exists")
        raise HTTPException(status_code=400, detail="Owner with this email already exists")
    
    existing_phone_number = db.execute(
        select(OwnerModel).where(OwnerModel.phone_number == owner_data.phone_number)
    ).scalars().first()

    if existing_phone_number:
        log.warning(f"Owner with phone number {owner_data.phone_number} already exists")
        raise HTTPException(status_code=400, detail="Owner with this phone_number already exists")
    
    try:
        new_owner = OwnerModel(**owner_data.model_dump())
        db.add(new_owner)
        db.commit()
        db.refresh(new_owner)
        log.info(f"Successfully created owner {new_owner.id}")
        return new_owner
    except Exception as e:
        log.error(f"Error creating owner: {str(e)}", exc_info=True)
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to create owner")

@router.delete("/{owner_id}", response_model=OwnerRead)
def delete_owner(owner_id, db: Session=Depends(get_db)):
    log.info(f"Attempting to delete owner {owner_id}")
    
    existing_owner = db.execute(
        select(OwnerModel).where(OwnerModel.id == owner_id)
    ).scalars().first()

    if not existing_owner:
        log.warning(f"Owner {owner_id} not found for deletion")
        raise HTTPException(status_code=400, detail="Owner does not exist")
    
    try:
        db.delete(existing_owner)
        db.commit()
        log.info(f"Successfully deleted owner {owner_id}")
        return existing_owner
    except Exception as e:
        log.error(f"Error deleting owner {owner_id}: {str(e)}", exc_info=True)
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to delete owner")