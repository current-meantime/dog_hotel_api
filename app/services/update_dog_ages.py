import logging
import os
from sqlalchemy.orm import Session
from app.models.dog import Dog
from datetime import datetime, timedelta, timezone
from sqlalchemy import select
from sqlalchemy import func

# Tworzenie katalogu 'logs', jeśli nie istnieje
log_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'logs')
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

# Inicjalizacja logera
logger = logging.getLogger("update_logger")  # Use a specific logger name
logger.setLevel(logging.INFO)

# File handler
file_handler = logging.FileHandler(os.path.join(log_dir, 'update.log'))
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(logging.Formatter("%(asctime)s - %(message)s"))

# Console handler
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(logging.Formatter("%(asctime)s - %(message)s"))

# Add handlers to the logger
if not logger.handlers:  # Avoid adding handlers multiple times
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

def update_dog_ages(db: Session):
    try:
        logger.info("Starting dog age update process.")
        one_year_ago = datetime.now(timezone.utc) - timedelta(days=365)
        logger.info(f"Fetching dogs added before: {one_year_ago}")

        dogs_to_update = db.execute(
            select(Dog).where(Dog.created_at <= one_year_ago)
        ).scalars().all()

        logger.info(f"Found {len(dogs_to_update)} dogs to update.")

        if dogs_to_update:
            for dog in dogs_to_update:
                dog.age += 1

            db.commit()
            logger.info("Database commit successful.")
            logger.info(f"Successfully updated ages for {len(dogs_to_update)} dogs.")

    except Exception as e:
        logger.error(f"Error while updating dog ages: {str(e)}")
