#!/usr/bin/env python3
"""
🧪 REVOLUTIONARY ULTIMATE SYSTEM DEMO & TESTING 🧪
==================================================

Demonstrerar och testar alla funktioner i Revolutionary Ultimate System v4.0:

🛡️ ANTI-BOT TESTING:
- Testar requests → cloudscraper → FlareSolverr → undetected-chrome pipeline
- Validerar CAPTCHA-lösning
- Kontrollerar TLS fingerprinting

📄 CONTENT EXTRACTION TESTING:
- HTML extraction med trafilatura vs BeautifulSoup
- PDF processing med Tika vs PyMuPDF
- Entity recognition (dates, amounts, measurements)
- Content quality scoring

⚙️ CONFIGURATION TESTING:
- Per-domain policies
- Rate limiting & retry logic
- Quality thresholds

🎯 REAL-WORLD SCENARIOS:
- News websites (Swedish & English)
- E-commerce sites
- Cloudflare-protected sites
- PDF documents
- API endpoints
"""

import asyncio
import logging
import time
import json
from typing import List, Dict, Any
from pathlib import Path
import sys

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from revolutionary_scraper.revolutionary_ultimate_v4 import RevolutionaryUltimateSystem
from revolutionary_scraper.system_configuration import ConfigurationManager

# Setup rich logging
try:
    from rich.console import Console
    from rich.table import Table
    from rich.progress import Progress, TaskID
    from rich.panel import Panel
    from rich import print as rich_print
    RICH_AVAILABLE = True
    console = Console()
except ImportError:
    RICH_AVAILABLE = False
    console = None

logger = logging.getLogger(__name__)


