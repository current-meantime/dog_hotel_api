from pydantic import BaseModel
from typing import Optional

class PaymentCreate(BaseModel):
    stay_id: int
    is_paid: Optional[bool] = False
    is_overdue: Optional[bool] = False
    overdue_days: Optional[int] = 0

    class Config:
        extra = "forbid"

class PaymentRead(PaymentCreate):
    id: int
    amount: float
    
    class Config:
        from_attributes = True  # Zezwala na korzystanie z ORM

class PaymentUpdate(BaseModel):
    is_paid: Optional[bool] = None
    is_overdue: Optional[bool] = False
    overdue_days: Optional[int] = 0
