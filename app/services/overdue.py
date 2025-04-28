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
    
#TODO: wyliczać overdue i informować kiedy jest ponad 30 dni
    
