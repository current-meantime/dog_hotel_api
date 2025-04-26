from app.database.database import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey
from datetime import datetime

class Dog(Base):
    __tablename__ = "dogs"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    age: Mapped[int]
    medicine: Mapped[str] = mapped_column(nullable=True)
    food: Mapped[str] = mapped_column(default="standard")
    notes: Mapped[str] = mapped_column(nullable=True)

    owner_id: Mapped[int] = mapped_column(ForeignKey("owners.id"), nullable=False)

    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)  # Dodajemy datę utworzenia psa

    owner = relationship("Owner", back_populates="dogs")