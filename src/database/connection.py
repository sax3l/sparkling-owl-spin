"""
Database Connection Management
High-performance connection pooling with smart routing
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, AsyncGenerator
from contextlib import asynccontextmanager
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.pool import QueuePool
from sqlalchemy import text, MetaData
import time
import ssl
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


@dataclass
class ConnectionConfig:
    """Database connection configuration."""
    url: str
    pool_size: int = 10
    max_overflow: int = 20
    pool_timeout: int = 30
    pool_recycle: int = 3600
    echo: bool = False
    ssl_context: Optional[ssl.SSLContext] = None
    connect_args: Dict[str, Any] = field(default_factory=dict)


class DatabaseConnection:
    """
    Advanced database connection manager with intelligent pooling.
    Supports PostgreSQL and MySQL with optimized connection handling.
    """
    
    def __init__(self, config: ConnectionConfig):
        self.config = config
        self.engine = None
        self.session_factory = None
        self._connection_pool_stats = {
            'total_connections': 0,
            'active_connections': 0,
            'idle_connections': 0,
            'failed_connections': 0,
            'average_connection_time': 0.0
        }
        
    async def initialize(self):
        """Initialize the database connection pool."""
        try:
            # Create async engine with optimized settings
            self.engine = create_async_engine(
                self.config.url,
                pool_size=self.config.pool_size,
                max_overflow=self.config.max_overflow,
                pool_timeout=self.config.pool_timeout,
                pool_recycle=self.config.pool_recycle,
                echo=self.config.echo,
                poolclass=QueuePool,
                connect_args=self.config.connect_args,
                # Performance optimizations
                pool_pre_ping=True,  # Verify connections before use
                pool_reset_on_return='commit',  # Clean state on return
            )
            
            # Create session factory
            self.session_factory = async_sessionmaker(
                self.engine,
                class_=AsyncSession,
                expire_on_commit=False
            )
            
            # Test connection
            await self._test_connection()
            logger.info("Database connection pool initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize database connection: {e}")
            raise
    
    async def _test_connection(self):
        """Test database connectivity."""
        start_time = time.time()
        async with self.engine.begin() as conn:
            await conn.execute(text("SELECT 1"))
        connection_time = time.time() - start_time
        self._connection_pool_stats['average_connection_time'] = connection_time
        logger.info(f"Database connection test successful ({connection_time:.3f}s)")
    
    @asynccontextmanager
    async def get_session(self) -> AsyncGenerator[AsyncSession, None]:
        """Get database session with automatic cleanup."""
        if not self.session_factory:
            raise RuntimeError("Database connection not initialized")
        
        session = self.session_factory()
        try:
            self._connection_pool_stats['active_connections'] += 1
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
            self._connection_pool_stats['active_connections'] -= 1
    
    async def execute_query(self, query: str, params: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Execute a query and return results."""
        async with self.get_session() as session:
            result = await session.execute(text(query), params or {})
            return [dict(row._mapping) for row in result]
    
    async def execute_command(self, command: str, params: Optional[Dict[str, Any]] = None) -> int:
        """Execute a command and return affected rows."""
        async with self.get_session() as session:
            result = await session.execute(text(command), params or {})
            return result.rowcount
    
    async def get_pool_status(self) -> Dict[str, Any]:
        """Get connection pool status."""
        if not self.engine:
            return {"status": "not_initialized"}
        
        pool = self.engine.pool
        return {
            "pool_size": pool.size(),
            "checked_in": pool.checkedin(),
            "checked_out": pool.checkedout(),
            "overflow": pool.overflow(),
            "invalid": pool.invalid(),
            **self._connection_pool_stats
        }
    
    async def close(self):
        """Close all connections and cleanup."""
        if self.engine:
            await self.engine.dispose()
            logger.info("Database connections closed")


class DatabaseMigrator:
    """
    Database migration manager for schema updates.
    """
    
    def __init__(self, connection: DatabaseConnection):
        self.connection = connection
        self.metadata = MetaData()
    
    async def create_tables(self):
        """Create all tables."""
        if not self.connection.engine:
            raise RuntimeError("Database connection not initialized")
        
        from .models import Base
        async with self.connection.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Database tables created successfully")
    
    async def drop_tables(self):
        """Drop all tables (use with caution)."""
        if not self.connection.engine:
            raise RuntimeError("Database connection not initialized")
        
        from .models import Base
        async with self.connection.engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
        logger.info("Database tables dropped")
    
    async def check_schema_version(self) -> Optional[str]:
        """Check current schema version."""
        try:
            result = await self.connection.execute_query(
                "SELECT version FROM schema_migrations ORDER BY created_at DESC LIMIT 1"
            )
            return result[0]['version'] if result else None
        except Exception:
            return None
    
    async def apply_migration(self, version: str, up_sql: str, down_sql: str):
        """Apply a database migration."""
        async with self.connection.get_session() as session:
            # Execute migration SQL
            await session.execute(text(up_sql))
            
            # Record migration
            await session.execute(
                text("""
                    INSERT INTO schema_migrations (version, up_sql, down_sql, created_at)
                    VALUES (:version, :up_sql, :down_sql, NOW())
                """),
                {
                    'version': version,
                    'up_sql': up_sql,
                    'down_sql': down_sql
                }
            )
        
        logger.info(f"Migration {version} applied successfully")
