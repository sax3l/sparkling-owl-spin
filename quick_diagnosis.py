#!/usr/bin/env python3
"""
Snabb problemdiagnostik - fokuserar på de 3 kvarvarande problemen
"""

import sys
import os
from pathlib import Path

# Add src to path
project_root = Path(__file__).parent
src_path = project_root / "src" 
sys.path.insert(0, str(src_path))

def test_specific_imports():
    """Test the 3 failing imports"""
    
    results = {"passed": 0, "failed": 0, "details": []}
    
    # Test 1: crawler.sitemap_generator
    try:
        import crawler.sitemap_generator
        results["passed"] += 1
        results["details"].append("✅ crawler.sitemap_generator - OK")
    except Exception as e:
        results["failed"] += 1
        results["details"].append(f"❌ crawler.sitemap_generator - {e}")
    
    # Test 2: crawler.url_queue  
    try:
        import crawler.url_queue
        results["passed"] += 1
        results["details"].append("✅ crawler.url_queue - OK")
    except Exception as e:
        results["failed"] += 1
        results["details"].append(f"❌ crawler.url_queue - {e}")
        
    # Test 3: scheduler.scheduler
    try:
        import scheduler.scheduler
        results["passed"] += 1
        results["details"].append("✅ scheduler.scheduler - OK")
    except Exception as e:
        results["failed"] += 1
        results["details"].append(f"❌ scheduler.scheduler - {e}")
        
    return results

if __name__ == "__main__":
    print("🎯 PROBLEMDIAGNOSTIK - DE 3 SISTA FELEN")
    print("=" * 50)
    
    results = test_specific_imports()
    
    for detail in results["details"]:
        print(detail)
        
    print()
    print(f"📊 RESULTAT: {results['passed']}/3 godkända")
    
    if results["failed"] == 0:
        print("🎉 ALLA PROBLEM LÖSTA!")
        sys.exit(0)
    else:
        print(f"⚠️ {results['failed']} problem återstår")
        sys.exit(1)
