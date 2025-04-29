from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class BankTransferCreate(BaseModel):
    from_account: str
    sender_name: str
    title: str
    amount: float
    received_at: Optional[datetime] = None

class BankTransferRead(BankTransferCreate):
    id: int
    matched_payment_id: Optional[int]
    
    class Config:
        from_attributes = True
