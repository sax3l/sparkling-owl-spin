#!/usr/bin/env python3
"""
Simple test for database import
"""

try:
    from src.database.connection import DatabaseConnection
    print("✅ Database connection imported successfully!")
except Exception as e:
    print(f"❌ Error importing database connection: {e}")
    import traceback
    traceback.print_exc()
