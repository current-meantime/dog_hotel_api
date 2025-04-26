from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.models.dog import Dog as DogModel
from app.schemas.dog import DogRead, DogCreate, DogUpdate
from app.database.database import get_db

router = APIRouter(prefix="/dogs", tags=["Dogs"])

@router.get("/", response_model=list[DogRead])
def read_dogs(db: Session=Depends(get_db)):
    owners = db.execute(
        select(DogModel)
    ).scalars().all()

    return owners

@router.get("/{owner_id}", response_model=DogRead)
def get_dog(owner_id, db: Session=Depends(get_db)):
    existing_dog = db.execute(
        select(DogModel).where(DogModel.id == owner_id)
    ).scalars().first()

    if not existing_dog:
        raise HTTPException(status_code=404, detail="Dog not found")
    
    return existing_dog

@router.post("/", response_model=DogRead)
def create_dog(dog_data: DogCreate, db: Session=Depends(get_db)):
    
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