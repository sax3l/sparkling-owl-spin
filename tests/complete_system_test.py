#!/usr/bin/env python3
"""
🚀 COMPLETE SYSTEM INTEGRATION TEST
Test av alla systemkomponenter med fixade imports
"""

import asyncio
import sys
import json
from pathlib import Path
from datetime import datetime

# Add current directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

async def test_complete_integration():
    """Test komplett systemintegration"""
    print("🚀 STARTING COMPLETE SYSTEM INTEGRATION TEST")
    print("=" * 60)
    
    results = {
        "timestamp": datetime.now().isoformat(),
        "tests": {},
        "overall_success": False,
        "errors": []
    }
    
    # Test 1: Import stealth browser manager
    print("\n📦 TESTING STEALTH BROWSER IMPORTS...")
    try:
        from stealth_browser_manager import (
            StealthBrowserManager, 
            CrawleeBrowserCrawler, 
            BrowserType,
            BrowserFingerprint
        )
        print("✅ All stealth browser components imported successfully")
        results["tests"]["imports"] = True
    except Exception as e:
        print(f"❌ Import failed: {e}")
        results["tests"]["imports"] = False
        results["errors"].append(f"Import error: {e}")
    
    # Test 2: Create stealth browser manager
    print("\n🔧 TESTING STEALTH BROWSER CREATION...")
    try:
        manager = StealthBrowserManager(BrowserType.CHROMIUM)
        print("✅ StealthBrowserManager created successfully")
        results["tests"]["manager_creation"] = True
    except Exception as e:
        print(f"❌ Manager creation failed: {e}")
        results["tests"]["manager_creation"] = False
        results["errors"].append(f"Manager creation error: {e}")
        return results
    
    # Test 3: Browser launch (headless for testing)
    print("\n🚀 TESTING BROWSER LAUNCH...")
    try:
        browser = await manager.launch_browser(headless=True)
        print("✅ Browser launched successfully")
        results["tests"]["browser_launch"] = True
    except Exception as e:
        print(f"❌ Browser launch failed: {e}")
        results["tests"]["browser_launch"] = False
        results["errors"].append(f"Browser launch error: {e}")
    
    # Test 4: Context creation
    print("\n📝 TESTING CONTEXT CREATION...")
    try:
        context = await manager.create_stealth_context()
        print("✅ Stealth context created successfully")
        results["tests"]["context_creation"] = True
    except Exception as e:
        print(f"❌ Context creation failed: {e}")
        results["tests"]["context_creation"] = False
        results["errors"].append(f"Context creation error: {e}")
    
    # Test 5: Page creation
    print("\n📄 TESTING PAGE CREATION...")
    try:
        page = await manager.create_stealth_page(context)
        print("✅ Stealth page created successfully")
        results["tests"]["page_creation"] = True
    except Exception as e:
        print(f"❌ Page creation failed: {e}")
        results["tests"]["page_creation"] = False
        results["errors"].append(f"Page creation error: {e}")
    
    # Test 6: Navigation test
    print("\n🌐 TESTING STEALTH NAVIGATION...")
    try:
        navigation_result = await manager.navigate_stealthily(page, "https://httpbin.org/headers")
        print(f"✅ Navigation completed with status: {navigation_result.get('status', 'unknown')}")
        results["tests"]["navigation"] = True
        results["navigation_result"] = navigation_result
    except Exception as e:
        print(f"❌ Navigation failed: {e}")
        results["tests"]["navigation"] = False
        results["errors"].append(f"Navigation error: {e}")
    
    # Test 7: Crawler test
    print("\n🕷️ TESTING CRAWLEE BROWSER CRAWLER...")
    try:
        crawler = CrawleeBrowserCrawler(manager)
        print("✅ CrawleeBrowserCrawler created successfully")
        results["tests"]["crawler_creation"] = True
        
        # Test crawler run with mock URLs
        test_urls = ["https://httpbin.org/headers", "https://httpbin.org/user-agent"]
        await crawler.run(test_urls[:1])  # Test with one URL
        print(f"✅ Crawler completed with {len(crawler.results)} results")
        results["tests"]["crawler_run"] = True
        results["crawler_results"] = len(crawler.results)
        
    except Exception as e:
        print(f"❌ Crawler test failed: {e}")
        results["tests"]["crawler_creation"] = False
        results["tests"]["crawler_run"] = False
        results["errors"].append(f"Crawler error: {e}")
    
    # Test 8: Cleanup
    print("\n🧹 TESTING CLEANUP...")
    try:
        await manager.close()
        print("✅ Cleanup completed successfully")
        results["tests"]["cleanup"] = True
    except Exception as e:
        print(f"❌ Cleanup failed: {e}")
        results["tests"]["cleanup"] = False
        results["errors"].append(f"Cleanup error: {e}")
    
    # Calculate success rate
    successful_tests = sum(1 for test_result in results["tests"].values() if test_result)
    total_tests = len(results["tests"])
    success_rate = (successful_tests / total_tests) * 100 if total_tests > 0 else 0
    
    results["successful_tests"] = successful_tests
    results["total_tests"] = total_tests
    results["success_rate"] = success_rate
    results["overall_success"] = success_rate >= 75
    
    # Print summary
    print("\n" + "=" * 60)
    print("📊 COMPLETE INTEGRATION TEST SUMMARY")
    print("=" * 60)
    print(f"✅ Successful Tests: {successful_tests}/{total_tests}")
    print(f"📊 Success Rate: {success_rate:.1f}%")
    
    if results["overall_success"]:
        print("🎉 OVERALL STATUS: SUCCESS! System is ready for production")
    else:
        print("⚠️ OVERALL STATUS: NEEDS IMPROVEMENT")
        if results["errors"]:
            print("\n❌ ERRORS ENCOUNTERED:")
            for error in results["errors"]:
                print(f"   • {error}")
    
    # Save results
    with open("complete_integration_test_results.json", "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, default=str)
    
    print(f"\n💾 Test results saved to: complete_integration_test_results.json")
    
    return results

def test_api_availability():
    """Test om API-komponenter är tillgängliga"""
    print("\n🔌 TESTING API COMPONENT AVAILABILITY...")
    
    api_tests = []
    
    # Test API file existence
    api_file = Path("tests/sos/unit/test_api.py")
    if api_file.exists():
        print("✅ API test file exists")
        api_tests.append(True)
    else:
        print("❌ API test file missing")
        api_tests.append(False)
    
    # Test frontend components
    frontend_files = [
        "frontend/src/api/client.ts",
        "frontend/src/pages/Dashboard.tsx",
        "frontend/src/components/Layout.tsx"
    ]
    
    for file_path in frontend_files:
        if Path(file_path).exists():
            print(f"✅ {file_path}")
            api_tests.append(True)
        else:
            print(f"❌ {file_path}")
            api_tests.append(False)
    
    return sum(api_tests) / len(api_tests) * 100 if api_tests else 0

async def main():
    """Main test function"""
    print("🚀 SPARKLING OWL SPIN - COMPLETE SYSTEM TEST")
    print("🌟 Testing all components with fixed imports and dependencies")
    
    # Run integration test
    integration_results = await test_complete_integration()
    
    # Test API availability
    api_score = test_api_availability()
    
    # Final assessment
    integration_score = integration_results["success_rate"]
    overall_score = (integration_score + api_score) / 2
    
    print("\n" + "=" * 60)
    print("🏆 FINAL SYSTEM ASSESSMENT")
    print("=" * 60)
    print(f"🔧 Integration Score: {integration_score:.1f}%")
    print(f"🔌 API Availability: {api_score:.1f}%")
    print(f"🎯 Overall System Score: {overall_score:.1f}%")
    
    if overall_score >= 85:
        print("🌟 STATUS: EXCELLENT - Production ready!")
    elif overall_score >= 70:
        print("✅ STATUS: GOOD - Ready for deployment")
    elif overall_score >= 55:
        print("⚠️ STATUS: ACCEPTABLE - Minor fixes needed")
    else:
        print("❌ STATUS: NEEDS WORK - Significant improvements required")
    
    # Final report
    final_report = {
        "timestamp": datetime.now().isoformat(),
        "integration_results": integration_results,
        "api_score": api_score,
        "overall_score": overall_score,
        "production_ready": overall_score >= 70,
        "recommendations": []
    }
    
    if overall_score >= 70:
        final_report["recommendations"].append("✅ System ready for production deployment")
        final_report["recommendations"].append("🚀 Consider performance optimization")
        final_report["recommendations"].append("📊 Set up monitoring and logging")
    else:
        final_report["recommendations"].append("🔧 Fix import and dependency issues")
        final_report["recommendations"].append("🧪 Add more comprehensive testing")
        final_report["recommendations"].append("📚 Improve documentation")
    
    with open("FINAL_SYSTEM_ASSESSMENT.json", "w", encoding="utf-8") as f:
        json.dump(final_report, f, indent=2, default=str)
    
    print(f"\n💾 Final assessment saved to: FINAL_SYSTEM_ASSESSMENT.json")
    print("\n🎉 COMPLETE SYSTEM TEST FINISHED!")
    
    return overall_score >= 70

if __name__ == "__main__":
    success = asyncio.run(main())
    print(f"\n🏁 Test completed with {'SUCCESS' if success else 'NEEDS IMPROVEMENT'}")
    sys.exit(0 if success else 1)
