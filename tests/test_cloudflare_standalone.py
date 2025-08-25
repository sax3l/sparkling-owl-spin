"""
Simplified Test for Advanced Cloudflare Bypass Integration
Direct testing without full revolutionary_scraper dependencies.
"""

import sys
import time
import json
import logging
import importlib.util

def test_cloudflare_bypass_standalone():
    """Test Cloudflare bypass as standalone module."""
    print("🚀 Testing Advanced Cloudflare Bypass (Standalone)")
    print("="*60)
    
    # Try to load our module directly
    try:
        spec = importlib.util.spec_from_file_location(
            "advanced_cloudflare_bypass", 
            r"c:\Users\simon\dyad-apps\Main_crawler_project\revolutionary_scraper\integrations\advanced_cloudflare_bypass.py"
        )
        cf_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cf_module)
        
        print("✓ Module loaded successfully")
        
    except Exception as e:
        print(f"✗ Module loading failed: {e}")
        return False
    
    # Test basic functionality
    tests_passed = 0
    total_tests = 0
    
    # Test 1: Create scraper instance
    total_tests += 1
    try:
        scraper = cf_module.create_scraper(debug=True, max_retries=2)
        print("✓ Test 1: Scraper creation successful")
        tests_passed += 1
    except Exception as e:
        print(f"✗ Test 1 failed: {e}")
        return False
    
    # Test 2: Basic HTTP request
    total_tests += 1
    try:
        response = scraper.get('https://httpbin.org/get', timeout=10)
        if response.status_code == 200:
            print(f"✓ Test 2: Basic request successful ({response.status_code})")
            tests_passed += 1
        else:
            print(f"⚠ Test 2: Unexpected status {response.status_code}")
    except Exception as e:
        print(f"✗ Test 2 failed: {e}")
    
    # Test 3: User agent handling
    total_tests += 1
    try:
        response = scraper.get('https://httpbin.org/headers', timeout=10)
        if response.status_code == 200:
            headers = response.json().get('headers', {})
            user_agent = headers.get('User-Agent', '')
            if 'Mozilla' in user_agent:
                print(f"✓ Test 3: User agent properly set")
                print(f"  User-Agent: {user_agent[:50]}...")
                tests_passed += 1
            else:
                print(f"⚠ Test 3: Unexpected user agent: {user_agent}")
        else:
            print(f"⚠ Test 3: Request failed with status {response.status_code}")
    except Exception as e:
        print(f"✗ Test 3 failed: {e}")
    
    # Test 4: Challenge detection (mock)
    total_tests += 1
    try:
        class MockResponse:
            def __init__(self, status_code, headers, text):
                self.status_code = status_code
                self.headers = headers
                self.text = text
        
        # Mock Cloudflare challenge response
        mock_cf_response = MockResponse(
            503,
            {'Server': 'cloudflare'},
            '''
            <form id="challenge-form" action="/cdn-cgi/l/chk_jschl">
                <input name="jschl_vc" value="test"/>
                <input name="pass" value="test"/>
            </form>
            <script>setTimeout(function(){var a={}; a.value=42;}, 4000);</script>
            '''
        )
        
        is_challenge = scraper._is_cloudflare_challenge(mock_cf_response)
        challenge_type = scraper._detect_challenge_type(mock_cf_response)
        
        if is_challenge and challenge_type == 'v1':
            print(f"✓ Test 4: Challenge detection working (detected: {challenge_type})")
            tests_passed += 1
        else:
            print(f"⚠ Test 4: Challenge detection issue - detected: {is_challenge}, type: {challenge_type}")
    except Exception as e:
        print(f"✗ Test 4 failed: {e}")
    
    # Test 5: JavaScript solver (if Node.js available)
    total_tests += 1
    try:
        test_js = '''
        var document = {
            getElementById: function() { return {innerHTML: 'test'}; },
            createElement: function() { return {firstChild: {href: 'https://example.com/'}}; }
        };
        var result = 42 + 8;
        result;
        '''
        
        try:
            result = cf_module.JavaScriptSolver.solve_with_node(test_js, 'example.com', 10)
            if '50' in str(result):
                print(f"✓ Test 5: JavaScript solver working (Node.js): {result}")
                tests_passed += 1
            else:
                print(f"⚠ Test 5: Unexpected JS result: {result}")
        except Exception as e:
            print(f"⚠ Test 5: Node.js not available or failed: {e}")
            # Try js2py fallback
            try:
                result = cf_module.JavaScriptSolver.solve_with_js2py(test_js, 'example.com')
                print(f"✓ Test 5: JavaScript solver working (js2py fallback): {result}")
                tests_passed += 1
            except Exception as e2:
                print(f"⚠ Test 5: Both JS solvers failed: {e2}")
    except Exception as e:
        print(f"✗ Test 5 failed: {e}")
    
    # Test 6: Configuration options
    total_tests += 1
    try:
        custom_scraper = cf_module.create_scraper(
            debug=False,
            user_agent='Test-Bot/1.0',
            min_request_interval=0.1,
            max_retries=1,
            rotate_user_agents=False
        )
        
        # Check the User-Agent header directly from the session
        actual_ua = custom_scraper.headers.get('User-Agent')
        expected_ua = 'Test-Bot/1.0'
        
        if actual_ua == expected_ua:
            print(f"✓ Test 6: Custom configuration working")
            print(f"  Custom UA applied: {actual_ua}")
            tests_passed += 1
        else:
            print(f"⚠ Test 6: Configuration issue - Expected '{expected_ua}', got '{actual_ua}'")
        
        custom_scraper.close()
    except Exception as e:
        print(f"✗ Test 6 failed: {e}")
    
    # Test 7: Token functions (convenience methods)
    total_tests += 1
    try:
        # Test with a site that will return cookies (even if not CF)
        test_url = 'https://httpbin.org/cookies/set/test/value'
        
        cookies, user_agent = cf_module.get_tokens(test_url)
        cookie_string, ua2 = cf_module.get_cookie_string(test_url)
        
        print(f"✓ Test 7: Token extraction functions working")
        print(f"  Cookies found: {len(cookies)} cookies")
        print(f"  Cookie string length: {len(cookie_string)}")
        tests_passed += 1
        
    except Exception as e:
        print(f"✗ Test 7 failed: {e}")
    
    # Test 8: Integration class
    total_tests += 1
    try:
        integration = cf_module.CloudflareBypassIntegration({
            'debug': False,
            'max_retries': 1
        })
        
        if integration.initialize():
            capabilities = integration.get_capabilities()
            session = integration.get_session()
            
            if capabilities and session:
                print(f"✓ Test 8: Integration class working")
                print(f"  Features: {len(capabilities.get('features', []))}")
                print(f"  Challenge types: {capabilities.get('challenge_types', [])}")
                tests_passed += 1
            else:
                print(f"⚠ Test 8: Integration class incomplete")
        else:
            print(f"⚠ Test 8: Integration initialization failed")
    except Exception as e:
        print(f"✗ Test 8 failed: {e}")
    
    # Close main scraper
    try:
        scraper.close()
    except:
        pass
    
    # Summary
    success_rate = (tests_passed / total_tests) * 100
    print(f"\n{'='*60}")
    print(f"📊 TEST RESULTS SUMMARY")
    print(f"{'='*60}")
    print(f"Tests Passed: {tests_passed}/{total_tests}")
    print(f"Success Rate: {success_rate:.1f}%")
    
    if success_rate >= 80:
        print(f"🎉 EXCELLENT! Cloudflare bypass integration is working well.")
        status = "EXCELLENT"
    elif success_rate >= 60:
        print(f"✅ GOOD! Integration is functional with minor limitations.")  
        status = "GOOD"
    else:
        print(f"⚠️  NEEDS WORK! Several tests failed, requires attention.")
        status = "NEEDS_WORK"
    
    print(f"Status: {status}")
    print(f"{'='*60}")
    
    return success_rate >= 60

