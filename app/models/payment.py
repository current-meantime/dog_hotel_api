from app.database.database import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey


DAILY_RATE = 50.0  # Stawka za dzień pobytu

class Payment(Base):
    __tablename__ = "payments"

    id: Mapped[int] = mapped_column(primary_key=True)
    amount: Mapped[float]
    is_paid: Mapped[bool] = mapped_column(default=False)  
    is_overdue: Mapped[bool] = mapped_column(default=False)  
    overdue_days: Mapped[int] = mapped_column(default=0)  

    stay_id: Mapped[int] = mapped_column(ForeignKey("stays.id"), nullable=False)
    stay = relationship("Stay", back_populates="payments")
    
    def calculate_amount(self):
        stay_duration = (self.stay.end_date - self.stay.start_date).days
        additional_fee = self.stay.additional_fee_per_day * stay_duration
        base_fee = DAILY_RATE * stay_duration
        total_amount = base_fee + additional_fee
        return total_amount