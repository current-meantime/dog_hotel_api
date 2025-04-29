from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.models.dog import Dog as DogModel
from app.models.owner import Owner as OwnerModel
from app.schemas.dog import DogRead, DogCreate, DogUpdate
from app.database.database import get_db
from typing import Optional
import logging

router = APIRouter(prefix="/dogs", tags=["Dogs"])
log = logging.getLogger(__name__)

@router.get("/", response_model=list[DogRead])
def search_dogs(
    owner_id: Optional[int] = None,
    name: Optional[str] = None,
    medicated: Optional[bool] = None,
    special_food: Optional[bool] = None,  # "standard" lub "non-standard"
    notes: Optional[bool] = None,
    db: Session = Depends(get_db),
):
    log.info(
        f"Searching dogs with filters: owner_id={owner_id}, name={name}, "
        f"medicated={medicated}, special_food={special_food}, notes={notes}"
    )
    
    query = select(DogModel)

    if owner_id is not None:
        owner = db.execute(select(OwnerModel).where(OwnerModel.id == owner_id)).scalars().first()
        if not owner:
            log.warning(f"Owner with id {owner_id} not found during dog search")
            raise HTTPException(status_code=404, detail="Owner not found")
        query = query.where(DogModel.owner_id == owner_id)

    if name is not None:
        query = query.where(DogModel.name == name)

    if medicated is not None:
        if medicated:
            query = query.where(DogModel.medicine.isnot(None))
        else:
            query = query.where(DogModel.medicine.is_(None))

    if special_food is not None:
        if special_food is True:
            query = query.where(DogModel.food != "standard")
        else:
            query = query.where(DogModel.food == "standard")
        
    if notes is True:
        query = query.where(DogModel.notes.isnot(None)).where(DogModel.notes != "")
    elif notes is False:
        query = query.where((DogModel.notes.is_(None)) | (DogModel.notes == ""))
        
    dogs = db.execute(query).scalars().all()
    return dogs

@router.get("/{dog_id}", response_model=DogRead)
def get_dog(dog_id, db: Session=Depends(get_db)):
    log.info(f"Fetching dog with id: {dog_id}")
    
    existing_dog = db.execute(
        select(DogModel).where(DogModel.id == dog_id)
    ).scalars().first()

    if not existing_dog:
        log.warning(f"Dog with id {dog_id} not found")
        raise HTTPException(status_code=404, detail="Dog not found")
    
    log.debug(f"Successfully retrieved dog {dog_id}")
    return existing_dog

@router.post("/", response_model=DogRead)
def create_dog(dog_data: DogCreate, db: Session=Depends(get_db)):
    log.info(f"Creating new dog with name: {dog_data.name} for owner_id: {dog_data.owner_id}")
    
    owner = db.execute(
        select(OwnerModel).where(OwnerModel.id == dog_data.owner_id)
    ).scalars().first()
    
    if not owner:
        log.error(f"Owner with id {dog_data.owner_id} not found")
        raise HTTPException(status_code=400, detail="Owner does not exist")
    
    dog_name = db.execute(
        select(DogModel).where(DogModel.name == dog_data.name, DogModel.owner_id == dog_data.owner_id)
    ).scalars().first()
    
    if dog_name:
        log.warning(f"Dog with name {dog_data.name} already exists for owner {dog_data.owner_id}")
        raise HTTPException(status_code=400, detail="Dog with this name already exists for this owner")
    
    try:
        new_dog = DogModel(**dog_data.model_dump())
        db.add(new_dog)
        db.commit()
        db.refresh(new_dog)
        log.info(f"Successfully created dog {new_dog.id}")
        return new_dog
    except Exception as e:
        log.error(f"Error creating dog: {str(e)}", exc_info=True)
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to create dog")

@router.put("/{dog_id}", response_model=DogRead)
def update_dog(dog_id: int, update_data: DogUpdate, db: Session = Depends(get_db)):
    log.info(f"Updating dog {dog_id}")
    
    existing_dog = db.execute(
        select(DogModel).where(DogModel.id == dog_id)
    ).scalars().first()

    if not existing_dog:
        log.warning(f"Dog {dog_id} not found for update")
        raise HTTPException(status_code=400, detail="Dog does not exist")

    try:
        for key, value in update_data.model_dump(exclude_unset=True).items():
            setattr(existing_dog, key, value)

        db.commit()
        db.refresh(existing_dog)
        log.info(f"Successfully updated dog {dog_id}")
        return existing_dog
    except Exception as e:
        log.error(f"Error updating dog {dog_id}: {str(e)}", exc_info=True)
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to update dog")

@router.delete("/{dog_id}", response_model=DogRead)
def delete_dog(dog_id, db: Session=Depends(get_db)):
    log.info(f"Attempting to delete dog {dog_id}")
    
    existing_dog = db.execute(
        select(DogModel).where(DogModel.id == dog_id)
    ).scalars().first()

    if not existing_dog:
        log.warning(f"Dog {dog_id} not found for deletion")
        raise HTTPException(status_code=400, detail="Dog does not exist")
    
    try:
        db.delete(existing_dog)
        db.commit()
        log.info(f"Successfully deleted dog {dog_id}")
        return existing_dog
    except Exception as e:
        log.error(f"Error deleting dog {dog_id}: {str(e)}", exc_info=True)
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to delete dog")