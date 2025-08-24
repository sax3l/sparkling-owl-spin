"""
ECaDP Database Manager

Session factory, transaction helpers, and repository methods for all database operations.
Supports MySQL/PostgreSQL with read/write routing and bulk operations.
"""

import logging
from contextlib import contextmanager
from typing import List, Optional, Dict, Any, Union, Tuple, Iterator, Type
from sqlalchemy import create_engine, Engine, MetaData, text, inspect
from sqlalchemy.orm import sessionmaker, Session, scoped_session
from sqlalchemy.exc import SQLAlchemyError, DisconnectionError, IntegrityError
from sqlalchemy.pool import QueuePool
from sqlalchemy.dialects import mysql, postgresql
import time
import random
from datetime import datetime, timedelta

from database.models import (
    Base, Project, CrawlPlan, Template, Job, JobLog, QueueUrl, ExtractedItem,
    DQViolation, Export, Proxy, AuditEvent, User, APIKey, Policy, 
    Notification, PrivacyRequest, PIIScanResult, RetentionPolicy,
    generate_item_key, generate_url_fingerprint
)
from settings import get_settings


logger = logging.getLogger(__name__)


class DatabaseError(Exception):
    """Base exception for database errors."""
    pass


class RetryableError(DatabaseError):
    """Error that indicates operation should be retried."""
    pass


class PermanentError(DatabaseError):
    """Error that should not be retried."""
    pass


def get_retry_delay(attempt: int, base_delay: float = 1.0, max_delay: float = 60.0) -> float:
    """Calculate exponential backoff delay with jitter."""
    delay = base_delay * (2 ** attempt)
    delay = min(delay, max_delay)
    # Add jitter (±20%)
    jitter = delay * 0.2 * (random.random() * 2 - 1)
    return max(0, delay + jitter)


def is_retryable_error(error: Exception) -> bool:
    """Determine if an error should be retried."""
    if isinstance(error, (DisconnectionError,)):
        return True
    
    error_msg = str(error).lower()
    
    # MySQL retryable errors
    mysql_retryable = [
        "deadlock", "lock wait timeout", "connection lost", 
        "server has gone away", "can't connect", "timeout"
    ]
    
    # PostgreSQL retryable errors  
    postgres_retryable = [
        "deadlock_detected", "connection_failure", "admin_shutdown",
        "crash_shutdown", "cannot_connect_now", "too_many_connections"
    ]
    
    retryable_errors = mysql_retryable + postgres_retryable
    
    return any(keyword in error_msg for keyword in retryable_errors)


def retry_on_database_error(max_attempts: int = 5):
    """Decorator to retry database operations on retryable errors."""
    def decorator(func):
        def wrapper(*args, **kwargs):
            last_error = None
            
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                    
                except Exception as error:
                    last_error = error
                    
                    if not is_retryable_error(error) or attempt == max_attempts - 1:
                        logger.error(f"Database operation failed permanently: {error}")
                        if isinstance(error, IntegrityError):
                            raise PermanentError(str(error)) from error
                        raise DatabaseError(str(error)) from error
                    
                    delay = get_retry_delay(attempt)
                    logger.warning(
                        f"Database operation failed (attempt {attempt + 1}/{max_attempts}), "
                        f"retrying in {delay:.2f}s: {error}"
                    )
                    time.sleep(delay)
            
            raise DatabaseError(f"Max attempts exceeded: {last_error}") from last_error
        return wrapper
    return decorator


