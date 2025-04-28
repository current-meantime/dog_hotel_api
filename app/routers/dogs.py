from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.models.dog import Dog as DogModel
from app.models.owner import Owner as OwnerModel
from app.schemas.dog import DogRead, DogCreate, DogUpdate
from app.database.database import get_db

router = APIRouter(prefix="/dogs", tags=["Dogs"])

@router.get("/", response_model=list[DogRead])
def read_dogs(db: Session=Depends(get_db)):
    owners = db.execute(
        select(DogModel)
    ).scalars().all()

    return owners

@router.get("/{dog_id}", response_model=DogRead)
def get_dog(dog_id, db: Session=Depends(get_db)):
    existing_dog = db.execute(
        select(DogModel).where(DogModel.id == dog_id)
    ).scalars().first()

    if not existing_dog:
        raise HTTPException(status_code=404, detail="Dog not found")
    
    return existing_dog

@router.get("/owner/{owner_id}", response_model=list[DogRead])
def get_dogs_by_owner(owner_id: int, db: Session=Depends(get_db)):
    owner = db.execute(
        select(OwnerModel).where(OwnerModel.id == owner_id)
    ).scalars().first()
    if not owner:
        raise HTTPException(status_code=404, detail="Owner not found")
    
    dogs = db.execute(
        select(DogModel).where(DogModel.owner_id == owner_id)
    ).scalars().all()

    if not dogs:
        raise HTTPException(status_code=404, detail="No dogs found for this owner")
    
    return dogs

@router.get("/name/{dog_name}", response_model=list[DogRead])
def get_dogs_by_name(dog_name: str, db: Session=Depends(get_db)):
    dogs = db.execute(
        select(DogModel).where(DogModel.name == dog_name)
    ).scalars().all()

    if not dogs:
        raise HTTPException(status_code=404, detail="No dogs found with this name")
    
    return dogs

@router.get("/medicated", response_model=list[DogRead])
def get_medicated_dogs(db: Session=Depends(get_db)):
    dogs = db.execute(
        select(DogModel).where(DogModel.medicine != None) #TODO: NIE DZIAŁA
    ).scalars().all()
    return dogs

@router.get("/food/standard", response_model=list[DogRead])
def get_standard_food_dogs(db: Session=Depends(get_db)):
    dogs = db.execute(
        select(DogModel).where(DogModel.food == "standard")
    ).scalars().all()
    return dogs

@router.get("/food/non-standard", response_model=list[DogRead])
def get_non_standard_food_dogs(db: Session=Depends(get_db)):
    dogs = db.execute(
        select(DogModel).where(DogModel.food != "standard")
    ).scalars().all()
    return dogs

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