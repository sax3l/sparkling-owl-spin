#!/usr/bin/env python3
"""
GitHub Repository Adapter Integration Tests - Revolutionary Ultimate System v4.0
Comprehensive tests for all GitHub repository integrations
"""

import asyncio
import logging
import time
import json
from pathlib import Path
from typing import Dict, Any, List, Optional
import sys
import os

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from revolutionary_scraper.adapters import (
    get_global_registry, 
    register_github_adapters,
    get_page_with_best_method,
    extract_content_with_best_method,
    discover_urls_with_best_method
)

logger = logging.getLogger(__name__)

class GitHubAdapterTester:
    """Comprehensive tester for all GitHub repository adapters"""
    
    def __init__(self):
        self.registry = get_global_registry()
        self.test_results = {}
        self.test_urls = [
            'https://httpbin.org/get',  # Simple test
            'https://example.com',      # Basic content
            'https://httpbin.org/delay/2',  # Timeout test
        ]
        
    async def run_all_tests(self) -> Dict[str, Any]:
        """Run comprehensive tests for all adapters"""
        
        logger.info("🧪 Starting GitHub repository adapter integration tests")
        start_time = time.time()
        
        # Initialize registry
        await self._initialize_registry()
        
        # Test individual adapters
        await self._test_individual_adapters()
        
        # Test high-level interfaces
        await self._test_high_level_interfaces()
        
        # Test adapter combinations
        await self._test_adapter_combinations()
        
        # Generate test report
        test_time = time.time() - start_time
        report = self._generate_test_report(test_time)
        
        # Cleanup
        await self._cleanup()
        
        return report
        
    async def _initialize_registry(self):
        """Initialize the adapter registry"""
        
        logger.info("🚀 Initializing adapter registry...")
        
        try:
            # Register all adapters
            register_github_adapters()
            
            # Initialize adapters by category
            categories = ['anti_bot_defense', 'content_extraction', 'url_discovery']
            
            for category in categories:
                logger.info(f"Initializing {category} adapters...")
                results = await self.registry.initialize_category(category)
                
                self.test_results[f'init_{category}'] = {
                    'success': any(results.values()),
                    'details': results,
                    'category': category
                }
                
        except Exception as e:
            logger.error(f"❌ Registry initialization failed: {str(e)}")
            self.test_results['init_registry'] = {
                'success': False,
                'error': str(e)
            }
            
    async def _test_individual_adapters(self):
        """Test each adapter individually"""
        
        logger.info("🔍 Testing individual adapters...")
        
        # Test anti-bot defense adapters
        await self._test_flaresolverr()
        await self._test_undetected_chrome()
        await self._test_cloudscraper()
        await self._test_cloudflare_scrape()
        
        # Test content extraction adapters
        await self._test_trafilatura()
        
        # Test URL discovery adapters
        await self._test_katana()
        
    async def _test_flaresolverr(self):
        """Test FlareSolverr adapter"""
        
        logger.info("Testing FlareSolverr adapter...")
        
        try:
            adapter = await self.registry.get_adapter('flaresolverr')
            if not adapter:
                self.test_results['flaresolverr'] = {'success': False, 'error': 'Adapter not initialized'}
                return
                
            # Test basic functionality
            result = await self.registry.call_adapter_method(
                'flaresolverr', 'solve_challenge',
                'https://httpbin.org/get',
                user_agent='TestAgent/1.0'
            )
            
            self.test_results['flaresolverr'] = {
                'success': result.get('success', False),
                'method': 'solve_challenge',
                'details': {
                    'url_tested': 'https://httpbin.org/get',
                    'status_code': result.get('status_code'),
                    'response_time': result.get('response_time'),
                    'error': result.get('error')
                }
            }
            
        except Exception as e:
            self.test_results['flaresolverr'] = {
                'success': False,
                'error': str(e)
            }
            
    async def _test_undetected_chrome(self):
        """Test Undetected Chrome adapter"""
        
        logger.info("Testing Undetected Chrome adapter...")
        
        try:
            adapter = await self.registry.get_adapter('undetected_chrome')
            if not adapter:
                self.test_results['undetected_chrome'] = {'success': False, 'error': 'Adapter not initialized'}
                return
                
            # Test stealth browsing
            result = await self.registry.call_adapter_method(
                'undetected_chrome', 'get_page_stealth',
                'https://httpbin.org/get',
                wait_for='body'
            )
            
            self.test_results['undetected_chrome'] = {
                'success': result.get('success', False),
                'method': 'get_page_stealth',
                'details': {
                    'url_tested': 'https://httpbin.org/get',
                    'content_length': len(result.get('html_content', '')),
                    'response_time': result.get('response_time'),
                    'error': result.get('error')
                }
            }
            
        except Exception as e:
            self.test_results['undetected_chrome'] = {
                'success': False,
                'error': str(e)
            }
            
    async def _test_cloudscraper(self):
        """Test CloudScraper adapter"""
        
        logger.info("Testing CloudScraper adapter...")
        
        try:
            adapter = await self.registry.get_adapter('cloudscraper')
            if not adapter:
                self.test_results['cloudscraper'] = {'success': False, 'error': 'Adapter not initialized'}
                return
                
            # Test CloudFlare bypass
            result = await self.registry.call_adapter_method(
                'cloudscraper', 'get_page_cloudflare',
                'https://httpbin.org/get'
            )
            
            self.test_results['cloudscraper'] = {
                'success': result.get('success', False),
                'method': 'get_page_cloudflare',
                'details': {
                    'url_tested': 'https://httpbin.org/get',
                    'status_code': result.get('status_code'),
                    'content_length': len(result.get('html_content', '')),
                    'response_time': result.get('response_time'),
                    'error': result.get('error')
                }
            }
            
        except Exception as e:
            self.test_results['cloudscraper'] = {
                'success': False,
                'error': str(e)
            }
            
    async def _test_cloudflare_scrape(self):
        """Test CloudFlare-Scrape adapter"""
        
        logger.info("Testing CloudFlare-Scrape adapter...")
        
        try:
            adapter = await self.registry.get_adapter('cloudflare_scrape')
            if not adapter:
                self.test_results['cloudflare_scrape'] = {'success': False, 'error': 'Adapter not initialized'}
                return
                
            # Test Node.js bypass
            result = await self.registry.call_adapter_method(
                'cloudflare_scrape', 'get_page_bypass',
                'https://httpbin.org/get'
            )
            
            self.test_results['cloudflare_scrape'] = {
                'success': result.get('success', False),
                'method': 'get_page_bypass',
                'details': {
                    'url_tested': 'https://httpbin.org/get',
                    'content_length': len(result.get('html_content', '')),
                    'response_time': result.get('response_time'),
                    'error': result.get('error')
                }
            }
            
        except Exception as e:
            self.test_results['cloudflare_scrape'] = {
                'success': False,
                'error': str(e)
            }
            
    async def _test_trafilatura(self):
        """Test Trafilatura adapter"""
        
        logger.info("Testing Trafilatura adapter...")
        
        try:
            adapter = await self.registry.get_adapter('trafilatura')
            if not adapter:
                self.test_results['trafilatura'] = {'success': False, 'error': 'Adapter not initialized'}
                return
                
            # Test content extraction with sample HTML
            sample_html = """
            <html>
            <head><title>Test Article</title></head>
            <body>
            <article>
            <h1>Test Article Title</h1>
            <p>This is a sample paragraph for testing content extraction.</p>
            <p>Another paragraph with more content for comprehensive testing.</p>
            <a href="https://example.com">External Link</a>
            <img src="test.jpg" alt="Test Image">
            </article>
            </body>
            </html>
            """
            
            result = await self.registry.call_adapter_method(
                'trafilatura', 'extract_article_content',
                sample_html, 'https://example.com/test'
            )
            
            self.test_results['trafilatura'] = {
                'success': result.get('success', False),
                'method': 'extract_article_content',
                'details': {
                    'title_extracted': result.get('title'),
                    'text_length': len(result.get('text_content', '')),
                    'word_count': result.get('word_count', 0),
                    'quality_score': result.get('quality_score', 0),
                    'links_found': len(result.get('links', [])),
                    'images_found': len(result.get('images', [])),
                    'error': result.get('error')
                }
            }
            
        except Exception as e:
            self.test_results['trafilatura'] = {
                'success': False,
                'error': str(e)
            }
            
    async def _test_katana(self):
        """Test Katana adapter"""
        
        logger.info("Testing Katana adapter...")
        
        try:
            adapter = await self.registry.get_adapter('katana')
            if not adapter:
                self.test_results['katana'] = {'success': False, 'error': 'Adapter not initialized'}
                return
                
            # Test URL discovery
            result = await self.registry.call_adapter_method(
                'katana', 'discover_urls_comprehensive',
                'https://example.com',
                max_depth=1,
                max_urls=10
            )
            
            self.test_results['katana'] = {
                'success': result.get('success', False),
                'method': 'discover_urls_comprehensive',
                'details': {
                    'target': result.get('target'),
                    'urls_discovered': result.get('total_urls', 0),
                    'unique_domains': result.get('unique_domains', 0),
                    'discovery_time': result.get('discovery_time', 0),
                    'by_source': result.get('by_source', {}),
                    'error': result.get('error')
                }
            }
            
        except Exception as e:
            self.test_results['katana'] = {
                'success': False,
                'error': str(e)
            }
            
    async def _test_high_level_interfaces(self):
        """Test high-level interface functions"""
        
        logger.info("🔗 Testing high-level interfaces...")
        
        # Test get_page_with_best_method
        await self._test_best_page_method()
        
        # Test extract_content_with_best_method
        await self._test_best_extraction_method()
        
        # Test discover_urls_with_best_method
        await self._test_best_discovery_method()
        
    async def _test_best_page_method(self):
        """Test get_page_with_best_method"""
        
        try:
            result = await get_page_with_best_method('https://httpbin.org/get')
            
            self.test_results['best_page_method'] = {
                'success': result.get('success', False),
                'method': result.get('method'),
                'details': {
                    'status_code': result.get('status_code'),
                    'content_length': len(result.get('html_content', '')),
                    'response_time': result.get('response_time'),
                    'error': result.get('error')
                }
            }
            
        except Exception as e:
            self.test_results['best_page_method'] = {
                'success': False,
                'error': str(e)
            }
            
    async def _test_best_extraction_method(self):
        """Test extract_content_with_best_method"""
        
        try:
            sample_html = """
            <html>
            <head><title>Integration Test Article</title></head>
            <body>
            <main>
            <h1>Integration Test Title</h1>
            <p>This is content for testing the best extraction method.</p>
            </main>
            </body>
            </html>
            """
            
            result = await extract_content_with_best_method(
                sample_html, 'https://example.com/integration-test'
            )
            
            self.test_results['best_extraction_method'] = {
                'success': result.get('success', False),
                'method': result.get('method'),
                'details': {
                    'title': result.get('title'),
                    'text_length': len(result.get('text_content', '')),
                    'word_count': result.get('word_count', 0),
                    'error': result.get('error')
                }
            }
            
        except Exception as e:
            self.test_results['best_extraction_method'] = {
                'success': False,
                'error': str(e)
            }
            
    async def _test_best_discovery_method(self):
        """Test discover_urls_with_best_method"""
        
        try:
            result = await discover_urls_with_best_method(
                'https://example.com',
                max_depth=1,
                max_urls=5
            )
            
            self.test_results['best_discovery_method'] = {
                'success': result.get('success', False),
                'method': result.get('method'),
                'details': {
                    'urls_discovered': result.get('total_urls', 0),
                    'error': result.get('error')
                }
            }
            
        except Exception as e:
            self.test_results['best_discovery_method'] = {
                'success': False,
                'error': str(e)
            }
            
    async def _test_adapter_combinations(self):
        """Test combinations of adapters working together"""
        
        logger.info("🔀 Testing adapter combinations...")
        
        # Test: Get page + Extract content
        await self._test_page_and_extraction_combo()
        
        # Test: Get page + Discover URLs
        await self._test_page_and_discovery_combo()
        
    async def _test_page_and_extraction_combo(self):
        """Test getting a page and extracting content"""
        
        try:
            # First get the page
            page_result = await get_page_with_best_method('https://example.com')
            
            if page_result.get('success'):
                # Then extract content
                content_result = await extract_content_with_best_method(
                    page_result['html_content'], 
                    page_result['url']
                )
                
                self.test_results['page_extraction_combo'] = {
                    'success': content_result.get('success', False),
                    'page_method': page_result.get('method'),
                    'extraction_method': content_result.get('method'),
                    'details': {
                        'page_status': page_result.get('status_code'),
                        'content_title': content_result.get('title'),
                        'text_length': len(content_result.get('text_content', '')),
                        'error': content_result.get('error')
                    }
                }
            else:
                self.test_results['page_extraction_combo'] = {
                    'success': False,
                    'error': f"Page fetch failed: {page_result.get('error')}"
                }
                
        except Exception as e:
            self.test_results['page_extraction_combo'] = {
                'success': False,
                'error': str(e)
            }
            
    async def _test_page_and_discovery_combo(self):
        """Test getting a page and discovering URLs"""
        
        try:
            # Test URL discovery
            discovery_result = await discover_urls_with_best_method(
                'https://example.com',
                max_depth=1,
                max_urls=5
            )
            
            self.test_results['page_discovery_combo'] = {
                'success': discovery_result.get('success', False),
                'discovery_method': discovery_result.get('method'),
                'details': {
                    'urls_found': discovery_result.get('total_urls', 0),
                    'unique_domains': discovery_result.get('unique_domains', 0),
                    'error': discovery_result.get('error')
                }
            }
            
        except Exception as e:
            self.test_results['page_discovery_combo'] = {
                'success': False,
                'error': str(e)
            }
            
    def _generate_test_report(self, test_time: float) -> Dict[str, Any]:
        """Generate comprehensive test report"""
        
        total_tests = len(self.test_results)
        successful_tests = sum(1 for result in self.test_results.values() if result.get('success'))
        success_rate = (successful_tests / total_tests) * 100 if total_tests > 0 else 0
        
        # Categorize results
        categories = {
            'initialization': [],
            'individual_adapters': [],
            'high_level_interfaces': [],
            'adapter_combinations': []
        }
        
        for test_name, result in self.test_results.items():
            if test_name.startswith('init_'):
                categories['initialization'].append((test_name, result))
            elif test_name in ['flaresolverr', 'undetected_chrome', 'cloudscraper', 
                              'cloudflare_scrape', 'trafilatura', 'katana']:
                categories['individual_adapters'].append((test_name, result))
            elif test_name.startswith('best_'):
                categories['high_level_interfaces'].append((test_name, result))
            elif test_name.endswith('_combo'):
                categories['adapter_combinations'].append((test_name, result))
                
        # Registry stats
        registry_stats = self.registry.get_registry_stats()
        
        report = {
            'summary': {
                'total_tests': total_tests,
                'successful_tests': successful_tests,
                'failed_tests': total_tests - successful_tests,
                'success_rate': success_rate,
                'test_duration': test_time
            },
            'registry_stats': registry_stats,
            'test_categories': {},
            'detailed_results': self.test_results,
            'recommendations': self._generate_recommendations()
        }
        
        # Add category summaries
        for category, tests in categories.items():
            if tests:
                successful = sum(1 for _, result in tests if result.get('success'))
                report['test_categories'][category] = {
                    'total': len(tests),
                    'successful': successful,
                    'success_rate': (successful / len(tests)) * 100 if tests else 0,
                    'tests': {name: result['success'] for name, result in tests}
                }
                
        return report
        
    def _generate_recommendations(self) -> List[str]:
        """Generate recommendations based on test results"""
        
        recommendations = []
        
        # Check adapter availability
        failed_adapters = [name for name, result in self.test_results.items() 
                          if not result.get('success') and name not in ['init_registry', 'best_discovery_method']]
        
        if failed_adapters:
            recommendations.append(f"Install missing dependencies for failed adapters: {', '.join(failed_adapters)}")
            
        # Check anti-bot defense
        anti_bot_success = any(self.test_results.get(name, {}).get('success', False) 
                              for name in ['flaresolverr', 'undetected_chrome', 'cloudscraper', 'cloudflare_scrape'])
        
        if not anti_bot_success:
            recommendations.append("Consider setting up at least one anti-bot defense method (FlareSolverr, Undetected Chrome, etc.)")
            
        # Check content extraction
        if not self.test_results.get('trafilatura', {}).get('success', False):
            recommendations.append("Install Trafilatura for advanced content extraction: pip install trafilatura")
            
        # Check URL discovery
        if not self.test_results.get('katana', {}).get('success', False):
            recommendations.append("Install Katana for URL discovery: go install github.com/projectdiscovery/katana/cmd/katana@latest")
            
        # High-level interface checks
        if not self.test_results.get('best_page_method', {}).get('success', False):
            recommendations.append("High-level page fetching interface needs attention")
            
        return recommendations
        
    async def _cleanup(self):
        """Clean up test resources"""
        await self.registry.cleanup_all()

