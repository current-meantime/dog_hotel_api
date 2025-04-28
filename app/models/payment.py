from app.database.database import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey


DAILY_RATE = 50.0  # Stawka za dzień pobytu

class Payment(Base):
    __tablename__ = "payments"

    id: Mapped[int] = mapped_column(primary_key=True)
    amount: Mapped[float] # zrobić tak, by wyliczało to pole na podstawie długości pobytu i stawki + ewentualna dodatkowa stawka za dzień przy specjalnych wymaganiach do opieki nad psem
    is_paid: Mapped[bool]
    overdue_30_days: Mapped[int] = mapped_column(default=0)  #TODO: zmienić na bool, albo zmienić na liczbę overdue dni i info o przekroczeniu 30 dni pokawać przez logi?

    stay_id: Mapped[int] = mapped_column(ForeignKey("stays.id"), nullable=False)
    stay = relationship("Stay", back_populates="payments")
    
    def calculate_amount(self):
        stay_duration = (self.stay.end_date - self.stay.start_date).days
        additional_fee = self.stay.additional_fee_per_day * stay_duration
        base_fee = DAILY_RATE * stay_duration
        total_amount = base_fee + additional_fee
        return total_amount