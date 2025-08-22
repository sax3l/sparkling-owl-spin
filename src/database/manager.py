import os
import asyncio
import logging
from contextlib import asynccontextmanager
from typing import Optional, Dict, Any, List, AsyncGenerator
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from dotenv import load_dotenv
import aiomysql
import pymysql

from src.utils.simple_logger import get_logger

load_dotenv()

logger = get_logger(__name__)

# MySQL Database URL construction from environment variables
def get_mysql_url(async_driver: bool = False) -> str:
    """Construct MySQL database URL from environment variables"""
    host = os.getenv("MYSQL_HOST", "localhost")
    port = os.getenv("MYSQL_PORT", "3306")
    database = os.getenv("MYSQL_DATABASE", "ecadp")
    username = os.getenv("MYSQL_USER", "ecadp_user")
    password = os.getenv("MYSQL_PASSWORD")
    
    if not password:
        raise ValueError("MYSQL_PASSWORD environment variable must be set")
    
    if async_driver:
        return f"mysql+aiomysql://{username}:{password}@{host}:{port}/{database}?charset=utf8mb4"
    else:
        return f"mysql+pymysql://{username}:{password}@{host}:{port}/{database}?charset=utf8mb4"

# Get database URLs
DATABASE_URL = get_mysql_url(async_driver=False)
ASYNC_DATABASE_URL = get_mysql_url(async_driver=True)

