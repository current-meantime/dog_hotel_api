from app.database.database import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship


class Owner(Base):
    __tablename__ = "owners"

    id: Mapped[int] = mapped_column(primary_key=True)
    fullname: Mapped[str]
    email: Mapped[str]
    phone_number: Mapped[int]
    bank_account: Mapped[int] = mapped_column(nullable=True)

    dogs = relationship("Dog", back_populates="owner")
    stays = relationship("Stay", back_populates="owner", foreign_keys="Stay.owner_id")
    
    