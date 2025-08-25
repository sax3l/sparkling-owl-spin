"""
Ultimate Scraping System - Complete Integration Test
Testar integration av alla 6 repository-integrations tillsammans
"""

import asyncio
import time
import json
import requests
from typing import Dict, Any


async def test_complete_integration():
    """
    Komplett test av alla integrationer i Ultimate Scraping System
    """
    
    print("🌟 ULTIMATE SCRAPING SYSTEM - COMPLETE INTEGRATION TEST")
    print("=" * 80)
    
    # Test Results Tracking
    test_results = {
        'total_tests': 0,
        'passed_tests': 0,
        'failed_tests': 0,
        'integrations': {}
    }
    
    # Test 1: Enhanced Stealth Integration
    print("\n1. 🥷 Testing Enhanced Stealth Integration")
    print("-" * 40)
    
    try:
        from enhanced_stealth_integration import EnhancedStealthManager, EnhancedStealthConfig
        
        stealth_config = EnhancedStealthConfig(
            randomize_canvas=True,
            block_webrtc=True,
            randomize_audio=True
        )
        stealth_manager = EnhancedStealthManager(stealth_config)
        
        print("   ✅ Enhanced Stealth: Initialized successfully")
        test_results['integrations']['stealth'] = {'status': 'success', 'features': ['canvas', 'webrtc', 'audio']}
        test_results['passed_tests'] += 1
        
    except Exception as e:
        print(f"   ❌ Enhanced Stealth: Failed - {e}")
        test_results['integrations']['stealth'] = {'status': 'failed', 'error': str(e)}
        test_results['failed_tests'] += 1
        
    test_results['total_tests'] += 1
    
    # Test 2: Advanced Fake-UserAgent Integration
    print("\n2. 🌐 Testing Advanced Fake-UserAgent Integration")
    print("-" * 40)
    
    try:
        from advanced_fake_useragent_integration import AdvancedUserAgentManager, UserAgentConfig
        
        ua_config = UserAgentConfig(
            browsers=['chrome', 'firefox', 'safari'],
            platforms=['windows', 'mac', 'linux'],
            cache_enabled=True
        )
        ua_manager = AdvancedUserAgentManager(ua_config)
        
        # Test user-agent generation
        ua_data = ua_manager.get_random_user_agent()
        print(f"   ✅ User-Agent Generated: {ua_data.user_agent[:60]}...")
        print(f"   📊 Browser: {ua_data.browser}, OS: {ua_data.os}")
        
        # Test statistics
        stats = ua_manager.get_statistics()
        print(f"   📈 Cache Hit Rate: {stats.get('cache_hit_rate', 0):.1f}%")
        
        test_results['integrations']['fake_useragent'] = {
            'status': 'success',
            'user_agent': ua_data.user_agent,
            'cache_hit_rate': stats.get('cache_hit_rate', 0)
        }
        test_results['passed_tests'] += 1
        
    except Exception as e:
        print(f"   ❌ Fake-UserAgent: Failed - {e}")
        test_results['integrations']['fake_useragent'] = {'status': 'failed', 'error': str(e)}
        test_results['failed_tests'] += 1
        
    test_results['total_tests'] += 1
    
    # Test 3: Advanced IP-Rotation Integration
    print("\n3. 🌍 Testing Advanced IP-Rotation Integration")
    print("-" * 40)
    
    try:
        from advanced_ip_rotation_integration import StealthIPRotator, IPRotationConfig
        
        ip_config = IPRotationConfig(
            rotation_strategy="weighted",
            rotation_interval=5,
            enable_fallback_proxies=False  # Disable för test
        )
        
        ip_rotator = StealthIPRotator("https://httpbin.org", **ip_config.__dict__)
        
        print("   ✅ IP-Rotation: Initialized successfully")
        
        # Test statistics
        stats = ip_rotator.get_statistics()
        print(f"   📊 Rotation Strategy: {ip_config.rotation_strategy}")
        print(f"   🔄 Rotation Interval: {ip_config.rotation_interval}")
        
        test_results['integrations']['ip_rotation'] = {
            'status': 'success',
            'strategy': ip_config.rotation_strategy,
            'interval': ip_config.rotation_interval
        }
        test_results['passed_tests'] += 1
        
    except Exception as e:
        print(f"   ❌ IP-Rotation: Failed - {e}")
        test_results['integrations']['ip_rotation'] = {'status': 'failed', 'error': str(e)}
        test_results['failed_tests'] += 1
        
    test_results['total_tests'] += 1
    
    # Test 4: Combined Integration Test
    print("\n4. 🚀 Testing Combined Integration")
    print("-" * 40)
    
    try:
        # Skapa kombinerad session med alla integrations
        session = requests.Session()
        
        # Lägg till User-Agent från fake-useragent integration
        if 'fake_useragent' in test_results['integrations'] and test_results['integrations']['fake_useragent']['status'] == 'success':
            ua_data = ua_manager.get_random_user_agent()
            session.headers.update(ua_data.headers)
            print(f"   ✅ Applied User-Agent: {ua_data.browser} on {ua_data.os}")
        
        # Test combined request
        print("   🎯 Making test request with combined integrations...")
        
        response = session.get("https://httpbin.org/headers", timeout=10)
        
        if response.ok:
            headers_data = response.json().get('headers', {})
            detected_ua = headers_data.get('User-Agent', '')
            
            print(f"   ✅ Request successful: {response.status_code}")
            print(f"   📱 Detected User-Agent: {detected_ua[:50]}...")
            
            test_results['integrations']['combined'] = {
                'status': 'success',
                'response_code': response.status_code,
                'user_agent_applied': bool(detected_ua)
            }
            test_results['passed_tests'] += 1
        else:
            raise Exception(f"Request failed with status {response.status_code}")
            
    except Exception as e:
        print(f"   ❌ Combined Integration: Failed - {e}")
        test_results['integrations']['combined'] = {'status': 'failed', 'error': str(e)}
        test_results['failed_tests'] += 1
        
    test_results['total_tests'] += 1
    
    # Test 5: Repository Integration Coverage
    print("\n5. 📦 Testing Repository Integration Coverage")
    print("-" * 40)
    
    expected_integrations = [
        'selenium-stealth',
        'scrapy-playwright',
        'requests-html',
        'fake-useragent',
        'requests-ip-rotator',
        'enhanced-stealth-base'
    ]
    
    available_integrations = []
    
    # Check each integration
    integration_checks = [
        ('selenium-stealth', 'selenium_stealth_integration'),
        ('scrapy-playwright', 'scrapy_playwright_integration'),
        ('requests-html', 'requests_html_integration'),
        ('fake-useragent', 'advanced_fake_useragent_integration'),
        ('requests-ip-rotator', 'advanced_ip_rotation_integration'),
        ('enhanced-stealth-base', 'enhanced_stealth_integration')
    ]
    
    for repo_name, module_name in integration_checks:
        try:
            __import__(module_name)
            print(f"   ✅ {repo_name}: Integration available")
            available_integrations.append(repo_name)
        except ImportError:
            print(f"   ⚠️  {repo_name}: Integration file not found")
        except Exception as e:
            print(f"   ❌ {repo_name}: Import error - {e}")
    
    coverage_percentage = (len(available_integrations) / len(expected_integrations)) * 100
    print(f"   📊 Integration Coverage: {len(available_integrations)}/{len(expected_integrations)} ({coverage_percentage:.1f}%)")
    
    test_results['integrations']['coverage'] = {
        'expected': len(expected_integrations),
        'available': len(available_integrations),
        'percentage': coverage_percentage,
        'available_list': available_integrations
    }
    
    if coverage_percentage >= 50:
        test_results['passed_tests'] += 1
    else:
        test_results['failed_tests'] += 1
        
    test_results['total_tests'] += 1
    
    # Test Results Summary
    print("\n" + "=" * 80)
    print("📊 ULTIMATE SCRAPING SYSTEM - TEST SUMMARY")
    print("=" * 80)
    
    success_rate = (test_results['passed_tests'] / test_results['total_tests']) * 100
    
    print(f"🎯 Overall Results:")
    print(f"   • Total Tests: {test_results['total_tests']}")
    print(f"   • Passed: {test_results['passed_tests']} ✅")
    print(f"   • Failed: {test_results['failed_tests']} ❌")
    print(f"   • Success Rate: {success_rate:.1f}%")
    
    print(f"\n🔧 Integration Status:")
    for integration, data in test_results['integrations'].items():
        if isinstance(data, dict) and 'status' in data:
            status_icon = "✅" if data['status'] == 'success' else "❌"
            print(f"   {status_icon} {integration.replace('_', '-').title()}")
        else:
            print(f"   ℹ️  {integration.replace('_', '-').title()}: Special case")
    
    print(f"\n🌟 Ultimate Scraping System Status:")
    if success_rate >= 80:
        print("   🎉 EXCELLENT - System is highly functional!")
    elif success_rate >= 60:
        print("   👍 GOOD - System is functional with some limitations")
    elif success_rate >= 40:
        print("   ⚠️  MODERATE - System needs attention")
    else:
        print("   ❌ POOR - System requires significant fixes")
    
    # Detailed integration info
    print(f"\n📋 Integration Details:")
    
    if 'fake_useragent' in test_results['integrations']:
        fa_data = test_results['integrations']['fake_useragent']
        if fa_data['status'] == 'success':
            print(f"   🌐 User-Agent Rotation: Active (Cache: {fa_data.get('cache_hit_rate', 0):.1f}%)")
    
    if 'ip_rotation' in test_results['integrations']:
        ip_data = test_results['integrations']['ip_rotation']
        if ip_data['status'] == 'success':
            print(f"   🌍 IP Rotation: Active (Strategy: {ip_data.get('strategy', 'unknown')})")
    
    if 'stealth' in test_results['integrations']:
        stealth_data = test_results['integrations']['stealth']
        if stealth_data['status'] == 'success':
            features = ', '.join(stealth_data.get('features', []))
            print(f"   🥷 Stealth Features: Active ({features})")
    
    if 'coverage' in test_results['integrations']:
        cov_data = test_results['integrations']['coverage']
        print(f"   📦 Repository Coverage: {cov_data['available']}/{cov_data['expected']} ({cov_data['percentage']:.1f}%)")
    
    # Save results
    with open('integration_test_results.json', 'w') as f:
        json.dump(test_results, f, indent=2)
        
    print(f"\n💾 Test results saved to: integration_test_results.json")
    
    return test_results


