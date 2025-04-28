from pydantic import BaseModel
from typing import Optional, List
from datetime import date, datetime


class StayCreate(BaseModel):
    start_date: date
    end_date: date
    notes: Optional[str]
    additional_fee_per_day: Optional[float]
    owner_id: int
    dog_id: int
    
    class Config:
        from_attributes = True  # Enable ORM mode to read data from ORM models
    
class StayRead(StayCreate):
    id: int
    created_at: datetime  #TODO: fix this - skoro w dog to nie musi być Optional, czemu brak Optional daje mi error?!
    
class StayUpdate(BaseModel):
    start_date: Optional[date]
    end_date: Optional[date]
    notes: Optional[str]
    additional_fee_per_day: Optional[float]
    
    class Config:
        from_attributes = True  # Enable ORM mode to read data from ORM models
    