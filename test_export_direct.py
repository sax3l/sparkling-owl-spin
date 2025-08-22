"""
Direct test of exporter functionality without complex imports.
"""

import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Set minimal environment variables
os.environ['MYSQL_PASSWORD'] = 'test123'

def test_direct_imports():
    """Test direct imports without going through __init__.py files."""
    try:
        # Import directly from files to avoid complex __init__ chains
        sys.path.append(str(project_root / 'src' / 'exporters'))
        sys.path.append(str(project_root / 'src' / 'utils'))
        
        # Test export_utils directly
        exec(open(project_root / 'src' / 'utils' / 'export_utils.py').read())
        print("✓ Successfully executed export_utils.py")
        
        # Test basic functionality
        mock_data = [{"id": 1, "name": "Test"}, {"id": 2, "name": "Test2"}]
        
        def mock_generator():
            for item in mock_data:
                yield item
        
        # Test the functions we know should exist
        csv_result = list(generate_csv_stream(mock_generator(), ["id", "name"]))
        print(f"✓ CSV generation works: {len(csv_result)} chunks")
        
        json_result = list(generate_json_stream(mock_generator()))
        print(f"✓ JSON generation works: {len(json_result)} chunks")
        
        print("\n🎉 Direct export utilities test successful!")
        return True
        
    except Exception as e:
        print(f"❌ Error in direct test: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("Direct Export Utilities Test\n" + "="*30)
    
    success = test_direct_imports()
    
    if success:
        print("\n✅ Direct test passed! Export utilities are working.")
        sys.exit(0)
    else:
        print("\n❌ Direct test failed.")
        sys.exit(1)