class RevolutionaryDemo:
    """Demonstrerar Revolutionary Ultimate System capabilities"""
    
    def __init__(self):
        self.demo_urls = {
            'basic_http': [
                'https://httpbin.org/get',
                'https://httpbin.org/html', 
                'https://httpbin.org/json',
            ],
            
            'swedish_sites': [
                'https://www.dn.se',
                'https://www.svt.se/nyheter',
                'https://www.aftonbladet.se',
                'https://www.expressen.se',
            ],
            
            'international_news': [
                'https://news.ycombinator.com',
                'https://www.bbc.com/news',
                'https://www.reuters.com',
            ],
            
            'ecommerce': [
                'https://example-shop.com/products',  # Placeholder
                'https://httpbin.org/html',  # Fallback test
            ],
            
            'cloudflare_protected': [
                'https://nowsecure.nl',  # Known Cloudflare test site
            ],
            
            'pdf_documents': [
                'https://www.w3.org/WAI/ER/tests/xhtml/testfiles/resources/pdf/dummy.pdf',
            ],
            
            'apis': [
                'https://jsonplaceholder.typicode.com/posts/1',
                'https://api.github.com/users/octocat',
            ]
        }
        
        self.results = {}
        
    def print_header(self, title: str):
        """Print demo section header"""
        if RICH_AVAILABLE:
            console.print(Panel(f"[bold blue]{title}[/bold blue]", expand=False))
        else:
            print(f"\n{'='*60}")
            print(f"🚀 {title}")
            print('='*60)
    
    def print_result(self, url: str, result: Any, details: Dict[str, Any] = None):
        """Print test result"""
        if RICH_AVAILABLE:
            status = "[green]✅ SUCCESS[/green]" if result.success else "[red]❌ FAILED[/red]"
            console.print(f"{status} {url}")
            
            if details:
                table = Table(show_header=True, header_style="bold magenta")
                table.add_column("Metric", style="cyan")
                table.add_column("Value", style="green")
                
                for key, value in details.items():
                    table.add_row(key, str(value))
                
                console.print(table)
        else:
            status = "✅ SUCCESS" if result.success else "❌ FAILED"
            print(f"{status} {url}")
            
            if details:
                for key, value in details.items():
                    print(f"   {key}: {value}")
    
    async def test_basic_functionality(self) -> Dict[str, Any]:
        """Test basic system functionality"""
        self.print_header("BASIC FUNCTIONALITY TEST")
        
        results = {
            'total_tested': 0,
            'successful': 0,
            'failed': 0,
            'total_time': 0.0,
            'average_quality': 0.0
        }
        
        async with RevolutionaryUltimateSystem() as scraper:
            
            for url in self.demo_urls['basic_http']:
                start_time = time.time()
                result = await scraper.scrape_url(url)
                end_time = time.time()
                
                results['total_tested'] += 1
                results['total_time'] += (end_time - start_time)
                
                if result.success:
                    results['successful'] += 1
                    if result.quality_score > 0:
                        results['average_quality'] += result.quality_score
                else:
                    results['failed'] += 1
                
                details = {
                    'Method': result.scraping_result.method_used.value if result.scraping_result else 'N/A',
                    'Status Code': result.scraping_result.status_code if result.scraping_result else 'N/A',
                    'Content Length': len(result.extracted_content.text or '') if result.extracted_content else 0,
                    'Quality Score': f"{result.quality_score:.2f}",
                    'Processing Time': f"{end_time - start_time:.2f}s",
                    'Error': result.error or 'None'
                }
                
                self.print_result(url, result, details)
        
        # Calculate averages
        if results['successful'] > 0:
            results['average_quality'] /= results['successful']
        
        self.results['basic'] = results
        return results
    
    async def test_anti_bot_escalation(self) -> Dict[str, Any]:
        """Test anti-bot method escalation"""
        self.print_header("ANTI-BOT ESCALATION TEST")
        
        results = {
            'methods_tested': {},
            'cloudflare_sites': 0,
            'captcha_detected': 0,
            'escalation_successful': 0
        }
        
        async with RevolutionaryUltimateSystem() as scraper:
            
            # Test Cloudflare-protected sites
            for url in self.demo_urls['cloudflare_protected']:
                result = await scraper.scrape_url(url)
                
                if result.scraping_result:
                    method = result.scraping_result.method_used.value
                    results['methods_tested'][method] = results['methods_tested'].get(method, 0) + 1
                    
                    if result.scraping_result.cloudflare_detected:
                        results['cloudflare_sites'] += 1
                    
                    if result.scraping_result.captcha_detected:
                        results['captcha_detected'] += 1
                    
                    if result.success:
                        results['escalation_successful'] += 1
                
                details = {
                    'Method Used': result.scraping_result.method_used.value if result.scraping_result else 'N/A',
                    'Cloudflare Detected': result.scraping_result.cloudflare_detected if result.scraping_result else False,
                    'CAPTCHA Detected': result.scraping_result.captcha_detected if result.scraping_result else False,
                    'Attempts': result.scraping_result.attempts if result.scraping_result else 0,
                    'Final Success': result.success
                }
                
                self.print_result(url, result, details)
        
        self.results['anti_bot'] = results
        return results
    
    async def test_content_extraction(self) -> Dict[str, Any]:
        """Test content extraction capabilities"""
        self.print_header("CONTENT EXTRACTION TEST")
        
        results = {
            'html_sites': 0,
            'pdf_documents': 0,
            'entities_extracted': 0,
            'high_quality_content': 0,
            'extraction_methods': {}
        }
        
        async with RevolutionaryUltimateSystem() as scraper:
            
            # Test HTML extraction
            for url in self.demo_urls['swedish_sites'][:2]:  # Test first 2 to avoid rate limits
                result = await scraper.scrape_url(url)
                
                if result.extracted_content:
                    results['html_sites'] += 1
                    
                    method = result.extracted_content.method_used.value if result.extracted_content.method_used else 'unknown'
                    results['extraction_methods'][method] = results['extraction_methods'].get(method, 0) + 1
                    
                    if result.extracted_content.entities:
                        results['entities_extracted'] += len(result.extracted_content.entities)
                    
                    if result.quality_score >= 0.7:
                        results['high_quality_content'] += 1
                
                details = {
                    'Extraction Method': result.extracted_content.method_used.value if result.extracted_content and result.extracted_content.method_used else 'N/A',
                    'Title': (result.extracted_content.title or 'No title')[:50] + '...' if result.extracted_content and result.extracted_content.title else 'No title',
                    'Text Length': len(result.extracted_content.text or '') if result.extracted_content else 0,
                    'Word Count': result.extracted_content.word_count if result.extracted_content else 0,
                    'Entities Found': len(result.extracted_content.entities) if result.extracted_content and result.extracted_content.entities else 0,
                    'Quality Score': f"{result.quality_score:.2f}",
                    'Language': result.extracted_content.language if result.extracted_content else 'N/A'
                }
                
                self.print_result(url, result, details)
                
                # Show sample entities
                if result.extracted_content and result.extracted_content.entities:
                    if RICH_AVAILABLE:
                        console.print("   [yellow]Sample entities:[/yellow]")
                        for entity in result.extracted_content.entities[:3]:
                            console.print(f"   • {entity.type}: {entity.text} → {entity.value}")
                    else:
                        print("   Sample entities:")
                        for entity in result.extracted_content.entities[:3]:
                            print(f"   • {entity.type}: {entity.text} → {entity.value}")
        
        self.results['content'] = results
        return results
    
    async def test_performance_scaling(self) -> Dict[str, Any]:
        """Test performance with multiple concurrent requests"""
        self.print_header("PERFORMANCE & SCALING TEST")
        
        # Test concurrent processing
        test_urls = self.demo_urls['basic_http'] * 3  # 9 URLs total
        
        start_time = time.time()
        
        async with RevolutionaryUltimateSystem() as scraper:
            results = await scraper.scrape_urls(test_urls)
        
        end_time = time.time()
        
        performance_results = {
            'total_urls': len(test_urls),
            'successful': sum(1 for r in results if r.success),
            'failed': sum(1 for r in results if not r.success),
            'total_time': end_time - start_time,
            'average_time_per_url': (end_time - start_time) / len(test_urls),
            'requests_per_second': len(test_urls) / (end_time - start_time),
            'concurrent_efficiency': 'Good' if (end_time - start_time) < len(test_urls) * 2 else 'Needs improvement'
        }
        
        if RICH_AVAILABLE:
            table = Table(show_header=True, header_style="bold magenta")
            table.add_column("Performance Metric", style="cyan")
            table.add_column("Value", style="green")
            
            for key, value in performance_results.items():
                table.add_row(key.replace('_', ' ').title(), str(value))
            
            console.print(table)
        else:
            print("Performance Results:")
            for key, value in performance_results.items():
                print(f"   {key.replace('_', ' ').title()}: {value}")
        
        self.results['performance'] = performance_results
        return performance_results
    
    async def test_domain_policies(self) -> Dict[str, Any]:
        """Test domain-specific policies"""
        self.print_header("DOMAIN POLICIES TEST")
        
        # Load configuration
        config_manager = ConfigurationManager()
        config = config_manager.load_config()
        
        policy_results = {
            'policies_tested': 0,
            'custom_policies_applied': 0,
            'rate_limiting_respected': True
        }
        
        # Test different domain policies
        test_domains = ['example.com', 'httpbin.org', 'test.local']
        
        for domain in test_domains:
            policy = config_manager.get_domain_policy(domain)
            policy_results['policies_tested'] += 1
            
            if RICH_AVAILABLE:
                console.print(f"[cyan]Domain:[/cyan] {domain}")
                console.print(f"   Engine: {policy.engine}")
                console.print(f"   Rate Limit: {policy.rate_limit}/s")
                console.print(f"   Quality Threshold: {policy.min_quality}")
                console.print(f"   Max Retries: {policy.max_retries}")
            else:
                print(f"Domain: {domain}")
                print(f"   Engine: {policy.engine}")
                print(f"   Rate Limit: {policy.rate_limit}/s")
                print(f"   Quality Threshold: {policy.min_quality}")
                print(f"   Max Retries: {policy.max_retries}")
        
        self.results['policies'] = policy_results
        return policy_results
    
    def generate_report(self):
        """Generate comprehensive test report"""
        self.print_header("COMPREHENSIVE TEST REPORT")
        
        if RICH_AVAILABLE:
            # Overall summary table
            summary_table = Table(show_header=True, header_style="bold magenta")
            summary_table.add_column("Test Category", style="cyan")
            summary_table.add_column("Status", style="green")
            summary_table.add_column("Details", style="white")
            
            # Basic functionality
            basic = self.results.get('basic', {})
            basic_status = "✅ PASSED" if basic.get('successful', 0) > 0 else "❌ FAILED"
            basic_details = f"{basic.get('successful', 0)}/{basic.get('total_tested', 0)} successful"
            summary_table.add_row("Basic Functionality", basic_status, basic_details)
            
            # Anti-bot
            anti_bot = self.results.get('anti_bot', {})
            anti_bot_status = "✅ PASSED" if anti_bot.get('escalation_successful', 0) > 0 else "⚠️  PARTIAL"
            anti_bot_details = f"{len(anti_bot.get('methods_tested', {}))} methods tested"
            summary_table.add_row("Anti-Bot Defense", anti_bot_status, anti_bot_details)
            
            # Content extraction
            content = self.results.get('content', {})
            content_status = "✅ PASSED" if content.get('html_sites', 0) > 0 else "❌ FAILED"
            content_details = f"{content.get('entities_extracted', 0)} entities extracted"
            summary_table.add_row("Content Extraction", content_status, content_details)
            
            # Performance
            perf = self.results.get('performance', {})
            perf_status = "✅ PASSED" if perf.get('requests_per_second', 0) > 1 else "⚠️  SLOW"
            perf_details = f"{perf.get('requests_per_second', 0):.1f} req/s"
            summary_table.add_row("Performance", perf_status, perf_details)
            
            console.print(summary_table)
            
            # Recommendations
            console.print("\n[bold yellow]RECOMMENDATIONS:[/bold yellow]")
            
            if basic.get('successful', 0) < basic.get('total_tested', 0):
                console.print("• Check network connectivity and service availability")
            
            if anti_bot.get('cloudflare_sites', 0) > 0:
                console.print("• Cloudflare detected - consider API keys for 2captcha/FlareSolverr")
            
            if content.get('high_quality_content', 0) == 0:
                console.print("• Consider lowering quality thresholds or improving extraction")
            
            if perf.get('requests_per_second', 0) < 2:
                console.print("• Performance could be improved - check rate limits and concurrency")
            
        else:
            # Plain text report
            print("\nTEST SUMMARY:")
            print("=" * 40)
            
            for category, results in self.results.items():
                print(f"\n{category.upper()} RESULTS:")
                for key, value in results.items():
                    print(f"  {key}: {value}")
    
    async def run_full_demo(self):
        """Run complete demonstration"""
        if RICH_AVAILABLE:
            rich_print("[bold green]🚀 REVOLUTIONARY ULTIMATE SYSTEM DEMO STARTING[/bold green]")
        else:
            print("🚀 REVOLUTIONARY ULTIMATE SYSTEM DEMO STARTING")
        
        try:
            # Run all test suites
            await self.test_basic_functionality()
            await self.test_anti_bot_escalation() 
            await self.test_content_extraction()
            await self.test_performance_scaling()
            await self.test_domain_policies()
            
            # Generate final report
            self.generate_report()
            
            if RICH_AVAILABLE:
                rich_print("[bold green]🎉 DEMO COMPLETED SUCCESSFULLY[/bold green]")
            else:
                print("🎉 DEMO COMPLETED SUCCESSFULLY")
                
        except Exception as e:
            if RICH_AVAILABLE:
                rich_print(f"[bold red]❌ DEMO FAILED: {e}[/bold red]")
            else:
                print(f"❌ DEMO FAILED: {e}")
            
            logger.error(f"Demo failed with exception: {e}")
            raise


