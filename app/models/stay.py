from __future__ import annotations
from app.database.database import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey
from datetime import date, datetime, timezone

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey
from app.models.owner import Owner

class Stay(Base):
    __tablename__ = "stays"

    id: Mapped[int] = mapped_column(primary_key=True)
    start_date: Mapped[date]
    end_date: Mapped[date]
    additional_fee_per_day: Mapped[float] = mapped_column(default=0.0)  # Dodatkowa stawka
    notes: Mapped[str] = mapped_column(nullable=True)
    created_at: Mapped[datetime] = mapped_column(default=datetime.now(timezone.utc))

    dog_id: Mapped[int] = mapped_column(ForeignKey("dogs.id"), nullable=False)
    owner_id: Mapped[int] = mapped_column(ForeignKey("owners.id"), nullable=False)

    dog = relationship("Dog", back_populates="stays")
    owner = relationship("Owner", back_populates="stays")
    payments = relationship("Payment", back_populates="stay")

