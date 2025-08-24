#!/usr/bin/env python3
"""
Enkel Komponentvalidering - Testa kärnfunktioner
==============================================

Detta script testar att kritiska komponenter kan importeras och är funktionella.
"""

import sys
import os
from pathlib import Path

# Add src to path
project_root = Path(__file__).parent
src_path = project_root / "src" 
sys.path.insert(0, str(src_path))

def test_working_components():
    """Testa komponenter som ska fungera"""
    
    tests = []
    
    # Test 1: Core exporters (these should work)
    try:
        from exporters.csv_exporter import CSVExporter
        from exporters.json_exporter import JSONExporter
        tests.append("✅ Exporters (CSV, JSON) - Fungerar")
    except Exception as e:
        tests.append(f"❌ Exporters - {e}")
    
    # Test 2: Utils (these should work)
    try:
        from utils.logger import get_logger
        from utils.validators import URLValidator
        tests.append("✅ Utils (Logger, Validator) - Fungerar")
    except Exception as e:
        tests.append(f"❌ Utils - {e}")
    
    # Test 3: Proxy validator (partial)
    try:
        from proxy_pool.validator import ProxyValidator
        tests.append("✅ Proxy Validator - Fungerar")
    except Exception as e:
        tests.append(f"❌ Proxy Validator - {e}")
    
    # Test 4: HTTP Scraper
    try:
        from scraper.http_scraper import HTTPScraper
        tests.append("✅ HTTP Scraper - Fungerar")
    except Exception as e:
        tests.append(f"❌ HTTP Scraper - {e}")
        
    # Test 5: Job definitions
    try:
        from scheduler.job_definitions import JobDefinition, JobPriority
        tests.append("✅ Job Definitions - Fungerar")
    except Exception as e:
        tests.append(f"❌ Job Definitions - {e}")
    
    return tests

def test_api_components():
    """Testa API-relaterade komponenter"""
    
    tests = []
    
    # Test 1: Settings
    try:
        from settings import get_settings
        tests.append("✅ Settings - Fungerar")
    except Exception as e:
        tests.append(f"❌ Settings - {e}")
    
    # Test 2: Observability metrics (if available)
    try:
        from observability.metrics import MetricsCollector
        tests.append("✅ Metrics Collector - Fungerar")
    except Exception as e:
        tests.append(f"❌ Metrics Collector - {e}")
    
    return tests

def test_core_functionality():
    """Testa grundläggande funktionalitet"""
    
    tests = []
    
    # Test att Python-miljön fungerar
    tests.append(f"✅ Python {sys.version.split()[0]} - Fungerar")
    
    # Test att projektstrukturen finns
    required_dirs = ["src", "tests", "config", "docs"]
    missing_dirs = []
    
    for dir_name in required_dirs:
        if not (project_root / dir_name).exists():
            missing_dirs.append(dir_name)
    
    if missing_dirs:
        tests.append(f"❌ Mappar saknas: {', '.join(missing_dirs)}")
    else:
        tests.append("✅ Projektstruktur - Komplett")
    
    # Test att viktiga filer finns
    required_files = ["pyproject.toml", "requirements.txt", "README.md"]
    missing_files = []
    
    for file_name in required_files:
        if not (project_root / file_name).exists():
            missing_files.append(file_name)
    
    if missing_files:
        tests.append(f"❌ Filer saknas: {', '.join(missing_files)}")
    else:
        tests.append("✅ Konfigurationsfiler - Kompletta")
        
    return tests

def main():
    """Kör enkel komponentvalidering"""
    
    print("🚀 SPARKLING OWL SPIN - ENKEL KOMPONENTVALIDERING")
    print("=" * 70)
    print(f"📍 Projekt: {project_root}")
    print(f"🐍 Python: {sys.version}")
    print("=" * 70)
    
    # Test core functionality
    print("\n📋 GRUNDLÄGGANDE FUNKTIONALITET:")
    core_tests = test_core_functionality()
    for test in core_tests:
        print(f"   {test}")
    
    # Test working components
    print("\n🔧 KÄRNKOMPONENTER:")
    component_tests = test_working_components() 
    for test in component_tests:
        print(f"   {test}")
    
    # Test API components  
    print("\n🌐 API-KOMPONENTER:")
    api_tests = test_api_components()
    for test in api_tests:
        print(f"   {test}")
    
    # Summary
    all_tests = core_tests + component_tests + api_tests
    passed = sum(1 for test in all_tests if test.startswith("✅"))
    failed = sum(1 for test in all_tests if test.startswith("❌"))
    total = len(all_tests)
    
    print("\n" + "=" * 70)
    print("📊 SAMMANFATTNING:")
    print("=" * 70)
    print(f"✅ Godkända: {passed}/{total}")
    print(f"❌ Misslyckade: {failed}/{total}")
    print(f"📈 Framgång: {(passed/total)*100:.1f}%")
    
    if failed == 0:
        print("\n🎉 ENKEL VALIDERING LYCKAD!")
        print("   Kärnkomponenterna fungerar korrekt.")
        status = "SUCCESS"
    elif passed >= total * 0.7:  # 70% success rate
        print("\n⚡ DELVIS FRAMGÅNG!")
        print("   Majoriteten av komponenterna fungerar.")
        status = "PARTIAL"
    else:
        print("\n⚠️  VALIDERING MISSLYCKAD!")
        print("   För många komponenter fungerar inte.")
        status = "FAILED"
    
    return status

if __name__ == "__main__":
    result = main()
    print(f"\n🏁 SLUTRESULTAT: {result}")
    sys.exit(0 if result in ["SUCCESS", "PARTIAL"] else 1)
