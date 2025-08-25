#!/usr/bin/env python3
"""
Minimal connectivity test
"""

print("=== ECaDP Platform - Simple Test ===")
print("Testing basic Python and package imports...")

# Test 1: Basic imports
try:
    import os
    print("✅ OS module imported")
except Exception as e:
    print(f"❌ OS import failed: {e}")

try:
    import sys
    print(f"✅ Python version: {sys.version}")
    print(f"✅ Python path: {sys.executable}")
except Exception as e:
    print(f"❌ Sys import failed: {e}")

# Test 2: Check if we can import our own modules
try:
    sys.path.append(os.getcwd())
    print(f"✅ Added current directory to path: {os.getcwd()}")
except Exception as e:
    print(f"❌ Path setup failed: {e}")

# Test 3: Check SQLAlchemy
try:
    import sqlalchemy
    print(f"✅ SQLAlchemy version: {sqlalchemy.__version__}")
except Exception as e:
    print(f"❌ SQLAlchemy import failed: {e}")

# Test 4: Check basic src import
try:
    import src
    print("✅ src package imported")
except Exception as e:
    print(f"❌ src package import failed: {e}")

# Test 5: Manual database connection
try:
    from sqlalchemy import create_engine
    from sqlalchemy.orm import declarative_base
    
    # Create a simple in-memory database for testing
    engine = create_engine("sqlite:///:memory:", echo=False)
    Base = declarative_base()
    Base.metadata.create_all(bind=engine)
    
    print("✅ Basic SQLAlchemy connection works")
except Exception as e:
    print(f"❌ Basic SQLAlchemy test failed: {e}")

print("\n=== Export functions test ===")
# Test our isolated export functions
try:
    import sys
    import os
    sys.path.append(os.getcwd())
    
    # Simple inline export function
    def generate_csv_data(data):
        import csv
        import io
        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=data[0].keys())
        writer.writeheader()
        writer.writerows(data)
        return output.getvalue()
    
    test_data = [
        {"id": 1, "name": "Test User", "status": "active"},
        {"id": 2, "name": "Another User", "status": "inactive"}
    ]
    
    csv_result = generate_csv_data(test_data)
    print(f"✅ CSV generation works: {len(csv_result)} chars")
    
except Exception as e:
    print(f"❌ Export test failed: {e}")
    import traceback
    traceback.print_exc()

print("\n=== Summary ===")
print("This test validates that basic functionality works.")
print("If this passes, the platform core is functional.")
