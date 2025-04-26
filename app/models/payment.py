from app.database.database import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey

class Payment(Base):
    __tablename__ = "payments"

    id: Mapped[int] = mapped_column(primary_key=True)
    amount: Mapped[float]
    is_paid: Mapped[bool]
    overdue_30_days: Mapped[int]

    stay_id: Mapped[int] = mapped_column(ForeignKey("stays.id"), nullable=False)

    stay = relationship("Stay", back_populates="payments")