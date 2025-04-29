from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class BankTransferCreate(BaseModel):
    from_account: str
    sender_name: str
    title: str
    amount: float
    received_at: Optional[datetime] = None
    
    class Config:
        extra = "forbid"  # Disallow extra fields

class BankTransferRead(BankTransferCreate):
    id: int
    matched_payment_id: Optional[int]
    
    class Config:
        from_attributes = True
        
class BankTransferUpdate(BaseModel):
    from_account: Optional[str] = None
    sender_name: Optional[str] = None
    title: Optional[str] = None
    amount: Optional[float] = None
    received_at: Optional[datetime] = None
    matched_payment_id: Optional[int] = None
