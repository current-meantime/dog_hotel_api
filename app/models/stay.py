from __future__ import annotations
from app.database.database import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey

class Stay(Base):
    __tablename__ = "stays"

    id: Mapped[int] = mapped_column(primary_key=True)
    start_date: Mapped[str]
    end_date: Mapped[str]

    owner_id: Mapped[int] = mapped_column(ForeignKey("owners.id"), nullable=False)

    owner = relationship("Owner", back_populates="stays")