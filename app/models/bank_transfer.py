from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime, timezone
from app.database.database import Base

class BankTransfer(Base):
    __tablename__ = "bank_transfers"

    id: Mapped[int] = mapped_column(primary_key=True)
    from_account: Mapped[str] = mapped_column(String, nullable=False)
    sender_name: Mapped[str] = mapped_column(String, nullable=False)
    title: Mapped[str] = mapped_column(String, nullable=False)
    amount: Mapped[float] = mapped_column(nullable=False)
    received_at: Mapped[datetime] = mapped_column(default=datetime.now(timezone.utc))

    matched_payment_id: Mapped[int | None] = mapped_column(ForeignKey("payments.id"), nullable=True)
    matched_payment = relationship("Payment", backref="matched_transfers")