class DatabaseManager:
    """Central database manager with session handling and connection pooling."""
    
    def __init__(self):
        self.settings = get_settings()
        self._primary_engine: Optional[Engine] = None
        self._replica_engine: Optional[Engine] = None
        self._session_factory = None
        self._scoped_session = None
        self.vendor = self.settings.database.DB_VENDOR
        
    def _create_engine(self, dsn: str, **kwargs) -> Engine:
        """Create database engine with appropriate configuration."""
        engine_kwargs = {
            "echo": self.settings.database.DB_ECHO,
            "pool_size": self.settings.database.DB_POOL_SIZE,
            "max_overflow": self.settings.database.DB_MAX_OVERFLOW,
            "pool_timeout": self.settings.database.DB_POOL_TIMEOUT,
            "pool_recycle": self.settings.database.DB_POOL_RECYCLE,
            "poolclass": QueuePool,
            **kwargs
        }
        
        # Vendor-specific optimizations
        if self.vendor == "mysql":
            engine_kwargs.update({
                "pool_pre_ping": True,
                "connect_args": {
                    "charset": "utf8mb4",
                    "autocommit": False,
                    "sql_mode": "TRADITIONAL",
                }
            })
        elif self.vendor == "postgres":
            engine_kwargs.update({
                "pool_pre_ping": True,
                "connect_args": {
                    "application_name": "ecadp_backend",
                    "connect_timeout": 10,
                }
            })
            
        return create_engine(dsn, **engine_kwargs)
    
    def initialize(self):
        """Initialize database connections and session factory."""
        logger.info("Initializing database manager")
        
        # Create primary engine
        self._primary_engine = self._create_engine(
            self.settings.database.DB_DSN_PRIMARY
        )
        
        # Create replica engine if configured
        if self.settings.database.DB_DSN_READREPLICA:
            self._replica_engine = self._create_engine(
                self.settings.database.DB_DSN_READREPLICA
            )
            logger.info("Read replica configured")
        else:
            logger.info("No read replica configured, using primary for all reads")
            
        # Create session factory
        self._session_factory = sessionmaker(bind=self._primary_engine)
        self._scoped_session = scoped_session(self._session_factory)
        
        logger.info(f"Database manager initialized for {self.vendor}")
    
    def get_engine(self, read_only: bool = False) -> Engine:
        """Get appropriate engine based on read/write preference."""
        if read_only and self._replica_engine:
            return self._replica_engine
        return self._primary_engine
    
    @contextmanager
    def get_session(self, read_only: bool = False) -> Iterator[Session]:
        """Get database session with automatic transaction handling."""
        engine = self.get_engine(read_only=read_only)
        session = sessionmaker(bind=engine)()
        
        try:
            yield session
            if not read_only:
                session.commit()
        except Exception as e:
            session.rollback()
            logger.error(f"Database session error: {e}")
            raise
        finally:
            session.close()
    
    @contextmanager
    def get_scoped_session(self) -> Iterator[Session]:
        """Get thread-safe scoped session."""
        session = self._scoped_session()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(f"Scoped session error: {e}")
            raise
        finally:
            self._scoped_session.remove()
    
    @retry_on_database_error(max_attempts=3)
    def test_connection(self, read_only: bool = False) -> Dict[str, Any]:
        """Test database connection and return server info."""
        engine = self.get_engine(read_only=read_only)
        
        with engine.connect() as conn:
            if self.vendor == "mysql":
                result = conn.execute(text("SELECT VERSION() as version")).fetchone()
                return {
                    "vendor": "mysql",
                    "version": result.version,
                    "read_only": read_only,
                    "dsn": self.settings.database.DB_DSN_READREPLICA if read_only else self.settings.database.DB_DSN_PRIMARY
                }
            else:  # postgresql
                result = conn.execute(text("SELECT version()")).fetchone()
                return {
                    "vendor": "postgresql", 
                    "version": result[0],
                    "read_only": read_only,
                    "dsn": self.settings.database.DB_DSN_READREPLICA if read_only else self.settings.database.DB_DSN_PRIMARY
                }
    
    def create_tables(self):
        """Create all database tables."""
        logger.info("Creating database tables")
        Base.metadata.create_all(bind=self._primary_engine)
        logger.info("Database tables created successfully")
    
    def drop_tables(self):
        """Drop all database tables (development only)."""
        if not self.settings.is_development:
            raise RuntimeError("Cannot drop tables in non-development environment")
        
        logger.warning("Dropping all database tables")
        Base.metadata.drop_all(bind=self._primary_engine)
        logger.warning("All database tables dropped")


# Legacy compatibility functions
def get_db() -> Iterator[Session]:
    """Legacy function for database session (compatibility)."""
    manager = get_database_manager()
    with manager.get_session() as session:
        yield session


def create_tables():
    """Create all database tables."""
    manager = get_database_manager()
    manager.create_tables()


def drop_tables():
    """Drop all database tables."""
    manager = get_database_manager()
    manager.drop_tables()


# Global database manager instance
_db_manager = None

# Legacy session factory for backwards compatibility
def SessionLocal():
    """Create a new database session (legacy compatibility)."""
    db_manager = get_database_manager()
    return db_manager._session_factory()

def get_database_manager() -> DatabaseManager:
    """Get global database manager instance."""
    global _db_manager
    if _db_manager is None:
        _db_manager = DatabaseManager()
        _db_manager.initialize()
    return _db_manager