async def main():
    """Run integration tests"""
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    tester = GitHubAdapterTester()
    
    try:
        # Run all tests
        report = await tester.run_all_tests()
        
        # Print summary
        print("\n" + "="*80)
        print("GITHUB REPOSITORY ADAPTER INTEGRATION TEST REPORT")
        print("="*80)
        
        summary = report['summary']
        print(f"Total Tests: {summary['total_tests']}")
        print(f"Successful: {summary['successful_tests']}")
        print(f"Failed: {summary['failed_tests']}")
        print(f"Success Rate: {summary['success_rate']:.1f}%")
        print(f"Duration: {summary['test_duration']:.2f}s")
        
        print("\n" + "-"*40)
        print("TEST CATEGORIES:")
        print("-"*40)
        
        for category, stats in report['test_categories'].items():
            print(f"{category.replace('_', ' ').title()}: {stats['successful']}/{stats['total']} ({stats['success_rate']:.1f}%)")
            
        print("\n" + "-"*40)
        print("REGISTRY STATS:")
        print("-"*40)
        
        registry_stats = report['registry_stats']
        print(f"Total Adapters: {registry_stats['total_adapters']}")
        print(f"Initialized: {registry_stats['initialized_adapters']}")
        
        print("\n" + "-"*40)
        print("RECOMMENDATIONS:")
        print("-"*40)
        
        for i, rec in enumerate(report['recommendations'], 1):
            print(f"{i}. {rec}")
            
        # Save detailed report
        report_path = Path("github_adapters_test_report.json")
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2, default=str)
            
        print(f"\n📄 Detailed report saved to: {report_path}")
        
        # Exit code based on success rate
        if summary['success_rate'] >= 70:
            print("\n✅ Tests passed with acceptable success rate")
            return 0
        else:
            print("\n❌ Tests failed - success rate below 70%")
            return 1
            
    except Exception as e:
        logger.error(f"❌ Test execution failed: {str(e)}")
        return 2

if __name__ == "__main__":
    import sys
    sys.exit(asyncio.run(main()))
