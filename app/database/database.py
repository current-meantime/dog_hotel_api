from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from dotenv import load_dotenv
import os

load_dotenv()  # Załadowanie zmiennych środowiskowych z pliku .env

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///dog_hotel.db")  # domyślnie SQLite, jeśli nie podano w .env

engine = create_engine(DATABASE_URL)

Session = sessionmaker(bind=engine)

class Base(DeclarativeBase):
    pass

def get_db():
    db = Session()
    try:
        yield db
    finally:
        db