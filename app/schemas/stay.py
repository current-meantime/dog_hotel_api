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
    
    @field_validator("end_date")
    @classmethod
    def validate_date_range(cls, end_date, values):
        # Tylko jeśli start_date i end_date są obecne w danych
        start_date = values.get("start_date")
        if start_date and end_date and end_date < start_date:
            raise ValueError("End date cannot be earlier than start date.")
        return end_date
    
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
    
    @field_validator("end_date")
    @classmethod
    def validate_date_range(cls, end_date, values):
        # Tylko jeśli start_date i end_date są obecne w danych
        start_date = values.get("start_date")
        if start_date and end_date and end_date < start_date:
            raise ValueError("End date cannot be earlier than start date.")
        return end_date
    