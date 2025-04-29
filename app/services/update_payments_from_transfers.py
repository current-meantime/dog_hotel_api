import logging
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.models.payment import Payment
from app.models.bank_transfer import BankTransfer

logger = logging.getLogger(__name__)

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
                    today = datetime.now(timezone.utc).date()
                    overdue_days = (today - payment.stay.end_date).days
                    payment.overdue_days = max(0, overdue_days)

                    logger.info(
                        f"Partial payment for stay_id {stay_id}: received {received_amount}, required {required_amount}. Overdue days: {payment.overdue_days}"
                    )

                updated_count += 1

            except Exception as e:
                logger.error(f"Failed to process transfer {transfer.id}", exc_info=True)

        db.commit()
        logger.info(f"Finished updating payments. Total updated: {updated_count}")

    except Exception as e:
        logger.error("Error while updating payments from transfers", exc_info=True)
