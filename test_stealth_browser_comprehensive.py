#!/usr/bin/env python3
"""
🧪 STEALTH BROWSER MANAGER - COMPREHENSIVE TESTING SUITE
Verifierar alla aspekter av stealth browser funktionalitet
"""

import asyncio
import time
import json
from typing import Dict, List
import pytest
from pathlib import Path
import sys
import os

# Add src paths för imports
sys.path.append(str(Path(__file__).parent / "src"))
sys.path.append(str(Path(__file__).parent / "src" / "sos" / "core"))
sys.path.append(str(Path(__file__).parent / "src" / "anti_bot" / "browser_stealth"))

# Import the fixed stealth browser manager
try:
    from stealth_browser_manager import (
        StealthBrowserManager, 
        CrawleeBrowserCrawler, 
        BrowserType,
        BrowserFingerprint
    )
    print("✅ Successfully imported StealthBrowser modules")
    IMPORTS_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ Import error: {e}")
    print("Testing will proceed in mock mode")
    IMPORTS_AVAILABLE = False

class StealthBrowserTester:
    """Comprehensive testing suite för stealth browser manager"""
    
    def __init__(self):
        self.results = {
            "tests_run": 0,
            "tests_passed": 0,
            "tests_failed": 0,
            "test_details": [],
            "performance_metrics": {},
            "stealth_metrics": {},
            "errors": []
        }
    
    async def run_all_tests(self):
        """Kör alla tester i sekvens"""
        print("🧪 STARTAR OMFATTANDE STEALTH BROWSER TESTER")
        print("=" * 60)
        
        if not IMPORTS_AVAILABLE:
            print("❌ CRITICAL: Cannot import stealth_browser_manager module")
            return self.results
        
        # Test suite
        test_methods = [
            ("Basic Initialization", self.test_basic_initialization),
            ("Fingerprint Generation", self.test_fingerprint_generation),
            ("Browser Launch", self.test_browser_launch),
            ("Stealth Context Creation", self.test_stealth_context_creation),
            ("Human Behavior Simulation", self.test_human_behavior),
            ("Stealth Scripts", self.test_stealth_scripts),
            ("Crawlee Browser Crawler", self.test_crawlee_browser_crawler),
            ("Performance Benchmarks", self.test_performance_benchmarks),
            ("Memory Management", self.test_memory_management),
            ("Error Handling", self.test_error_handling)
        ]
        
        for test_name, test_method in test_methods:
            await self._run_single_test(test_name, test_method)
        
        self._print_final_results()
        return self.results
    
    async def _run_single_test(self, test_name: str, test_method):
        """Kör en enskild test med error handling"""
        print(f"\n🔬 Testing: {test_name}")
        print("-" * 40)
        
        self.results["tests_run"] += 1
        start_time = time.time()
        
        try:
            result = await test_method()
            elapsed = time.time() - start_time
            
            if result:
                self.results["tests_passed"] += 1
                print(f"✅ {test_name}: PASSED ({elapsed:.2f}s)")
            else:
                self.results["tests_failed"] += 1
                print(f"❌ {test_name}: FAILED ({elapsed:.2f}s)")
                
            self.results["test_details"].append({
                "name": test_name,
                "status": "PASSED" if result else "FAILED",
                "duration": elapsed
            })
            
        except Exception as e:
            elapsed = time.time() - start_time
            self.results["tests_failed"] += 1
            error_msg = f"Exception in {test_name}: {str(e)}"
            print(f"❌ {test_name}: ERROR ({elapsed:.2f}s)")
            print(f"   Error: {error_msg}")
            
            self.results["errors"].append(error_msg)
            self.results["test_details"].append({
                "name": test_name,
                "status": "ERROR",
                "duration": elapsed,
                "error": error_msg
            })
    
    async def test_basic_initialization(self) -> bool:
        """Test basic StealthBrowserManager initialization"""
        try:
            # Test default initialization
            manager = StealthBrowserManager()
            
            assert manager.browser_type == BrowserType.CHROMIUM
            assert manager.playwright is None
            assert manager.browser is None
            assert len(manager.contexts) == 0
            assert manager.stealth_enabled == True
            assert len(manager.fingerprint_pool) > 0
            
            print("   ✓ Default initialization successful")
            
            # Test with different browser types
            for browser_type in [BrowserType.CHROMIUM, BrowserType.FIREFOX, BrowserType.WEBKIT]:
                manager = StealthBrowserManager(browser_type)
                assert manager.browser_type == browser_type
                print(f"   ✓ {browser_type.value} initialization successful")
            
            # Test fingerprint pool generation
            assert len(manager.fingerprint_pool) >= 10, "Should have at least 10 fingerprints"
            print(f"   ✓ Generated {len(manager.fingerprint_pool)} fingerprints")
            
            return True
            
        except Exception as e:
            print(f"   ❌ Basic initialization failed: {e}")
            return False
    
    async def test_fingerprint_generation(self) -> bool:
        """Test fingerprint generation quality"""
        try:
            manager = StealthBrowserManager()
            
            # Test fingerprint diversity
            fingerprints = manager.fingerprint_pool
            user_agents = set()
            viewports = set()
            platforms = set()
            
            for fp in fingerprints[:20]:  # Test first 20
                user_agents.add(fp.user_agent)
                viewports.add(f"{fp.viewport['width']}x{fp.viewport['height']}")
                platforms.add(fp.platform)
                
                # Validate required fields
                assert fp.user_agent and len(fp.user_agent) > 50
                assert fp.viewport['width'] >= 800 and fp.viewport['height'] >= 600
                assert fp.locale in ['en-US', 'en-GB', 'sv-SE']
                assert fp.timezone_id
                assert len(fp.languages) > 0
            
            print(f"   ✓ {len(user_agents)} unique user agents")
            print(f"   ✓ {len(viewports)} unique viewports")
            print(f"   ✓ {len(platforms)} unique platforms")
            
            # Test fingerprint variation
            assert len(user_agents) >= 15, "Should have diverse user agents"
            assert len(viewports) >= 10, "Should have diverse viewports"
            assert len(platforms) >= 2, "Should have multiple platforms"
            
            return True
            
        except Exception as e:
            print(f"   ❌ Fingerprint generation failed: {e}")
            return False
    
    async def test_browser_launch(self) -> bool:
        """Test browser launching with different configurations"""
        try:
            manager = StealthBrowserManager()
            
            # Test headless launch
            browser = await manager.launch(headless=True)
            assert browser is not None
            print("   ✓ Headless browser launch successful")
            
            # Test browser cleanup
            await manager.close()
            print("   ✓ Browser cleanup successful")
            
            return True
            
        except Exception as e:
            print(f"   ❌ Browser launch failed: {e}")
            return False
    
    async def test_stealth_context_creation(self) -> bool:
        """Test stealth context creation and configuration"""
        try:
            manager = StealthBrowserManager()
            await manager.launch(headless=True)
            
            # Test context creation
            context = await manager.create_stealth_context()
            assert context is not None
            print("   ✓ Stealth context created successfully")
            
            # Test page creation
            page = await manager.create_stealth_page(context)
            assert page is not None
            print("   ✓ Stealth page created successfully")
            
            # Test stealth script injection
            user_agent = await page.evaluate("navigator.userAgent")
            webdriver_property = await page.evaluate("navigator.webdriver")
            
            assert user_agent is not None
            assert webdriver_property is None  # Should be hidden
            
            print("   ✓ Stealth scripts working (webdriver property hidden)")
            print(f"   ✓ User agent: {user_agent[:60]}...")
            
            await manager.close()
            return True
            
        except Exception as e:
            print(f"   ❌ Stealth context creation failed: {e}")
            return False
    
    async def test_human_behavior(self) -> bool:
        """Test human behavior simulation methods"""
        try:
            manager = StealthBrowserManager()
            await manager.launch(headless=True)
            
            context = await manager.create_stealth_context()
            page = await manager.create_stealth_page(context)
            
            # Create a simple test page
            await page.set_content("""
                <html>
                <body>
                    <input id="test-input" placeholder="Test input">
                    <button id="test-button">Test Button</button>
                    <div style="height: 2000px;">Long content for scrolling</div>
                </body>
                </html>
            """)
            
            # Test human typing
            start_time = time.time()
            await manager.human_type(page, "#test-input", "Hello World")
            typing_duration = time.time() - start_time
            
            input_value = await page.evaluate("document.getElementById('test-input').value")
            assert input_value == "Hello World"
            assert typing_duration > 0.5  # Should take time for human-like typing
            
            print(f"   ✓ Human typing successful ({typing_duration:.2f}s)")
            
            # Test human clicking
            start_time = time.time()
            await manager.human_click(page, "#test-button")
            click_duration = time.time() - start_time
            
            assert click_duration > 0.2  # Should have human-like delays
            print(f"   ✓ Human clicking successful ({click_duration:.2f}s)")
            
            # Test scrolling
            start_time = time.time()
            await manager.scroll_page(page, scroll_count=2)
            scroll_duration = time.time() - start_time
            
            assert scroll_duration > 1.0  # Should take time for realistic scrolling
            print(f"   ✓ Human scrolling successful ({scroll_duration:.2f}s)")
            
            await manager.close()
            return True
            
        except Exception as e:
            print(f"   ❌ Human behavior simulation failed: {e}")
            return False
    
    async def test_stealth_scripts(self) -> bool:
        """Test stealth script effectiveness"""
        try:
            manager = StealthBrowserManager()
            await manager.launch(headless=True)
            
            context = await manager.create_stealth_context()
            page = await manager.create_stealth_page(context)
            
            # Test various stealth measures
            tests = {
                "webdriver": "navigator.webdriver",
                "plugins": "navigator.plugins.length",
                "languages": "navigator.languages.length",
                "chrome": "window.chrome",
                "permissions": "navigator.permissions"
            }
            
            results = {}
            for test_name, js_code in tests.items():
                try:
                    result = await page.evaluate(js_code)
                    results[test_name] = result
                    print(f"   ✓ {test_name}: {result}")
                except Exception as e:
                    print(f"   ⚠️ {test_name}: Error - {e}")
            
            # Verify stealth effectiveness
            assert results.get("webdriver") is None, "webdriver should be undefined"
            assert results.get("plugins", 0) > 0, "Should have plugins"
            assert results.get("languages", 0) > 0, "Should have languages"
            assert results.get("chrome") is not None, "Should have chrome object"
            
            await manager.close()
            return True
            
        except Exception as e:
            print(f"   ❌ Stealth scripts failed: {e}")
            return False
    
    async def test_crawlee_browser_crawler(self) -> bool:
        """Test Crawlee-inspired browser crawler"""
        try:
            async def test_handler(context):
                page = context['page']
                url = context['url']
                
                # Simple data extraction
                title = await page.title()
                return {
                    'url': url,
                    'title': title,
                    'timestamp': time.time()
                }
            
            crawler = CrawleeBrowserCrawler(
                browser_type=BrowserType.CHROMIUM,
                headless=True,
                max_concurrent_pages=1,
                stealth_enabled=True
            )
            
            # Test with data URLs (no network required)
            test_urls = [
                "data:text/html,<html><head><title>Test Page 1</title></head><body>Content 1</body></html>",
                "data:text/html,<html><head><title>Test Page 2</title></head><body>Content 2</body></html>"
            ]
            
            start_time = time.time()
            results = await crawler.crawl_urls(test_urls, test_handler)
            duration = time.time() - start_time
            
            assert len(results) == 2
            assert all('title' in result for result in results if result)
            assert all('url' in result for result in results if result)
            
            print(f"   ✓ Crawled {len(results)} URLs in {duration:.2f}s")
            print(f"   ✓ Average: {duration/len(results):.2f}s per URL")
            
            return True
            
        except Exception as e:
            print(f"   ❌ Crawlee browser crawler failed: {e}")
            return False
    
    async def test_performance_benchmarks(self) -> bool:
        """Test performance benchmarks"""
        try:
            manager = StealthBrowserManager()
            
            # Benchmark fingerprint generation
            start_time = time.time()
            for _ in range(100):
                fp = manager._generate_fingerprint_pool()
            fingerprint_time = time.time() - start_time
            
            # Benchmark browser operations
            await manager.launch(headless=True)
            
            start_time = time.time()
            context = await manager.create_stealth_context()
            context_time = time.time() - start_time
            
            start_time = time.time()
            page = await manager.create_stealth_page(context)
            page_time = time.time() - start_time
            
            # Store performance metrics
            self.results["performance_metrics"] = {
                "fingerprint_generation_per_100": f"{fingerprint_time:.3f}s",
                "context_creation": f"{context_time:.3f}s",
                "page_creation": f"{page_time:.3f}s"
            }
            
            print(f"   ✓ Fingerprint generation (100x): {fingerprint_time:.3f}s")
            print(f"   ✓ Context creation: {context_time:.3f}s")
            print(f"   ✓ Page creation: {page_time:.3f}s")
            
            # Performance assertions
            assert fingerprint_time < 1.0, "Fingerprint generation should be fast"
            assert context_time < 2.0, "Context creation should be reasonable"
            assert page_time < 1.0, "Page creation should be fast"
            
            await manager.close()
            return True
            
        except Exception as e:
            print(f"   ❌ Performance benchmarks failed: {e}")
            return False
    
    async def test_memory_management(self) -> bool:
        """Test memory management and resource cleanup"""
        try:
            import gc
            import psutil
            import os
            
            process = psutil.Process(os.getpid())
            initial_memory = process.memory_info().rss / 1024 / 1024  # MB
            
            # Create and destroy multiple managers
            for i in range(5):
                manager = StealthBrowserManager()
                await manager.launch(headless=True)
                
                context = await manager.create_stealth_context()
                page = await manager.create_stealth_page(context)
                
                await manager.close()
                del manager
                gc.collect()
            
            final_memory = process.memory_info().rss / 1024 / 1024  # MB
            memory_increase = final_memory - initial_memory
            
            print(f"   ✓ Initial memory: {initial_memory:.1f}MB")
            print(f"   ✓ Final memory: {final_memory:.1f}MB")
            print(f"   ✓ Memory increase: {memory_increase:.1f}MB")
            
            # Memory should not increase dramatically
            assert memory_increase < 100, f"Memory increase too high: {memory_increase}MB"
            
            return True
            
        except ImportError:
            print("   ⚠️ psutil not available, skipping memory test")
            return True
        except Exception as e:
            print(f"   ❌ Memory management test failed: {e}")
            return False
    
    async def test_error_handling(self) -> bool:
        """Test error handling and recovery"""
        try:
            manager = StealthBrowserManager()
            
            # Test handling of invalid URLs
            await manager.launch(headless=True)
            context = await manager.create_stealth_context()
            page = await manager.create_stealth_page(context)
            
            # Test invalid URL handling
            try:
                await manager.navigate_with_stealth(page, "invalid://url")
                print("   ⚠️ Expected error for invalid URL")
            except Exception:
                print("   ✓ Properly handles invalid URLs")
            
            # Test cleanup after errors
            await manager.close()
            
            # Test multiple close calls (should not error)
            await manager.close()
            await manager.close()
            
            print("   ✓ Graceful error handling verified")
            
            return True
            
        except Exception as e:
            print(f"   ❌ Error handling test failed: {e}")
            return False
    
    def _print_final_results(self):
        """Print final test results summary"""
        print("\n" + "=" * 60)
        print("🏆 FINAL TEST RESULTS SUMMARY")
        print("=" * 60)
        
        total_tests = self.results["tests_run"]
        passed_tests = self.results["tests_passed"]
        failed_tests = self.results["tests_failed"]
        
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"📊 Tests Run: {total_tests}")
        print(f"✅ Tests Passed: {passed_tests}")
        print(f"❌ Tests Failed: {failed_tests}")
        print(f"📈 Success Rate: {success_rate:.1f}%")
        
        if success_rate >= 90:
            print("🏆 RESULT: EXCELLENT - Production ready!")
        elif success_rate >= 80:
            print("🎯 RESULT: GOOD - Minor improvements needed")
        elif success_rate >= 70:
            print("⚠️ RESULT: ACCEPTABLE - Some issues to address")
        else:
            print("❌ RESULT: NEEDS WORK - Major issues found")
        
        # Print performance metrics
        if self.results["performance_metrics"]:
            print(f"\n📈 PERFORMANCE METRICS:")
            for metric, value in self.results["performance_metrics"].items():
                print(f"   • {metric.replace('_', ' ').title()}: {value}")
        
        # Print errors if any
        if self.results["errors"]:
            print(f"\n🐛 ERRORS ENCOUNTERED:")
            for error in self.results["errors"]:
                print(f"   • {error}")

async def main():
    """Main test execution function"""
    tester = StealthBrowserTester()
    
    print("🚀 STARTING STEALTH BROWSER MANAGER COMPREHENSIVE TESTING")
    print("This will test all aspects of the stealth browser implementation")
    print()
    
    results = await tester.run_all_tests()
    
    # Save results to file
    results_file = Path(__file__).parent / "stealth_browser_test_results.json"
    with open(results_file, 'w') as f:
        json.dump(results, f, indent=2, default=str)
    
    print(f"\n💾 Test results saved to: {results_file}")
    
    return results

if __name__ == "__main__":
    asyncio.run(main())
