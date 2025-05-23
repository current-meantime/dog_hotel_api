from pydantic import BaseModel
from typing import Optional

class OwnerCreate(BaseModel):
    fullname: str
    email: str
    phone_number: int
    bank_account: Optional[int] = None

    class Config:
        extra = "forbid"  # Disallow extra fields

class OwnerRead(OwnerCreate):
    id: int
    
    class Config:
        from_attributes = True

class OwnerUpdate(BaseModel):
    fullname: Optional[str] = None
    email: Optional[str] = None
    phone_number: Optional[str] = None
    bank_account: Optional[int] = None
