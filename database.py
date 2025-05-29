# greengrow_manager/database.py

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os

DATABASE_FILE = "store.db"
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE_PATH = os.path.join(BASE_DIR, DATABASE_FILE)

engine = create_engine(f"sqlite:///{DATABASE_PATH}", echo=False)

Base = declarative_base()

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    """Dependency to get a database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_all_tables():
    """Creates all tables defined in models.py."""
    print(f"Attempting to create tables in {DATABASE_PATH}...")
    Base.metadata.create_all(bind=engine)
    print("Tables created (if they didn't exist).")

if __name__ == "__main__":
    create_all_tables()