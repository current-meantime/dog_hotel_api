import logging
import os
from datetime import datetime, timezone

from sqlalchemy.orm import Session
from sqlalchemy import select

from app.models.payment import Payment
from app.models.bank_transfer import BankTransfer
from app.models.stay import Stay

# Tworzenie katalogu 'logs', jeśli nie istnieje
log_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'logs')
os.makedirs(log_dir, exist_ok=True)

# Logger
logger = logging.getLogger("payment_update_logger")
logger.setLevel(logging.INFO)

# File handler
file_handler = logging.FileHandler(os.path.join(log_dir, 'payment_update.log'))
file_handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))

# Console handler
console_handler = logging.StreamHandler()
console_handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))

# Add handlers if not already added
if not logger.handlers:
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)


def update_payments_from_transfers(db: Session):
    logger.info("Starting payment update from bank transfers")

    try:
        transfers = db.execute(select(BankTransfer)).scalars().all()
        logger.info(f"Found {len(transfers)} bank transfers")

        updated_count = 0

        for transfer in transfers:
            try:
                stay_id = int(transfer.transfer_title.strip())
                payment = db.execute(
                    select(Payment).where(Payment.stay_id == stay_id)
                ).scalars().first()

                if not payment:
                    logger.warning(f"No payment found for stay_id: {stay_id}")
                    continue

                required_amount = payment.calculate_amount()
                received_amount = transfer.amount

                if received_amount >= required_amount:
                    payment.amount = required_amount
                    payment.is_paid = True
                    payment.is_overdue = False
                    payment.overdue_days = 0
                    logger.info(f"Marked payment for stay_id {stay_id} as fully paid")
                else:
                    payment.amount = received_amount
                    payment.is_paid = False
                    payment.is_overdue = True

                    # Licz dni od zakończenia pobytu
                    today = datetime.now(timezone.utc).date()
                    overdue_days = (today - payment.stay.end_date).days
                    payment.overdue_days = max(0, overdue_days)

                    logger.info(
                        f"Partial payment for stay_id {stay_id}: received {received_amount}, required {required_amount}. Overdue days set to {payment.overdue_days}"
                    )

                updated_count += 1

            except Exception as e:
                logger.error(f"Failed to process transfer {transfer.id}: {e}")

        db.commit()
        logger.info(f"Finished updating payments. Total updated: {updated_count}")

    except Exception as e:
        logger.error(f"Error while updating payments from transfers: {e}")
