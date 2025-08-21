"""
Database connection management for the crawler application.

Provides:
- Connection pooling
- Async database operations  
- Connection health monitoring
- Transaction management
- Migration support
"""

import asyncio
import logging
from contextlib import asynccontextmanager
from typing import Optional, Dict, Any, AsyncGenerator
import os
from datetime import datetime
import asyncpg
import yaml

from src.utils.logger import get_logger

logger = get_logger(__name__)

class DatabaseConnection:
    """Manages database connections and operations."""
    
    def __init__(self, config_path: str = "config/app_config.yml"):
        self.config_path = config_path
        self.pool: Optional[asyncpg.Pool] = None
        self.config = self._load_config()
        
    def _load_config(self) -> Dict[str, Any]:
        """Load database configuration."""
        try:
            with open(self.config_path, 'r') as f:
                config = yaml.safe_load(f)
                return config.get('database', self._default_config())
        except FileNotFoundError:
            logger.warning(f"Config file not found: {self.config_path}")
            return self._default_config()
    
    def _default_config(self) -> Dict[str, Any]:
        """Default database configuration."""
        return {
            "host": os.getenv("DB_HOST", "localhost"),
            "port": int(os.getenv("DB_PORT", "5432")),
            "database": os.getenv("DB_NAME", "crawler_db"),
            "user": os.getenv("DB_USER", "postgres"),
            "password": os.getenv("DB_PASSWORD", "password"),
            "min_connections": 10,
            "max_connections": 20,
            "command_timeout": 30,
            "server_settings": {
                "application_name": "crawler_app",
                "timezone": "UTC"
            }
        }
    
    async def initialize(self) -> None:
        """Initialize database connection pool."""
        if self.pool is not None:
            logger.warning("Database pool already initialized")
            return
        
        try:
            self.pool = await asyncpg.create_pool(
                host=self.config["host"],
                port=self.config["port"],
                database=self.config["database"],
                user=self.config["user"],
                password=self.config["password"],
                min_size=self.config["min_connections"],
                max_size=self.config["max_connections"],
                command_timeout=self.config["command_timeout"],
                server_settings=self.config["server_settings"]
            )
            
            logger.info(f"Database pool initialized with {self.config['min_connections']}-{self.config['max_connections']} connections")
            
            # Test connection
            await self.health_check()
            
        except Exception as e:
            logger.error(f"Failed to initialize database pool: {e}")
            raise
    
    async def close(self) -> None:
        """Close database connection pool."""
        if self.pool:
            await self.pool.close()
            self.pool = None
            logger.info("Database pool closed")
    
    async def health_check(self) -> bool:
        """Check database connection health."""
        if not self.pool:
            return False
        
        try:
            async with self.pool.acquire() as conn:
                await conn.execute("SELECT 1")
                return True
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            return False
    
    @asynccontextmanager
    async def get_connection(self) -> AsyncGenerator[asyncpg.Connection, None]:
        """Get a database connection from the pool."""
        if not self.pool:
            await self.initialize()
        
        async with self.pool.acquire() as connection:
            yield connection
    
    @asynccontextmanager
    async def get_transaction(self) -> AsyncGenerator[asyncpg.Connection, None]:
        """Get a database connection with transaction."""
        async with self.get_connection() as conn:
            async with conn.transaction():
                yield conn
    
    async def execute(self, query: str, *args) -> Any:
        """Execute a query and return result."""
        async with self.get_connection() as conn:
            return await conn.execute(query, *args)
    
    async def fetch(self, query: str, *args) -> list:
        """Fetch multiple rows from query."""
        async with self.get_connection() as conn:
            return await conn.fetch(query, *args)
    
    async def fetchrow(self, query: str, *args) -> Optional[asyncpg.Record]:
        """Fetch single row from query."""
        async with self.get_connection() as conn:
            return await conn.fetchrow(query, *args)
    
    async def fetchval(self, query: str, *args) -> Any:
        """Fetch single value from query."""
        async with self.get_connection() as conn:
            return await conn.fetchval(query, *args)
    
    async def executemany(self, query: str, args_list: list) -> None:
        """Execute query multiple times with different arguments."""
        async with self.get_connection() as conn:
            await conn.executemany(query, args_list)
    
    async def copy_to_table(self, table_name: str, columns: list, data: list) -> None:
        """Bulk insert data using COPY."""
        async with self.get_connection() as conn:
            await conn.copy_records_to_table(table_name, records=data, columns=columns)
    
    async def get_pool_stats(self) -> Dict[str, Any]:
        """Get connection pool statistics."""
        if not self.pool:
            return {"status": "not_initialized"}
        
        return {
            "status": "active",
            "size": self.pool.get_size(),
            "min_size": self.pool.get_min_size(),
            "max_size": self.pool.get_max_size(),
            "idle_connections": self.pool.get_idle_size(),
            "checked_out": self.pool.get_size() - self.pool.get_idle_size()
        }

# Global database instance
_db_instance: Optional[DatabaseConnection] = None

async def get_db_connection() -> DatabaseConnection:
    """Get the global database connection instance."""
    global _db_instance
    
    if _db_instance is None:
        _db_instance = DatabaseConnection()
        await _db_instance.initialize()
    
    return _db_instance

async def close_db_connection():
    """Close the global database connection."""
    global _db_instance
    
    if _db_instance:
        await _db_instance.close()
        _db_instance = None

# Context manager for database operations
@asynccontextmanager
async def db_connection() -> AsyncGenerator[asyncpg.Connection, None]:
    """Context manager for database connections."""
    db = await get_db_connection()
    async with db.get_connection() as conn:
        yield conn

@asynccontextmanager  
async def db_transaction() -> AsyncGenerator[asyncpg.Connection, None]:
    """Context manager for database transactions."""
    db = await get_db_connection()
    async with db.get_transaction() as conn:
        yield conn

# Migration support
class DatabaseMigrator:
    """Handles database schema migrations."""
    
    def __init__(self, migrations_dir: str = "supabase/migrations"):
        self.migrations_dir = migrations_dir
        self.db = None
    
    async def initialize(self):
        """Initialize migrator with database connection."""
        self.db = await get_db_connection()
    
    async def ensure_migrations_table(self):
        """Create migrations tracking table if it doesn't exist."""
        await self.db.execute("""
            CREATE TABLE IF NOT EXISTS schema_migrations (
                version VARCHAR(255) PRIMARY KEY,
                applied_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
            )
        """)
    
    async def get_applied_migrations(self) -> set:
        """Get list of applied migrations."""
        result = await self.db.fetch("SELECT version FROM schema_migrations")
        return {row['version'] for row in result}
    
    async def apply_migration(self, version: str, sql: str):
        """Apply a single migration."""
        async with self.db.get_transaction() as conn:
            await conn.execute(sql)
            await conn.execute(
                "INSERT INTO schema_migrations (version) VALUES ($1)",
                version
            )
        logger.info(f"Applied migration {version}")
    
    async def run_migrations(self) -> int:
        """Run all pending migrations."""
        await self.ensure_migrations_table()
        applied = await self.get_applied_migrations()
        
        # Get migration files (would scan directory in real implementation)
        pending_migrations = []
        migrations_applied = 0
        
        for migration in pending_migrations:
            if migration['version'] not in applied:
                await self.apply_migration(migration['version'], migration['sql'])
                migrations_applied += 1
        
        return migrations_applied

async def run_migrations() -> int:
    """Run database migrations."""
    migrator = DatabaseMigrator()
    await migrator.initialize()
    return await migrator.run_migrations()