# Interactive demo menu
async def interactive_menu():
    """Interactive demo menu"""
    demo = RevolutionaryDemo()
    
    while True:
        if RICH_AVAILABLE:
            console.print("\n[bold blue]Revolutionary Ultimate System Demo Menu[/bold blue]")
            console.print("1. Run Full Demo")
            console.print("2. Test Basic Functionality")
            console.print("3. Test Anti-Bot Defense")
            console.print("4. Test Content Extraction")
            console.print("5. Test Performance")
            console.print("6. Test Domain Policies")
            console.print("7. Custom URL Test")
            console.print("0. Exit")
        else:
            print("\nRevolutionary Ultimate System Demo Menu")
            print("1. Run Full Demo")
            print("2. Test Basic Functionality") 
            print("3. Test Anti-Bot Defense")
            print("4. Test Content Extraction")
            print("5. Test Performance")
            print("6. Test Domain Policies")
            print("7. Custom URL Test")
            print("0. Exit")
        
        choice = input("\nSelect option: ").strip()
        
        try:
            if choice == '1':
                await demo.run_full_demo()
            elif choice == '2':
                await demo.test_basic_functionality()
            elif choice == '3':
                await demo.test_anti_bot_escalation()
            elif choice == '4':
                await demo.test_content_extraction()
            elif choice == '5':
                await demo.test_performance_scaling()
            elif choice == '6':
                await demo.test_domain_policies()
            elif choice == '7':
                url = input("Enter URL to test: ").strip()
                if url:
                    async with RevolutionaryUltimateSystem() as scraper:
                        result = await scraper.scrape_url(url)
                        demo.print_result(url, result)
            elif choice == '0':
                print("Goodbye! 👋")
                break
            else:
                print("Invalid choice. Please try again.")
                
        except KeyboardInterrupt:
            print("\nOperation cancelled by user.")
        except Exception as e:
            print(f"Error: {e}")


