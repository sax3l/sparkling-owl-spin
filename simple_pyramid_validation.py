#!/usr/bin/env python3
"""
Simple Pyramid Validation - för att testa grundfunktionaliteten
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_imports():
    """Test basic imports"""
    print("Testing imports...")
    
    try:
        from core.base_classes import BaseService, BaseAgent, ServiceStatus
        print("✅ Core base classes imported successfully")
        
        from core.registry import ServiceRegistry
        print("✅ Service registry imported successfully")
        
        from engines.processing.scheduler import EnhancedBFSScheduler
        print("✅ Scheduler imported successfully")
        
        return True
    except Exception as e:
        print(f"❌ Import failed: {e}")
        return False

def test_instantiation():
    """Test basic instantiation"""
    print("\nTesting instantiation...")
    
    try:
        from core.base_classes import BaseService
        
        class TestService(BaseService):
            async def start(self):
                return True
            async def stop(self):
                return True
            async def health_check(self):
                return {'status': 'healthy'}
        
        service = TestService("test")
        print("✅ Service instantiation works")
        
        from core.registry import ServiceRegistry
        registry = ServiceRegistry()
        print("✅ Registry instantiation works")
        
        from engines.processing.scheduler import EnhancedBFSScheduler
        scheduler = EnhancedBFSScheduler("test_scheduler")
        print("✅ Scheduler instantiation works")
        
        return True
    except Exception as e:
        print(f"❌ Instantiation failed: {e}")
        return False

def main():
    print("🏗️ Simple Pyramid Architecture Validation")
    print("=" * 50)
    
    success = True
    
    success &= test_imports()
    success &= test_instantiation()
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 Basic validation PASSED!")
    else:
        print("❌ Basic validation FAILED!")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
