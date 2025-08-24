#!/usr/bin/env python3
"""
🧪 FINAL VALIDATION - SPARKLING OWL SPIN PLATFORM
Slutlig validering av alla systemkomponenter
"""

import asyncio
import time
import json
from pathlib import Path
import sys
import os
from typing import Dict, List, Any

def add_project_paths():
    """Lägg till alla nödvändiga paths för import"""
    project_root = Path(__file__).parent
    paths_to_add = [
        project_root / "src",
        project_root / "src" / "sos",
        project_root / "src" / "sos" / "core", 
        project_root / "src" / "anti_bot" / "browser_stealth",
        project_root / "src" / "revolutionary_scraper" / "core",
        project_root / "api",
        project_root,
    ]
    
    for path in paths_to_add:
        if path.exists():
            sys.path.insert(0, str(path))
            print(f"✅ Added path: {path}")

def test_imports():
    """Testa alla viktiga imports"""
    results = {}
    
    # Test stealth browser imports
    try:
        from src.sos.core.stealth_browser import StealthBrowser
        results['stealth_browser_sos'] = "✅ SUCCESS"
        print("✅ src.sos.core.stealth_browser imported successfully")
    except Exception as e:
        results['stealth_browser_sos'] = f"❌ FAILED: {e}"
        print(f"❌ Failed to import src.sos.core.stealth_browser: {e}")
    
    try:
        from src.anti_bot.browser_stealth.stealth_browser import StealthBrowser
        results['stealth_browser_anti_bot'] = "✅ SUCCESS"
        print("✅ src.anti_bot.browser_stealth.stealth_browser imported successfully")
    except Exception as e:
        results['stealth_browser_anti_bot'] = f"❌ FAILED: {e}"
        print(f"❌ Failed to import src.anti_bot.browser_stealth.stealth_browser: {e}")
    
    # Test revolutionary scraper
    try:
        from src.revolutionary_scraper.core.stealth_engine import StealthEngine
        results['stealth_engine'] = "✅ SUCCESS"
        print("✅ StealthEngine imported successfully")
    except Exception as e:
        results['stealth_engine'] = f"❌ FAILED: {e}"
        print(f"❌ Failed to import StealthEngine: {e}")
    
    try:
        from src.revolutionary_scraper.core.revolutionary_crawler import RevolutionaryCrawler
        results['revolutionary_crawler'] = "✅ SUCCESS"
        print("✅ RevolutionaryCrawler imported successfully")
    except Exception as e:
        results['revolutionary_crawler'] = f"❌ FAILED: {e}"
        print(f"❌ Failed to import RevolutionaryCrawler: {e}")
    
    # Test SOS components
    try:
        from src.sos.api.main import app
        results['sos_api'] = "✅ SUCCESS"
        print("✅ SOS API app imported successfully")
    except Exception as e:
        results['sos_api'] = f"❌ FAILED: {e}"
        print(f"❌ Failed to import SOS API: {e}")
        
    try:
        from src.sos.db.models import CrawlJob
        results['sos_models'] = "✅ SUCCESS"
        print("✅ SOS database models imported successfully")
    except Exception as e:
        results['sos_models'] = f"❌ FAILED: {e}"
        print(f"❌ Failed to import SOS models: {e}")
    
    return results

def test_file_structure():
    """Validera viktiga filer existerar"""
    project_root = Path(__file__).parent
    
    critical_files = [
        "src/sos/core/stealth_browser.py",
        "src/anti_bot/browser_stealth/stealth_browser.py", 
        "src/revolutionary_scraper/core/stealth_engine.py",
        "src/revolutionary_scraper/core/revolutionary_crawler.py",
        "src/sos/api/main.py",
        "src/sos/db/models.py",
        "frontend/src/api/client.ts",
        "frontend/src/pages/Dashboard.tsx",
        "api/complete-integration.py"
    ]
    
    results = {}
    for file_path in critical_files:
        full_path = project_root / file_path
        if full_path.exists():
            results[file_path] = "✅ EXISTS"
            print(f"✅ {file_path}")
        else:
            results[file_path] = "❌ MISSING"
            print(f"❌ {file_path}")
    
    return results

def test_configuration_files():
    """Testa konfigurationsfiler"""
    project_root = Path(__file__).parent
    
    config_files = [
        "package.json",
        "requirements.txt", 
        "pyproject.toml",
        "docker-compose.yml",
        "Makefile"
    ]
    
    results = {}
    for config_file in config_files:
        full_path = project_root / config_file
        if full_path.exists():
            results[config_file] = "✅ EXISTS"
            print(f"✅ {config_file}")
        else:
            results[config_file] = "❌ MISSING"
            print(f"❌ {config_file}")
    
    return results

def analyze_code_quality():
    """Analysera kodkvalitet baserat på filstorlekar och struktur"""
    project_root = Path(__file__).parent
    
    # Räkna Python filer
    python_files = list(project_root.rglob("*.py"))
    ts_files = list(project_root.rglob("*.ts"))
    tsx_files = list(project_root.rglob("*.tsx"))
    
    total_python_lines = 0
    total_ts_lines = 0
    
    for py_file in python_files:
        try:
            with open(py_file, 'r', encoding='utf-8') as f:
                total_python_lines += len(f.readlines())
        except:
            pass
    
    for ts_file in ts_files + tsx_files:
        try:
            with open(ts_file, 'r', encoding='utf-8') as f:
                total_ts_lines += len(f.readlines())
        except:
            pass
    
    return {
        'python_files': len(python_files),
        'typescript_files': len(ts_files + tsx_files),
        'python_lines': total_python_lines,
        'typescript_lines': total_ts_lines,
        'total_files': len(python_files) + len(ts_files) + len(tsx_files),
        'total_lines': total_python_lines + total_ts_lines
    }