# Sync SQLAlchemy setup
engine = create_engine(
    DATABASE_URL,
    pool_size=int(os.getenv("MYSQL_POOL_SIZE", "10")),
    max_overflow=int(os.getenv("MYSQL_MAX_OVERFLOW", "20")),
    pool_timeout=int(os.getenv("MYSQL_POOL_TIMEOUT", "30")),
    pool_recycle=int(os.getenv("MYSQL_POOL_RECYCLE", "3600")),
    echo=os.getenv("ENVIRONMENT", "development") == "development"
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Async engine for async operations
async_engine = create_async_engine(
    ASYNC_DATABASE_URL,
    pool_size=int(os.getenv("MYSQL_POOL_SIZE", "10")),
    max_overflow=int(os.getenv("MYSQL_MAX_OVERFLOW", "20")),
    pool_timeout=int(os.getenv("MYSQL_POOL_TIMEOUT", "30")),
    pool_recycle=int(os.getenv("MYSQL_POOL_RECYCLE", "3600")),
    echo=os.getenv("ENVIRONMENT", "development") == "development"
)

def get_db():
    """Dependency for FastAPI - provides sync database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class DatabaseManager:
    """
    Comprehensive MySQL database manager that provides both sync and async operations.
    
    Features:
    - MySQL connection management and pooling
    - Query execution and transaction management  
    - Data validation and error handling
    - Health monitoring and metrics
    - Support for both sync and async operations
    """
    
    def __init__(self, database_url: Optional[str] = None):
        self.database_url = database_url or DATABASE_URL
        self.sync_engine = create_engine(self.database_url)
        self.async_engine = create_async_engine(
            self.database_url.replace("postgresql://", "postgresql+asyncpg://")
        )
        self._session_factory = sessionmaker(
            autocommit=False, 
            autoflush=False, 
            bind=self.sync_engine
        )
        self._connection_pool: Optional[asyncpg.Pool] = None
        
    async def initialize(self):
        """Initialize async connection pool"""
        try:
            # Extract connection parameters from URL
            url_parts = self.database_url.replace("postgresql://", "").split("@")
            if len(url_parts) == 2:
                credentials, host_db = url_parts
                user_pass = credentials.split(":")
                host_port_db = host_db.split("/")
                
                if len(user_pass) == 2 and len(host_port_db) >= 2:
                    user, password = user_pass
                    host_port = host_port_db[0].split(":")
                    host = host_port[0]
                    port = int(host_port[1]) if len(host_port) > 1 else 5432
                    database = host_port_db[1].split("?")[0]  # Remove query params
                    
                    self._connection_pool = await asyncpg.create_pool(
                        host=host,
                        port=port,
                        user=user,
                        password=password,
                        database=database,
                        min_size=2,
                        max_size=10
                    )
                    logger.info("Database connection pool initialized")
                else:
                    raise ValueError("Invalid database URL format")
            else:
                raise ValueError("Invalid database URL format")
        except Exception as e:
            logger.error(f"Failed to initialize database connection pool: {e}")
            raise
    
    async def close(self):
        """Close all connections"""
        if self._connection_pool:
            await self._connection_pool.close()
            logger.info("Database connection pool closed")
    
    @asynccontextmanager
    async def get_connection(self):
        """Get async database connection from pool"""
        if not self._connection_pool:
            await self.initialize()
        
        async with self._connection_pool.acquire() as connection:
            yield connection
    
    @asynccontextmanager 
    async def get_transaction(self):
        """Get database transaction context"""
        async with self.get_connection() as conn:
            async with conn.transaction():
                yield conn
    
    def get_session(self) -> Session:
        """Get sync SQLAlchemy session"""
        return self._session_factory()
    
    @asynccontextmanager
    async def get_async_session(self) -> AsyncGenerator[AsyncSession, None]:
        """Get async SQLAlchemy session"""
        from sqlalchemy.ext.asyncio import AsyncSession as SQLAsyncSession
        
        async with SQLAsyncSession(self.async_engine) as session:
            yield session
    
    # Async query methods
    async def fetch_one(self, query: str, *args) -> Optional[Dict[str, Any]]:
        """Execute query and fetch one result"""
        async with self.get_connection() as conn:
            result = await conn.fetchrow(query, *args)
            return dict(result) if result else None
    
    async def fetch_all(self, query: str, *args) -> List[Dict[str, Any]]:
        """Execute query and fetch all results"""
        async with self.get_connection() as conn:
            results = await conn.fetch(query, *args)
            return [dict(row) for row in results]
    
    async def execute(self, query: str, *args) -> str:
        """Execute query (INSERT, UPDATE, DELETE)"""
        async with self.get_connection() as conn:
            return await conn.execute(query, *args)
    
    async def execute_many(self, query: str, args_list: List[tuple]) -> None:
        """Execute query multiple times with different parameters"""
        async with self.get_connection() as conn:
            await conn.executemany(query, args_list)
    
    # Sync query methods for backward compatibility
    def sync_fetch_one(self, query: str, params: Dict[str, Any] = None) -> Optional[Dict[str, Any]]:
        """Sync version of fetch_one"""
        with self.get_session() as session:
            result = session.execute(text(query), params or {})
            row = result.fetchone()
            return dict(row._mapping) if row else None
    
    def sync_fetch_all(self, query: str, params: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Sync version of fetch_all"""
        with self.get_session() as session:
            result = session.execute(text(query), params or {})
            return [dict(row._mapping) for row in result.fetchall()]
    
    def sync_execute(self, query: str, params: Dict[str, Any] = None) -> None:
        """Sync version of execute"""
        with self.get_session() as session:
            session.execute(text(query), params or {})
            session.commit()
    
    # Health and monitoring
    async def health_check(self) -> Dict[str, Any]:
        """Check database health"""
        try:
            async with self.get_connection() as conn:
                result = await conn.fetchval("SELECT 1")
                return {
                    "status": "healthy",
                    "database": "connected",
                    "pool_size": self._connection_pool.get_size() if self._connection_pool else 0,
                    "test_query": result == 1
                }
        except Exception as e:
            return {
                "status": "unhealthy", 
                "error": str(e),
                "database": "disconnected"
            }
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get database statistics"""
        try:
            stats = {}
            if self._connection_pool:
                stats.update({
                    "pool_size": self._connection_pool.get_size(),
                    "pool_min_size": self._connection_pool.get_min_size(),
                    "pool_max_size": self._connection_pool.get_max_size(),
                })
            
            # Get database-specific stats
            async with self.get_connection() as conn:
                # Table counts
                table_stats = await conn.fetch("""
                    SELECT schemaname, tablename, n_tup_ins, n_tup_upd, n_tup_del
                    FROM pg_stat_user_tables 
                    WHERE schemaname = 'public'
                """)
                
                stats["tables"] = [dict(row) for row in table_stats]
                
                # Database size
                db_size = await conn.fetchval("""
                    SELECT pg_size_pretty(pg_database_size(current_database()))
                """)
                stats["database_size"] = db_size
                
            return stats
        except Exception as e:
            logger.error(f"Failed to get database stats: {e}")
            return {"error": str(e)}


# Global instance for backward compatibility
_db_manager: Optional[DatabaseManager] = None

def get_database_manager() -> DatabaseManager:
    """Get global database manager instance"""
    global _db_manager
    if _db_manager is None:
        _db_manager = DatabaseManager()
    return _db_manager


# Async context manager for sessions
@asynccontextmanager
async def get_async_session():
    """Get async database session - compatibility function"""
    manager = get_database_manager()
    async with manager.get_async_session() as session:
        yield session