"""
Database connection and session management.
"""

import os
from typing import Generator
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import QueuePool

from .config import get_settings

settings = get_settings()

# Database URL from environment or config
DATABASE_URL = os.getenv("DATABASE_URL") or settings.database_url

# Create SQLAlchemy engine
engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=settings.db_pool_size,
    max_overflow=settings.db_max_overflow,
    pool_pre_ping=True,
    pool_recycle=3600,  # Recycle connections every hour
    echo=settings.debug  # Log SQL queries in debug mode
)

# Configure connection pool events
@event.listens_for(engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    """Set SQLite pragmas for performance and reliability."""
    if "sqlite" in DATABASE_URL:
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.execute("PRAGMA journal_mode=WAL") 
        cursor.execute("PRAGMA synchronous=NORMAL")
        cursor.execute("PRAGMA cache_size=1000")
        cursor.execute("PRAGMA temp_store=MEMORY")
        cursor.close()

# Session factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

def get_db() -> Generator[Session, None, None]:
    """
    Dependency function to get database session.
    
    Yields:
        Session: SQLAlchemy database session
        
    Usage:
        @app.get("/items/")
        def read_items(db: Session = Depends(get_db)):
            return db.query(Item).all()
    """
    db = SessionLocal()
    try:
        yield db
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()

def get_db_session() -> Session:
    """
    Get a database session for use outside of FastAPI dependency injection.
    
    Returns:
        Session: SQLAlchemy database session
        
    Note:
        Remember to close the session when done:
        ```python
        db = get_db_session()
        try:
            # Use db here
            pass
        finally:
            db.close()
        ```
    """
    return SessionLocal()

def check_database_connection() -> bool:
    """
    Check if database connection is working.
    
    Returns:
        bool: True if connection is successful, False otherwise
    """
    try:
        db = SessionLocal()
        db.execute("SELECT 1")
        db.close()
        return True
    except Exception:
        return False

def create_database_tables():
    """
    Create all database tables.
    
    This should be called during application startup.
    """
    from .models.base import Base
    Base.metadata.create_all(bind=engine)

def drop_database_tables():
    """
    Drop all database tables.
    
    WARNING: This will delete all data!
    """
    from .models.base import Base
    Base.metadata.drop_all(bind=engine)
