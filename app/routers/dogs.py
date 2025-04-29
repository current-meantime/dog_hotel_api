from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.models.dog import Dog as DogModel
from app.models.owner import Owner as OwnerModel
from app.schemas.dog import DogRead, DogCreate, DogUpdate
from app.database.database import get_db
from typing import Optional

router = APIRouter(prefix="/dogs", tags=["Dogs"])

@router.get("/", response_model=list[DogRead])
def search_dogs(
    owner_id: Optional[int] = None,
    name: Optional[str] = None,
    medicated: Optional[bool] = None,
    food_type: Optional[str] = None,  # "standard" lub "non-standard"
    notes: Optional[bool] = None,
    db: Session = Depends(get_db),
):
    query = select(DogModel)

    if owner_id is not None:
        owner = db.execute(select(OwnerModel).where(OwnerModel.id == owner_id)).scalars().first()
        if not owner:
            raise HTTPException(status_code=404, detail="Owner not found")
        query = query.where(DogModel.owner_id == owner_id)

    if name is not None:
        query = query.where(DogModel.name == name)

    if medicated is not None:
        if medicated:
            query = query.where(DogModel.medicine.isnot(None))
        else:
            query = query.where(DogModel.medicine.is_(None))

    if food_type is not None:
        if food_type == "standard":
            query = query.where(DogModel.food == "standard")
        elif food_type == "non-standard":
            query = query.where(DogModel.food != "standard")
        else:
            raise HTTPException(status_code=400, detail="Invalid food_type value (must be 'standard' or 'non-standard')")
        
    if notes is True:
        query = query.where(DogModel.notes.isnot(None)).where(DogModel.notes != "")
    elif notes is False:
        query = query.where((DogModel.notes.is_(None)) | (DogModel.notes == ""))
        
    dogs = db.execute(query).scalars().all()
    return dogs

@router.get("/{dog_id}", response_model=DogRead)
def get_dog(dog_id, db: Session=Depends(get_db)):
    existing_dog = db.execute(
        select(DogModel).where(DogModel.id == dog_id)
    ).scalars().first()

    if not existing_dog:
        raise HTTPException(status_code=404, detail="Dog not found")
    
    return existing_dog

@router.post("/", response_model=DogRead)
def create_dog(dog_data: DogCreate, db: Session=Depends(get_db)):
    
    owner = db.execute(
        select(OwnerModel).where(OwnerModel.id == dog_data.owner_id)
    ).scalars().first()
    
    if not owner:
        raise HTTPException(status_code=400, detail="Owner does not exist")
    
    dog_name = db.execute(
        select(DogModel).where(DogModel.name == dog_data.name, DogModel.owner_id == dog_data.owner_id)
    ).scalars().first()
    
    if dog_name:
        raise HTTPException(status_code=400, detail="Dog with this name already exists for this owner")
    
    new_dog = DogModel(**dog_data.model_dump())
    db.add(new_dog)
    db.commit()
    db.refresh(new_dog)

    return new_dog

@router.put("/{dog_id}", response_model=DogRead)
def update_dog(dog_id: int, update_data: DogUpdate, db: Session = Depends(get_db)):
    existing_dog = db.execute(
        select(DogModel).where(DogModel.id == dog_id)
    ).scalars().first()

    if not existing_dog:
        raise HTTPException(status_code=400, detail="Dog does not exist")

    # Aktualizujemy dane psa
    for key, value in update_data.model_dump(exclude_unset=True).items():  # Używamy exclude_unset, by ignorować puste dane
        setattr(existing_dog, key, value)

    db.commit()
    db.refresh(existing_dog)

    return existing_dog


@router.delete("/{dog_id}", response_model=DogRead)
def delete_dog(dog_id, db: Session=Depends(get_db)):
    existing_dog = db.execute(
        select(DogModel).where(DogModel.id == dog_id)
    ).scalars().first()

    if not existing_dog:
        raise HTTPException(status_code=400, detail="Dog does not exist")
    
    db.delete(existing_dog)
    db.commit()

    return existing_dog