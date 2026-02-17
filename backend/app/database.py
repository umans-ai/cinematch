import os
from pathlib import Path
from sqlalchemy import create_engine, event
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./cinematch.db")

# Create database directory if it doesn't exist (for SQLite)
if DATABASE_URL.startswith("sqlite"):
    # Extract path from sqlite URL (handles both /// and //// formats)
    db_path = DATABASE_URL.replace("sqlite://", "").lstrip("/")
    if db_path:
        # For absolute paths starting with /
        if not db_path.startswith("/"):
            db_path = "/" + db_path
        db_dir = Path(db_path).parent
        db_dir.mkdir(parents=True, exist_ok=True)
    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
else:
    engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def init_db():
    Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
