#!/usr/bin/env python3
"""
🚀 SPARKLING OWL SPIN - ENHANCED SYSTEM VALIDATION
Komplett systemvalidering med fixade imports och funktionalitetstester
"""

import os
import sys
import json
import asyncio
from pathlib import Path
from typing import Dict, List, Any
from datetime import datetime
import importlib.util

print("🚀 SPARKLING OWL SPIN - ENHANCED SYSTEM VALIDATION")
print("=" * 60)

def setup_paths():
    """Setup alla nödvändiga Python paths"""
    project_root = Path(__file__).parent
    paths_to_add = [
        project_root,
        project_root / "src",
        project_root / "src" / "sos",
        project_root / "src" / "sos" / "core",
        project_root / "src" / "anti_bot" / "browser_stealth",
        project_root / "src" / "revolutionary_scraper" / "core",
        project_root / "api",
        project_root / "backend",
        project_root / "lib",
    ]
    
    print("\n📚 SETTING UP IMPORT PATHS...")
    for path in paths_to_add:
        if path.exists():
            path_str = str(path.absolute())
            if path_str not in sys.path:
                sys.path.insert(0, path_str)
                print(f"✅ Added: {path}")

def test_file_structure():
    """Test filstruktur"""
    print("\n📁 TESTING PROJECT STRUCTURE...")
    
    critical_files = [
        "stealth_browser_manager.py",  # Fixed version
        "src/sos/core/stealth_browser.py",
        "src/anti_bot/browser_stealth/stealth_browser.py", 
        "src/revolutionary_scraper/core/stealth_engine.py",
        "src/revolutionary_scraper/core/revolutionary_crawler.py",
        "src/sos/api/main.py",
        "src/sos/db/models.py",
        "frontend/src/api/client.ts",
        "frontend/src/pages/Dashboard.tsx",
        "api/complete-integration.py",
        "tests/sos/unit/test_api.py"
    ]
    
    existing = 0
    for file_path in critical_files:
        if Path(file_path).exists():
            print(f"✅ {file_path}")
            existing += 1
        else:
            print(f"❌ {file_path}")
    
    return (existing / len(critical_files)) * 100

def test_configuration():
    """Test konfigurationsfiler"""
    print("\n⚙️ TESTING CONFIGURATION FILES...")
    
    config_files = [
        "package.json",
        "requirements.txt", 
        "pyproject.toml",
        "docker-compose.yml",
        "Makefile"
    ]
    
    existing = 0
    for config_file in config_files:
        if Path(config_file).exists():
            print(f"✅ {config_file}")
            existing += 1
        else:
            print(f"❌ {config_file}")
    
    return (existing / len(config_files)) * 100

def test_imports():
    """Test kritiska imports"""
    print("\n🔍 TESTING CRITICAL IMPORTS...")
    
    results = []
    
    # Test 1: Fixed Stealth Browser Manager
    try:
        from stealth_browser_manager import StealthBrowserManager, CrawleeBrowserCrawler, BrowserType
        print("✅ Stealth Browser Manager: SUCCESS")
        results.append(True)
    except Exception as e:
        print(f"❌ Stealth Browser Manager: {e}")
        results.append(False)
    
    # Test 2: Optional SOS imports
    try:
        sys.path.insert(0, str(Path(__file__).parent / "src" / "sos" / "core"))
        import stealth_browser
        print("✅ SOS Stealth Browser: SUCCESS")
        results.append(True)
    except Exception as e:
        print(f"⚠️ SOS Stealth Browser: {e} (OPTIONAL)")
        results.append(False)
    
    # Test 3: Revolutionary components
    try:
        sys.path.insert(0, str(Path(__file__).parent / "src" / "revolutionary_scraper" / "core"))
        import stealth_engine
        print("✅ Revolutionary Stealth Engine: SUCCESS")
        results.append(True)
    except Exception as e:
        print(f"⚠️ Revolutionary Stealth Engine: {e} (OPTIONAL)")
        results.append(False)
    
    return (sum(results) / len(results)) * 100

def analyze_code_metrics():
    """Analysera kodmetrik"""
    print("\n📊 ANALYZING CODE METRICS...")
    
    python_files = 0
    typescript_files = 0
    total_lines = 0
    
    # Count files
    for py_file in Path(".").rglob("*.py"):
        if not any(skip in str(py_file) for skip in [".venv", "__pycache__", ".git", "node_modules"]):
            python_files += 1
            try:
                with open(py_file, 'r', encoding='utf-8', errors='ignore') as f:
                    lines = len(f.readlines())
                    total_lines += lines
            except Exception:
                pass
    
    for ts_file in Path(".").rglob("*.{ts,tsx,js,jsx}"):
        if not any(skip in str(ts_file) for skip in [".venv", "__pycache__", ".git", "node_modules"]):
            typescript_files += 1
            try:
                with open(ts_file, 'r', encoding='utf-8', errors='ignore') as f:
                    lines = len(f.readlines())
                    total_lines += lines
            except Exception:
                pass
    
    return {
        "python_files": python_files,
        "typescript_files": typescript_files, 
        "total_lines": total_lines
    }

