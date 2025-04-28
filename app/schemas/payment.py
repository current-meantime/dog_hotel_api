from pydantic import BaseModel
from typing import Optional

class PaymentCreate(BaseModel):
    stay_id: int
    is_paid: Optional[bool] = False
    overdue_30_days: Optional[int] = 0

    class Config:
        from_attributes = True  # Zezwala na korzystanie z ORM

class PaymentRead(PaymentCreate):
    id: int
    amount: float

class PaymentUpdate(BaseModel):
    is_paid: Optional[bool] = None
    overdue_30_days: Optional[int] = None

    class Config:
        from_attributes = True  # Zezwala na korzystanie z ORM