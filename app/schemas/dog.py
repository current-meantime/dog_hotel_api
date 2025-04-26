from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class DogCreate(BaseModel):
    name: str
    age: int
    medicine: Optional[str] = None
    food: Optional[str] = "standard"
    notes: Optional[str] = None
    owner_id: int

    class Config:
        from_attributes = True

class DogRead(DogCreate):
    id: int
    created_at: datetime

class DogUpdate(BaseModel):
    name: Optional[str] = None
    age: Optional[int] = None
    medicine: Optional[str] = None
    food: Optional[str] = None
    notes: Optional[str] = None
    owner_id: Optional[int] = None

    class Config:
        from_attributes = True