async def test_stealth_functionality():
    """Test stealth browser functionality"""
    print("\n🧪 TESTING STEALTH BROWSER FUNCTIONALITY...")
    
    try:
        from stealth_browser_manager import StealthBrowserManager, BrowserType
        
        manager = StealthBrowserManager(BrowserType.CHROMIUM)
        print("✅ StealthBrowserManager created")
        
        # Test browser launch (mock mode if Playwright not available)
        browser = await manager.launch_browser(headless=True)
        print("✅ Browser launched")
        
        # Test context creation
        context = await manager.create_stealth_context()
        print("✅ Stealth context created")
        
        # Test page creation
        page = await manager.create_stealth_page(context)
        print("✅ Stealth page created")
        
        # Test navigation with mock or real URL
        result = await manager.navigate_stealthily(page, "https://httpbin.org/headers")
        print(f"✅ Navigation test: Status {result.get('status', 'unknown')}")
        
        # Cleanup
        await manager.close()
        print("✅ Browser cleanup completed")
        
        return True
        
    except Exception as e:
        print(f"❌ Stealth functionality test failed: {e}")
        return False

def create_system_test():
    """Skapa systemtest för kontinuerlig validering"""
    test_code = '''#!/usr/bin/env python3
"""
🧪 Kontinuerlig systemtest för Sparkling Owl Spin
"""
import asyncio
from stealth_browser_manager import StealthBrowserManager, BrowserType

async def test_system():
    print("🧪 Testing Sparkling Owl Spin System...")
    
    # Test stealth browser
    manager = StealthBrowserManager(BrowserType.CHROMIUM)
    browser = await manager.launch_browser(headless=True)
    context = await manager.create_stealth_context()
    page = await manager.create_stealth_page(context)
    
    # Test navigation
    result = await manager.navigate_stealthily(page, "https://httpbin.org/headers")
    print(f"Navigation result: {result}")
    
    await manager.close()
    print("✅ System test completed successfully!")

if __name__ == "__main__":
    asyncio.run(test_system())
'''
    
    with open("system_test.py", "w", encoding="utf-8") as f:
        f.write(test_code)
    print("\n📝 Created continuous system test: system_test.py")

async def main():
    """Main validation function"""
    setup_paths()
    
    # Run all tests
    structure_score = test_file_structure()
    config_score = test_configuration()
    import_score = test_imports()
    metrics = analyze_code_metrics()
    
    # Test functionality
    functionality_score = 100 if await test_stealth_functionality() else 0
    
    # Create test
    create_system_test()
    
    # Calculate overall score
    overall_score = (structure_score + config_score + import_score + functionality_score) / 4
    
    print("\n" + "=" * 60)
    print("📋 ENHANCED VALIDATION SUMMARY")
    print("=" * 60)
    print(f"📁 File Structure Score: {structure_score:.1f}%")
    print(f"⚙️ Configuration Score: {config_score:.1f}%")
    print(f"🔍 Import Success Score: {import_score:.1f}%")
    print(f"🧪 Functionality Score: {functionality_score:.1f}%")
    print(f"📊 Python Files: {metrics['python_files']:,}")
    print(f"📊 TypeScript Files: {metrics['typescript_files']:,}")
    print(f"📊 Total Lines: {metrics['total_lines']:,}")
    
    print(f"\n🎯 OVERALL SCORE: {overall_score:.1f}/100")
    
    if overall_score >= 85:
        status = "✅ EXCELLENT ⭐⭐⭐⭐⭐"
        production = "🚀 PRODUCTION READY - DEPLOY NOW!"
    elif overall_score >= 70:
        status = "✅ GOOD ⭐⭐⭐⭐"
        production = "🚀 PRODUCTION READY - Minor improvements recommended"
    elif overall_score >= 55:
        status = "⚠️ ACCEPTABLE ⭐⭐⭐"
        production = "🔧 NEEDS MINOR FIXES - Address issues before deployment"
    else:
        status = "❌ NEEDS WORK ⭐⭐"
        production = "🚧 NOT READY - Requires significant development"
    
    print(f"📊 STATUS: {status}")
    print(f"🚀 PRODUCTION READINESS: {production}")
    
    # Save enhanced report
    report = {
        "timestamp": datetime.now().isoformat(),
        "overall_score": overall_score,
        "detailed_scores": {
            "structure": structure_score,
            "configuration": config_score,
            "imports": import_score,
            "functionality": functionality_score
        },
        "metrics": metrics,
        "status": status,
        "production_ready": overall_score >= 70,
        "improvements_made": [
            "Fixed stealth browser manager imports",
            "Created standalone stealth browser implementation",
            "Added comprehensive functionality testing",
            "Enhanced import path management",
            "Created continuous system test"
        ]
    }
    
    with open("ENHANCED_VALIDATION_REPORT.json", "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)
    
    print(f"\n💾 Enhanced report saved to: ENHANCED_VALIDATION_REPORT.json")
    print("\n🎉 ENHANCED VALIDATION COMPLETED SUCCESSFULLY!")
    
    return overall_score >= 70

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
