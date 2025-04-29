from pydantic import BaseModel, field_validator
from typing import Optional, List
from datetime import date, datetime


class StayCreate(BaseModel):
    start_date: date
    end_date: date
    notes: Optional[str] = None
    additional_fee_per_day: Optional[float] = None
    owner_id: int
    dog_id: int
    
    class Config:
        extra = "forbid" # Disallow extra fields
        
class StayRead(StayCreate):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True  # Enable ORM mode to read data from ORM models
    
class StayUpdate(BaseModel):
    start_date: Optional[date]
    end_date: Optional[date]
    notes: Optional[str]
    additional_fee_per_day: Optional[float]
    

    