async def demo_integrated_scraping():
    """
    Demo av integrerat scraping med alla system
    """
    
    print("\n🎬 INTEGRATED SCRAPING DEMO")
    print("=" * 50)
    
    try:
        # Import alla tillgängliga integrations
        from advanced_fake_useragent_integration import AdvancedUserAgentManager
        from enhanced_stealth_integration import EnhancedStealthManager
        
        # Skapa managers
        ua_manager = AdvancedUserAgentManager()
        stealth_manager = EnhancedStealthManager()
        
        print("🔧 Creating integrated scraping session...")
        
        # Skapa session med alla integrations
        session = requests.Session()
        
        # User-Agent rotation
        ua_data = ua_manager.get_random_user_agent()
        session.headers.update(ua_data.headers)
        
        print(f"   🌐 User-Agent: {ua_data.browser} on {ua_data.os}")
        
        # Test targets
        test_urls = [
            "https://httpbin.org/headers",
            "https://httpbin.org/user-agent", 
            "https://httpbin.org/ip"
        ]
        
        print(f"\n🎯 Testing {len(test_urls)} endpoints...")
        
        for i, url in enumerate(test_urls, 1):
            try:
                print(f"\n   Request {i}: {url}")
                
                response = session.get(url, timeout=10)
                
                if response.ok:
                    data = response.json()
                    
                    if 'headers' in data:
                        headers = data['headers']
                        print(f"     ✅ Status: {response.status_code}")
                        print(f"     📱 UA: {headers.get('User-Agent', 'None')[:40]}...")
                        print(f"     🌐 Host: {headers.get('Host', 'None')}")
                    elif 'user-agent' in data:
                        print(f"     ✅ Status: {response.status_code}")
                        print(f"     📱 Detected: {data['user-agent'][:40]}...")
                    elif 'origin' in data:
                        print(f"     ✅ Status: {response.status_code}")
                        print(f"     🌍 Origin IP: {data['origin']}")
                    else:
                        print(f"     ✅ Status: {response.status_code}")
                        
                else:
                    print(f"     ❌ Failed: {response.status_code}")
                    
            except Exception as e:
                print(f"     ❌ Error: {e}")
                
        # Statistics
        ua_stats = ua_manager.get_statistics()
        print(f"\n📊 Session Statistics:")
        print(f"   • User-Agent Cache Hit Rate: {ua_stats.get('cache_hit_rate', 0):.1f}%")
        print(f"   • Requests Made: {len(test_urls)}")
        print(f"   • Browser: {ua_data.browser}")
        print(f"   • Platform: {ua_data.os}")
        
    except Exception as e:
        print(f"❌ Demo failed: {e}")


if __name__ == "__main__":
    # Run complete integration test
    test_results = asyncio.run(test_complete_integration())
    
    # Run scraping demo if basic tests pass
    if test_results['passed_tests'] >= 2:
        asyncio.run(demo_integrated_scraping())
    else:
        print("\n⚠️  Skipping integrated demo due to test failures")
