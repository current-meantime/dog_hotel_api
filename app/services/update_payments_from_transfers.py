from sqlalchemy.orm import Session
from sqlalchemy import select
from app.models.bank_transfer import BankTransfer
from app.models.payment import Payment
from app.models.stay import Stay
from app.models.owner import Owner
import re

def parse_stay_id_from_title(title: str) -> int | None:
    match = re.search(r"stay[ _-]?(\d+)", title.lower())
    return int(match.group(1)) if match else None

def process_bank_transfers(db: Session):
    unmatched_transfers = db.execute(
        select(BankTransfer).where(BankTransfer.matched_payment_id.is_(None))
    ).scalars().all()

    for transfer in unmatched_transfers:
        stay_id = parse_stay_id_from_title(transfer.title)
        if not stay_id:
            continue

        stay = db.execute(select(Stay).where(Stay.id == stay_id)).scalars().first()
        if not stay:
            continue

        owner = stay.owner
        if owner and owner.bank_account == transfer.from_account:
            payment = db.execute(
                select(Payment).where(Payment.stay_id == stay.id)
            ).scalars().first()

            if payment:
                payment.amount -= transfer.amount  # Zakładamy, że nadpłaty nie istnieją
                if payment.amount <= 0:
                    payment.amount = 0
                    payment.is_paid = True
                    payment.is_overdue = False
                    payment.overdue_days = 0

                transfer.matched_payment_id = payment.id
                db.add_all([transfer, payment])
    
    db.commit()