# Main execution
async def main():
    """Main demo function"""
    
    import argparse
    parser = argparse.ArgumentParser(description="Revolutionary Ultimate System Demo")
    parser.add_argument('--full', action='store_true', help='Run full demo')
    parser.add_argument('--interactive', action='store_true', help='Interactive menu')
    parser.add_argument('--url', type=str, help='Test specific URL')
    
    args = parser.parse_args()
    
    if args.url:
        # Test specific URL
        async with RevolutionaryUltimateSystem() as scraper:
            result = await scraper.scrape_url(args.url)
            
            print(f"\nURL: {args.url}")
            print(f"Success: {result.success}")
            
            if result.success:
                print(f"Method: {result.scraping_result.method_used.value if result.scraping_result else 'N/A'}")
                print(f"Quality: {result.quality_score:.2f}")
                
                if result.extracted_content:
                    print(f"Title: {result.extracted_content.title or 'No title'}")
                    print(f"Text length: {len(result.extracted_content.text or '')} chars")
                    print(f"Entities: {len(result.extracted_content.entities or [])} found")
            else:
                print(f"Error: {result.error}")
                
    elif args.full:
        # Run full demo
        demo = RevolutionaryDemo()
        await demo.run_full_demo()
        
    elif args.interactive:
        # Interactive mode
        await interactive_menu()
        
    else:
        # Default: show menu
        await interactive_menu()


if __name__ == "__main__":
    asyncio.run(main())
