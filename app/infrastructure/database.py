from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

# Check if we're in test environment
_test_mode = os.getenv("PYTEST_CURRENT_TEST") is not None

try:
    if _test_mode:
        # Use SQLite for tests
        database_url = "sqlite:///./test_app.db"
        engine = create_engine(database_url, connect_args={"check_same_thread": False}, echo=False)
    else:
        from app.infrastructure.config import settings
        database_url = settings.DATABASE_URL
        engine = create_engine(database_url, echo=settings.DEBUG)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
except Exception as e:
    # If database connection fails, create a dummy engine for imports
    # This allows tests to override it
    print(f"Warning: Could not create database engine: {e}")
    engine = None
    SessionLocal = None

Base = declarative_base()


def get_db():
    """Dependency for getting database session"""
    if SessionLocal is None:
        raise RuntimeError("Database session not initialized. Check database connection.")
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


