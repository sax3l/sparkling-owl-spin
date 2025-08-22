#!/usr/bin/env python3
"""
Test script to identify import issues
"""

print("Testing imports...")

try:
    from src.database.connection import get_db_connection
    print("✅ Database connection import OK")
except ImportError as e:
    print(f"❌ Database connection import failed: {e}")

try:
    from src.database.models import User
    print("✅ Database models import OK")
except ImportError as e:
    print(f"❌ Database models import failed: {e}")

try:
    from src.services.auth import AuthService
    print("✅ Auth service import OK")
except ImportError as e:
    print(f"❌ Auth service import failed: {e}")

try:
    from src.services.cache import CacheService
    print("✅ Cache service import OK")
except ImportError as e:
    print(f"❌ Cache service import failed: {e}")

try:
    from src.utils.config import get_settings
    print("✅ Config utils import OK")
except ImportError as e:
    print(f"❌ Config utils import failed: {e}")

try:
    from src.webapp.deps import get_database
    print("✅ Webapp deps import OK")
except ImportError as e:
    print(f"❌ Webapp deps import failed: {e}")

try:
    from src.webapp.routers.health import router
    print("✅ Health router import OK")
except ImportError as e:
    print(f"❌ Health router import failed: {e}")

print("Import test completed!")
