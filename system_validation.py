#!/usr/bin/env python3
"""
System Val        # Scheduler
        ("scheduler.scheduler", ["CrawlScheduler"]),
        ("scheduler.job_definitions", ["JobDefinition", "JobPriority"]),tion Test - Komplett systemvalidering
=====================================

Detta script validerar att alla kritiska systemkomponenter fungerar korrekt.
"""

import sys
import os
from pathlib import Path
import importlib
import traceback

# Add src to path
project_root = Path(__file__).parent
src_path = project_root / "src"
sys.path.insert(0, str(src_path))

def test_critical_imports():
    """Testa import av kritiska systemkomponenter"""
    
    critical_modules = [
        # Database layer
        ("database.models", ["User", "Job", "Template", "Project"]),
        ("database.manager", ["DatabaseManager"]),
        
        # Core crawler components  
        ("crawler.sitemap_generator", ["SitemapGenerator"]),
        ("crawler.url_queue", ["URLQueue"]),
        
        # Scraper system
        ("scraper.base_scraper", ["BaseScraper"]),
        ("scraper.http_scraper", ["HTTPScraper"]),
        
        # Proxy system
        ("proxy_pool.manager", ["ProxyPoolManager"]),
        ("proxy_pool.validator", ["ProxyValidator"]),
        
        # Scheduler
        ("scheduler.scheduler", ["ECaDPScheduler"]),
        ("scheduler.job_definitions", ["JobDefinition", "JobPriority"]),
        
        # Exporters
        ("exporters.csv_exporter", ["CSVExporter"]),
        ("exporters.json_exporter", ["JSONExporter"]),
        
        # Utils
        ("utils.logger", ["get_logger"]),
        ("utils.validators", ["URLValidator"]),
    ]
    
    results = {"passed": 0, "failed": 0, "errors": []}
    
    print("🔍 TESTER KRITISKA SYSTEMIMPORTER...")
    print("=" * 60)
    
    for module_name, class_names in critical_modules:
        try:
            module = importlib.import_module(module_name)
            
            # Test that required classes exist
            for class_name in class_names:
                if hasattr(module, class_name):
                    print(f"✅ {module_name}.{class_name}")
                    results["passed"] += 1
                else:
                    print(f"❌ {module_name}.{class_name} - Klass saknas")
                    results["failed"] += 1
                    results["errors"].append(f"{module_name}.{class_name} - Klass saknas")
                    
        except Exception as e:
            print(f"❌ {module_name} - Import fel: {e}")
            results["failed"] += 1
            results["errors"].append(f"{module_name} - {str(e)}")
    
    return results

def test_configuration_files():
    """Testa att kritiska konfigurationsfiler finns"""
    
    required_files = [
        "pyproject.toml",
        "requirements.txt", 
        "README.md",
        "src/__init__.py",
        "src/settings.py",
    ]
    
    print("\n🔍 TESTER KONFIGURATIONSFILER...")
    print("=" * 60)
    
    results = {"passed": 0, "failed": 0}
    
    for file_path in required_files:
        full_path = project_root / file_path
        if full_path.exists():
            print(f"✅ {file_path}")
            results["passed"] += 1
        else:
            print(f"❌ {file_path} - Saknas")
            results["failed"] += 1
    
    return results

def test_directory_structure():
    """Testa att kritiska mappar finns"""
    
    required_dirs = [
        "src",
        "src/database",
        "src/crawler",
        "src/scraper", 
        "src/proxy_pool",
        "src/scheduler",
        "src/exporters",
        "src/utils",
        "tests",
        "config",
        "docs",
    ]
    
    print("\n🔍 TESTER MAPPSTRUKTUR...")
    print("=" * 60)
    
    results = {"passed": 0, "failed": 0}
    
    for dir_path in required_dirs:
        full_path = project_root / dir_path
        if full_path.exists() and full_path.is_dir():
            print(f"✅ {dir_path}/")
            results["passed"] += 1
        else:
            print(f"❌ {dir_path}/ - Saknas")
            results["failed"] += 1
    
    return results

def main():
    """Kör alla systemvalideringstester"""
    
    print("🚀 SPARKLING OWL SPIN - SYSTEMVALIDERING")
    print("=" * 60)
    print(f"📍 Projektrot: {project_root}")
    print(f"🐍 Python: {sys.version}")
    print("=" * 60)
    
    # Run all tests
    import_results = test_critical_imports()
    config_results = test_configuration_files()  
    dir_results = test_directory_structure()
    
    # Summary
    total_passed = import_results["passed"] + config_results["passed"] + dir_results["passed"]
    total_failed = import_results["failed"] + config_results["failed"] + dir_results["failed"]
    total_tests = total_passed + total_failed
    
    print("\n" + "=" * 60)
    print("📊 SAMMANFATTNING AV SYSTEMVALIDERING")
    print("=" * 60)
    print(f"✅ Godkända tester: {total_passed}")
    print(f"❌ Misslyckade tester: {total_failed}")
    print(f"📈 Framgångsfrekvens: {(total_passed/total_tests)*100:.1f}%")
    
    if import_results["errors"]:
        print(f"\n🔥 KRITISKA FEL:")
        for error in import_results["errors"]:
            print(f"   • {error}")
    
    # Spara resultat till JSON för andra script att läsa
    import json
    from datetime import datetime
    
    results = {
        "total_tests": total_tests,
        "passed_tests": total_passed,
        "failed_tests": total_failed,
        "success_rate": (total_passed/total_tests)*100,
        "timestamp": datetime.now().isoformat(),
        "errors": import_results["errors"],
        "import_results": import_results,
        "config_results": config_results,
        "directory_results": dir_results
    }
    
    results_file = project_root / "system_validation_results.json"
    with open(results_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"📄 Resultat sparade i: {results_file.name}")
    
    if total_failed == 0:
        print(f"\n🎉 SYSTEMVALIDERING LYCKAD!")
        print("   Alla kritiska komponenter fungerar korrekt.")
        return 0
    else:
        print(f"\n⚠️  SYSTEMVALIDERING MISSLYCKAD!")
        print(f"   {total_failed} komponenter behöver åtgärdas.")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
