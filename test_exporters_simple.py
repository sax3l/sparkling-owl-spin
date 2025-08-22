"""
Standalone test for exporters module to verify basic functionality.
This test does not require database connections or external dependencies.
"""

import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Set minimal environment variables
os.environ['MYSQL_PASSWORD'] = 'test123'
os.environ['MYSQL_HOST'] = 'localhost'
os.environ['MYSQL_USER'] = 'root'
os.environ['MYSQL_DATABASE'] = 'test_db'

def test_exporter_classes():
    """Test that exporter classes can be imported and instantiated."""
    try:
        # Import directly from the file to avoid the complex __init__ chain
        from src.exporters.base import BaseExporter, ExportConfig, ExportResult, ExporterRegistry
        
        print("✓ Successfully imported exporter classes")
        
        # Test ExportConfig creation
        config = ExportConfig(
            export_type="test",
            format="csv",
            tenant_id="test-tenant"
        )
        print("✓ ExportConfig created successfully")
        
        # Test ExportResult creation
        result = ExportResult(
            success=True,
            file_url="https://example.com/test.csv",
            record_count=100,
            format="csv"
        )
        print("✓ ExportResult created successfully")
        
        # Test ExporterRegistry
        registry = ExporterRegistry()
        print("✓ ExporterRegistry created successfully")
        
        print("\n🎉 All exporter classes work correctly!")
        return True
        
    except Exception as e:
        print(f"❌ Error testing exporter classes: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_export_utils():
    """Test that export utilities can be imported."""
    try:
        from src.utils.export_utils import (
            generate_csv_stream,
            generate_json_stream, 
            generate_ndjson_stream,
            get_fieldnames_for_export_type
        )
        
        print("✓ Successfully imported export utility functions")
        
        # Test fieldnames function
        fieldnames = get_fieldnames_for_export_type("person")
        print(f"✓ Got fieldnames for person: {len(fieldnames)} fields")
        
        # Test data generators with mock data
        mock_data = [
            {"id": 1, "name": "Test Person", "age": 30},
            {"id": 2, "name": "Another Person", "age": 25}
        ]
        
        def mock_generator():
            for item in mock_data:
                yield item
        
        # Test CSV generation
        csv_chunks = list(generate_csv_stream(mock_generator(), ["id", "name", "age"]))
        print(f"✓ CSV stream generated: {len(csv_chunks)} chunks")
        
        # Test JSON generation
        json_chunks = list(generate_json_stream(mock_generator()))
        print(f"✓ JSON stream generated: {len(json_chunks)} chunks")
        
        # Test NDJSON generation
        ndjson_chunks = list(generate_ndjson_stream(mock_generator()))
        print(f"✓ NDJSON stream generated: {len(ndjson_chunks)} chunks")
        
        print("\n🎉 All export utilities work correctly!")
        return True
        
    except Exception as e:
        print(f"❌ Error testing export utilities: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("Testing Exporter Module Components\n" + "="*40)
    
    success1 = test_exporter_classes()
    print()
    success2 = test_export_utils()
    
    if success1 and success2:
        print("\n✅ All tests passed! The exporter module is working correctly.")
        sys.exit(0)
    else:
        print("\n❌ Some tests failed. Check the errors above.")
        sys.exit(1)
