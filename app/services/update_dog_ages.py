import logging
from sqlalchemy.orm import Session
from app.models.dog import Dog
from datetime import datetime, timedelta, timezone
from sqlalchemy import select

logger = logging.getLogger(__name__)

def update_dog_ages(db: Session):
    try:
        logger.info("Starting dog age update process.")
        one_year_ago = datetime.now(timezone.utc) - timedelta(days=365)
        logger.info(f"Fetching dogs added before: {one_year_ago}")

        dogs_to_update = db.execute(
            select(Dog).where(Dog.created_at <= one_year_ago)
        ).scalars().all()

        logger.info(f"Found {len(dogs_to_update)} dogs to update.")

        for dog in dogs_to_update:
            dog.age += 1

        db.commit()
        logger.info("Database commit successful.")
        logger.info(f"Successfully updated ages for {len(dogs_to_update)} dogs.")

    except Exception as e:
        logger.error("Error while updating dog ages", exc_info=True)