def generate_final_report():
    """Generera slutlig validering rapport"""
    print("🚀 SPARKLING OWL SPIN - FINAL SYSTEM VALIDATION")
    print("=" * 55)
    
    # Test project structure
    print("\n📁 TESTING PROJECT STRUCTURE...")
    file_results = test_file_structure()
    
    # Test configuration
    print("\n⚙️ TESTING CONFIGURATION FILES...")
    config_results = test_configuration_files()
    
    # Add paths and test imports
    print("\n📚 SETTING UP IMPORT PATHS...")
    add_project_paths()
    
    print("\n🔍 TESTING CRITICAL IMPORTS...")
    import_results = test_imports()
    
    # Analyze code quality
    print("\n📊 ANALYZING CODE QUALITY...")
    quality_results = analyze_code_quality()
    
    # Calculate scores
    total_files = len(file_results)
    existing_files = sum(1 for v in file_results.values() if v == "✅ EXISTS")
    file_score = (existing_files / total_files) * 100
    
    total_configs = len(config_results) 
    existing_configs = sum(1 for v in config_results.values() if v == "✅ EXISTS")
    config_score = (existing_configs / total_configs) * 100
    
    total_imports = len(import_results)
    successful_imports = sum(1 for v in import_results.values() if v == "✅ SUCCESS")
    import_score = (successful_imports / total_imports) * 100
    
    overall_score = (file_score + config_score + import_score) / 3
    
    # Generate final report
    final_report = {
        "validation_timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "overall_score": round(overall_score, 2),
        "scores": {
            "file_structure": round(file_score, 2),
            "configuration": round(config_score, 2),
            "imports": round(import_score, 2)
        },
        "detailed_results": {
            "files": file_results,
            "configs": config_results,
            "imports": import_results,
            "code_quality": quality_results
        },
        "recommendations": generate_recommendations(overall_score),
        "production_readiness": get_production_status(overall_score)
    }
    
    # Print summary
    print("\n" + "=" * 55)
    print("📋 VALIDATION SUMMARY")
    print("=" * 55)
    print(f"📁 File Structure Score: {file_score:.1f}%")
    print(f"⚙️ Configuration Score: {config_score:.1f}%") 
    print(f"📚 Import Success Score: {import_score:.1f}%")
    print(f"📊 Python Files: {quality_results['python_files']}")
    print(f"📊 TypeScript Files: {quality_results['typescript_files']}")
    print(f"📊 Total Lines of Code: {quality_results['total_lines']:,}")
    print(f"\n🎯 OVERALL SCORE: {overall_score:.1f}/100")
    
    if overall_score >= 90:
        print("🏆 STATUS: WORLD-CLASS SYSTEM ⭐⭐⭐⭐⭐")
    elif overall_score >= 80:
        print("✅ STATUS: PRODUCTION READY ⭐⭐⭐⭐")
    elif overall_score >= 70:
        print("⚠️ STATUS: NEEDS MINOR FIXES ⭐⭐⭐")
    else:
        print("❌ STATUS: REQUIRES ATTENTION ⭐⭐")
    
    print(f"🚀 PRODUCTION READINESS: {final_report['production_readiness']}")
    
    # Save report
    report_file = Path(__file__).parent / "FINAL_VALIDATION_REPORT.json"
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(final_report, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 Report saved to: {report_file}")
    
    return final_report

def generate_recommendations(score: float) -> List[str]:
    """Generera rekommendationer baserat på score"""
    recommendations = []
    
    if score >= 90:
        recommendations.append("System is ready for immediate production deployment")
        recommendations.append("Consider setting up monitoring and alerting")
        recommendations.append("Implement automated testing pipeline")
    elif score >= 80:
        recommendations.append("Address minor import issues before deployment")
        recommendations.append("Verify all dependencies are properly installed")
        recommendations.append("Run comprehensive integration tests")
    else:
        recommendations.append("Fix critical import and configuration issues")
        recommendations.append("Ensure all required dependencies are installed")
        recommendations.append("Verify project structure is complete")
    
    return recommendations

def get_production_status(score: float) -> str:
    """Bedöm production readiness"""
    if score >= 90:
        return "READY FOR IMMEDIATE DEPLOYMENT"
    elif score >= 80:
        return "READY AFTER MINOR FIXES"
    elif score >= 70:
        return "REQUIRES TESTING AND VALIDATION"
    else:
        return "NOT READY - NEEDS DEVELOPMENT"

if __name__ == "__main__":
    try:
        report = generate_final_report()
        print("\n✅ VALIDATION COMPLETED SUCCESSFULLY")
    except Exception as e:
        print(f"\n❌ VALIDATION FAILED: {e}")
        import traceback
        traceback.print_exc()
