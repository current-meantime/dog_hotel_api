from app.database.database import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey
from app.models.stay import Stay as StayModel
from sqlalchemy.orm import Session

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
    
    def calculate_amount(self, db: Session) -> float:
        stay = db.get(StayModel, self.stay_id)
        if not stay:
            raise ValueError(f"Stay not found for stay_id={self.stay_id}")
        
        #TODO: Add validation for stay dates/duration in other files and remove this if it gets redundant
        stay_duration = (stay.end_date - stay.start_date).days + 1  # +1 to include the last day
        if stay_duration <= 0:
            raise ValueError("Stay duration must be greater than 0 days.")
        additional_fee = stay.additional_fee_per_day if stay.additional_fee_per_day else 0
        return stay_duration * (DAILY_RATE + additional_fee)