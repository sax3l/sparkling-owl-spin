#!/usr/bin/env python3
"""
Step by step import test
"""

print("=== Step by step import test ===")

print("Step 1: Basic imports...")
try:
    import os
    import logging
    from typing import Optional, Generator
    print("✅ Basic imports OK")
except Exception as e:
    print(f"❌ Basic imports failed: {e}")
    exit(1)

print("Step 2: SQLAlchemy imports...")
try:
    from sqlalchemy import create_engine, Engine, text
    from sqlalchemy.orm import sessionmaker, Session, declarative_base
    from sqlalchemy.pool import QueuePool
    from sqlalchemy.exc import SQLAlchemyError
    print("✅ SQLAlchemy imports OK")
except Exception as e:
    print(f"❌ SQLAlchemy imports failed: {e}")
    exit(1)

print("Step 3: Redis imports...")
try:
    import redis
    from redis import Redis
    print("✅ Redis imports OK")
except Exception as e:
    print(f"❌ Redis imports failed: {e}")
    exit(1)

print("Step 4: Creating DatabaseConnection class...")
try:
    # SQLAlchemy Base for models
    Base = declarative_base()

    class DatabaseConnection:
        """Manages database connections and sessions."""
        
        def __init__(self, database_url: Optional[str] = None):
            """Initialize database connection."""
            self.database_url = database_url or os.getenv(
                "DATABASE_URL", 
                "mysql+pymysql://user:password@localhost:3306/crawler_db"
            )
            
            self._engine: Optional[Engine] = None
            self._session_factory: Optional[sessionmaker] = None
    
    print("✅ DatabaseConnection class created successfully")
except Exception as e:
    print(f"❌ DatabaseConnection class creation failed: {e}")
    import traceback
    traceback.print_exc()
    exit(1)

print("Step 5: Testing class instantiation...")
try:
    db = DatabaseConnection()
    print("✅ DatabaseConnection instantiated successfully")
except Exception as e:
    print(f"❌ DatabaseConnection instantiation failed: {e}")
    import traceback
    traceback.print_exc()

print("\n=== All steps completed successfully! ===")
print("DatabaseConnection can be created without imports through src package.")