def test_dependencies():
    """Check what optional dependencies are available."""
    print("\n🔍 Checking Optional Dependencies:")
    print("-" * 40)
    
    dependencies = {
        'selenium': 'Browser automation support',
        'undetected_chromedriver': 'Advanced Chrome stealth',
        'js2py': 'JavaScript execution fallback',
        'requests': 'HTTP client (required)',
    }
    
    available = {}
    for dep, description in dependencies.items():
        try:
            __import__(dep)
            available[dep] = True
            print(f"✓ {dep}: Available - {description}")
        except ImportError:
            available[dep] = False  
            print(f"✗ {dep}: Missing - {description}")
    
    # Check for Node.js
    try:
        import subprocess
        result = subprocess.run(['node', '--version'], capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            available['nodejs'] = True
            print(f"✓ Node.js: Available - {result.stdout.strip()}")
        else:
            available['nodejs'] = False
            print(f"✗ Node.js: Not working")
    except Exception:
        available['nodejs'] = False
        print(f"✗ Node.js: Not found")
    
    print(f"\nDependency Summary: {sum(available.values())}/{len(available)} available")
    
    return available

def main():
    """Main test execution."""
    print("🌟 Advanced Cloudflare Bypass - Standalone Test Suite")
    print("=" * 70)
    
    # Check dependencies first
    deps = test_dependencies()
    
    # Run main tests
    success = test_cloudflare_bypass_standalone()
    
    # Additional info
    print(f"\n📋 Additional Information:")
    print(f"   • This integration supports multiple bypass methods")
    print(f"   • JavaScript challenges can be solved with Node.js or js2py")  
    print(f"   • Browser automation available if Selenium is installed")
    print(f"   • FlareSolverr proxy support for complex challenges")
    print(f"   • Multiple Cloudflare challenge versions supported (v1, v2, v3, Turnstile)")
    
    if success:
        print(f"\n✅ Integration is ready for use in the Revolutionary Scraper system!")
    else:
        print(f"\n❌ Integration needs attention before production use.")
    
    return 0 if success else 1

if __name__ == "__main__":
    import warnings
    warnings.filterwarnings("ignore", category=DeprecationWarning)
    
    sys.exit(main())
