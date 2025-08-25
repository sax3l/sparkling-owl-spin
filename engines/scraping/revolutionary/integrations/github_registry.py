#!/usr/bin/env python3
"""
GitHub Repository Integration Registry - Revolutionary Ultimate System v4.0
Centralized registry and management for all GitHub-based crawler integrations
"""

import logging
import asyncio
import time
from typing import Dict, Any, List, Optional, Type, Union
from dataclasses import dataclass, asdict
from pathlib import Path
from enum import Enum

logger = logging.getLogger(__name__)

class IntegrationCategory(Enum):
    """Categories for GitHub integrations"""
    CONTENT_EXTRACTION = "content_extraction"
    PROXY_MANAGEMENT = "proxy_management"
    URL_DISCOVERY = "url_discovery"
    ANTI_BOT_DEFENSE = "anti_bot_defense"
    BROWSER_AUTOMATION = "browser_automation"
    CRAWLING_FRAMEWORKS = "crawling_frameworks"
    DATA_PROCESSING = "data_processing"
    MONITORING = "monitoring"

@dataclass
class IntegrationInfo:
    """Information about a GitHub integration"""
    name: str
    display_name: str
    category: IntegrationCategory
    description: str
    github_repo: str
    adapter_module: str
    adapter_class: str
    primary_features: List[str]
    dependencies: List[str]
    optional_dependencies: List[str]
    supported_formats: List[str]
    min_python_version: str = "3.8"
    platform_support: List[str] = None
    documentation_url: Optional[str] = None
    license: str = "Unknown"
    maturity_level: str = "stable"  # experimental, beta, stable, mature
    performance_tier: str = "medium"  # low, medium, high, enterprise
    last_updated: Optional[str] = None

class GitHubIntegrationRegistry:
    """
    Centralized registry for all GitHub repository integrations.
    
    Manages the complete collection of third-party tools integrated
    into the Revolutionary Ultimate System.
    """
    
    def __init__(self):
        self._integrations = {}
        self._loaded_adapters = {}
        self._stats = {
            'total_integrations': 0,
            'loaded_adapters': 0,
            'failed_loads': 0,
            'successful_operations': 0,
            'failed_operations': 0,
            'total_execution_time': 0.0
        }
        self._initialize_registry()
        
    def _initialize_registry(self):
        """Initialize the registry with all known integrations"""
        
        # Content Extraction Tools
        self._register_integration(IntegrationInfo(
            name="apache_tika",
            display_name="Apache Tika",
            category=IntegrationCategory.CONTENT_EXTRACTION,
            description="Multi-format document extraction with 1000+ file type support and OCR",
            github_repo="apache/tika",
            adapter_module="revolutionary_scraper.adapters.apache_tika_adapter",
            adapter_class="ApacheTikaAdapter",
            primary_features=["Multi-format parsing", "OCR", "Metadata extraction", "Batch processing"],
            dependencies=["requests", "subprocess"],
            optional_dependencies=["java", "tesseract"],
            supported_formats=["PDF", "DOC", "XLS", "PPT", "HTML", "XML", "RTF", "TXT", "Images"],
            platform_support=["Windows", "Linux", "macOS"],
            documentation_url="https://tika.apache.org/",
            license="Apache 2.0",
            maturity_level="mature",
            performance_tier="high"
        ))
        
        self._register_integration(IntegrationInfo(
            name="trafilatura",
            display_name="Trafilatura",
            category=IntegrationCategory.CONTENT_EXTRACTION,
            description="Web content extraction focused on main text and metadata",
            github_repo="adbar/trafilatura",
            adapter_module="revolutionary_scraper.adapters.trafilatura_adapter",
            adapter_class="TrafilaturaAdapter",
            primary_features=["Main content extraction", "Language detection", "Metadata extraction", "XML output"],
            dependencies=["trafilatura", "requests"],
            optional_dependencies=["selenium", "playwright"],
            supported_formats=["HTML", "XML"],
            platform_support=["Windows", "Linux", "macOS"],
            documentation_url="https://trafilatura.readthedocs.io/",
            license="GPL-3.0",
            maturity_level="stable",
            performance_tier="high"
        ))
        
        self._register_integration(IntegrationInfo(
            name="pdf_extract_kit",
            display_name="PDF-Extract-Kit",
            category=IntegrationCategory.CONTENT_EXTRACTION,
            description="Advanced PDF processing with layout analysis and specialized content extraction",
            github_repo="opendatalab/PDF-Extract-Kit",
            adapter_module="revolutionary_scraper.adapters.pdf_extract_kit_adapter",
            adapter_class="PDFExtractKitAdapter",
            primary_features=["Layout analysis", "Table extraction", "Figure extraction", "Mathematical formulas", "Reading order"],
            dependencies=["requests", "json"],
            optional_dependencies=["PyMuPDF", "PIL", "numpy"],
            supported_formats=["PDF"],
            platform_support=["Windows", "Linux", "macOS"],
            documentation_url="https://github.com/opendatalab/PDF-Extract-Kit",
            license="Apache 2.0",
            maturity_level="beta",
            performance_tier="high"
        ))
        
        # Proxy Management Tools
        self._register_integration(IntegrationInfo(
            name="proxy_broker",
            display_name="ProxyBroker",
            category=IntegrationCategory.PROXY_MANAGEMENT,
            description="Asynchronous proxy finder and checker with comprehensive validation",
            github_repo="constverum/ProxyBroker",
            adapter_module="revolutionary_scraper.adapters.proxy_broker_adapter",
            adapter_class="ProxyBrokerAdapter",
            primary_features=["Proxy discovery", "Health checking", "Anonymity testing", "Geographic filtering"],
            dependencies=["aiohttp", "asyncio"],
            optional_dependencies=["proxybroker"],
            supported_formats=["HTTP", "HTTPS", "SOCKS4", "SOCKS5"],
            platform_support=["Windows", "Linux", "macOS"],
            documentation_url="https://proxybroker.readthedocs.io/",
            license="Apache 2.0",
            maturity_level="stable",
            performance_tier="medium"
        ))
        
        self._register_integration(IntegrationInfo(
            name="proxy_pool",
            display_name="Proxy Pool",
            category=IntegrationCategory.PROXY_MANAGEMENT,
            description="Distributed proxy pool with Redis backend and health monitoring",
            github_repo="jhao104/proxy_pool",
            adapter_module="revolutionary_scraper.adapters.proxy_pool_adapter",
            adapter_class="ProxyPoolAdapter",
            primary_features=["Pool management", "Health monitoring", "Load balancing", "Redis integration"],
            dependencies=["requests", "redis"],
            optional_dependencies=["schedule", "flask"],
            supported_formats=["HTTP", "HTTPS"],
            platform_support=["Windows", "Linux", "macOS"],
            documentation_url="https://github.com/jhao104/proxy_pool",
            license="MIT",
            maturity_level="stable",
            performance_tier="medium"
        ))
        
        self._register_integration(IntegrationInfo(
            name="requests_ip_rotator",
            display_name="Requests IP Rotator",
            category=IntegrationCategory.PROXY_MANAGEMENT,
            description="Automatic IP rotation for requests with AWS integration",
            github_repo="Ge0rg3/requests-ip-rotator",
            adapter_module="revolutionary_scraper.adapters.requests_ip_rotator_adapter",
            adapter_class="RequestsIPRotatorAdapter",
            primary_features=["Automatic IP rotation", "AWS integration", "Session management", "Rate limiting"],
            dependencies=["requests", "boto3"],
            optional_dependencies=["aws-cli"],
            supported_formats=["HTTP", "HTTPS"],
            platform_support=["Windows", "Linux", "macOS"],
            documentation_url="https://github.com/Ge0rg3/requests-ip-rotator",
            license="GPL-3.0",
            maturity_level="stable",
            performance_tier="high"
        ))
        
        # URL Discovery Tools
        self._register_integration(IntegrationInfo(
            name="katana",
            display_name="Katana",
            category=IntegrationCategory.URL_DISCOVERY,
            description="Fast web crawler with JavaScript support and comprehensive URL discovery",
            github_repo="projectdiscovery/katana",
            adapter_module="revolutionary_scraper.adapters.katana_adapter",
            adapter_class="KatanaAdapter",
            primary_features=["JavaScript support", "Headless crawling", "URL filtering", "Output formats"],
            dependencies=["subprocess", "json"],
            optional_dependencies=["katana-binary"],
            supported_formats=["JSON", "TXT"],
            platform_support=["Windows", "Linux", "macOS"],
            documentation_url="https://github.com/projectdiscovery/katana",
            license="MIT",
            maturity_level="stable",
            performance_tier="high"
        ))
        
        self._register_integration(IntegrationInfo(
            name="photon",
            display_name="Photon",
            category=IntegrationCategory.URL_DISCOVERY,
            description="Lightning-fast web crawler with intelligence and extensive data extraction",
            github_repo="s0md3v/Photon",
            adapter_module="revolutionary_scraper.adapters.photon_adapter",
            adapter_class="PhotonAdapter",
            primary_features=["Fast crawling", "Data extraction", "URL filtering", "Multi-threading"],
            dependencies=["requests", "threading"],
            optional_dependencies=["python-photon"],
            supported_formats=["TXT", "JSON"],
            platform_support=["Windows", "Linux", "macOS"],
            documentation_url="https://github.com/s0md3v/Photon",
            license="GPL-3.0",
            maturity_level="stable",
            performance_tier="high"
        ))
        
        self._register_integration(IntegrationInfo(
            name="colly",
            display_name="Colly",
            category=IntegrationCategory.URL_DISCOVERY,
            description="Go-powered high-performance web scraper with concurrent processing",
            github_repo="gocolly/colly",
            adapter_module="revolutionary_scraper.adapters.colly_adapter",
            adapter_class="CollyAdapter",
            primary_features=["High performance", "Concurrent processing", "Go integration", "HTTP API"],
            dependencies=["requests"],
            optional_dependencies=["go", "colly-server"],
            supported_formats=["JSON", "HTML"],
            platform_support=["Windows", "Linux", "macOS"],
            documentation_url="https://go-colly.org/",
            license="Apache 2.0",
            maturity_level="stable",
            performance_tier="enterprise"
        ))
        
        # Anti-bot Defense Tools
        self._register_integration(IntegrationInfo(
            name="flaresolverr",
            display_name="FlareSolverr",
            category=IntegrationCategory.ANTI_BOT_DEFENSE,
            description="CloudFlare bypass service with JavaScript challenge solving",
            github_repo="FlareSolverr/FlareSolverr",
            adapter_module="revolutionary_scraper.adapters.flaresolverr_adapter",
            adapter_class="FlareSolverrAdapter",
            primary_features=["CloudFlare bypass", "JavaScript challenges", "Proxy support", "Session management"],
            dependencies=["requests"],
            optional_dependencies=["docker", "flaresolverr-service"],
            supported_formats=["HTML", "JSON"],
            platform_support=["Windows", "Linux", "macOS"],
            documentation_url="https://github.com/FlareSolverr/FlareSolverr",
            license="MIT",
            maturity_level="stable",
            performance_tier="medium"
        ))
        
        self._register_integration(IntegrationInfo(
            name="undetected_chrome",
            display_name="Undetected Chrome",
            category=IntegrationCategory.ANTI_BOT_DEFENSE,
            description="Stealth browser automation bypassing detection systems",
            github_repo="ultrafunkamsterdam/undetected-chromedriver",
            adapter_module="revolutionary_scraper.adapters.undetected_chrome_adapter",
            adapter_class="UndetectedChromeAdapter",
            primary_features=["Stealth mode", "Detection bypass", "Chrome automation", "Session persistence"],
            dependencies=["selenium", "undetected-chromedriver"],
            optional_dependencies=["chrome-binary"],
            supported_formats=["HTML", "Screenshots"],
            platform_support=["Windows", "Linux", "macOS"],
            documentation_url="https://github.com/ultrafunkamsterdam/undetected-chromedriver",
            license="GPL-3.0",
            maturity_level="stable",
            performance_tier="medium"
        ))
        
        self._register_integration(IntegrationInfo(
            name="cloudscraper",
            display_name="CloudScraper",
            category=IntegrationCategory.ANTI_BOT_DEFENSE,
            description="Python library to bypass CloudFlare protection",
            github_repo="VeNoMouS/cloudscraper",
            adapter_module="revolutionary_scraper.adapters.cloudscraper_adapter",
            adapter_class="CloudScraperAdapter",
            primary_features=["CloudFlare bypass", "JavaScript execution", "Cookie management", "Captcha solving"],
            dependencies=["cloudscraper", "requests"],
            optional_dependencies=["captcha-solvers"],
            supported_formats=["HTML", "JSON"],
            platform_support=["Windows", "Linux", "macOS"],
            documentation_url="https://github.com/VeNoMouS/cloudscraper",
            license="MIT",
            maturity_level="stable",
            performance_tier="medium"
        ))
        
        self._register_integration(IntegrationInfo(
            name="cloudflare_scrape",
            display_name="CloudFlare-Scrape",
            category=IntegrationCategory.ANTI_BOT_DEFENSE,
            description="Specialized CloudFlare challenge solver",
            github_repo="Anorov/cloudflare-scrape",
            adapter_module="revolutionary_scraper.adapters.cloudflare_scrape_adapter",
            adapter_class="CloudFlareScrapeAdapter",
            primary_features=["Challenge solving", "Cookie preservation", "Session management", "Rate limiting"],
            dependencies=["cfscrape", "requests"],
            optional_dependencies=["node.js"],
            supported_formats=["HTML", "Cookies"],
            platform_support=["Windows", "Linux", "macOS"],
            documentation_url="https://github.com/Anorov/cloudflare-scrape",
            license="MIT",
            maturity_level="stable",
            performance_tier="medium"
        ))
        
        # Browser Automation Tools
        self._register_integration(IntegrationInfo(
            name="playwright",
            display_name="Playwright",
            category=IntegrationCategory.BROWSER_AUTOMATION,
            description="Modern browser automation with multi-browser support",
            github_repo="microsoft/playwright-python",
            adapter_module="revolutionary_scraper.adapters.playwright_adapter",
            adapter_class="PlaywrightAdapter",
            primary_features=["Multi-browser", "Device emulation", "Network monitoring", "PDF generation"],
            dependencies=["playwright"],
            optional_dependencies=["playwright-browsers"],
            supported_formats=["HTML", "PDF", "Screenshots"],
            platform_support=["Windows", "Linux", "macOS"],
            documentation_url="https://playwright.dev/python/",
            license="Apache 2.0",
            maturity_level="mature",
            performance_tier="enterprise"
        ))
        
        self._register_integration(IntegrationInfo(
            name="drission_page",
            display_name="DrissionPage",
            category=IntegrationCategory.BROWSER_AUTOMATION,
            description="Python browser automation with selenium-like simplicity",
            github_repo="g1879/DrissionPage",
            adapter_module="revolutionary_scraper.adapters.drission_adapter",
            adapter_class="DrissionPageAdapter",
            primary_features=["Browser automation", "Element extraction", "Form interaction", "Screenshot capture"],
            dependencies=["requests"],
            optional_dependencies=["DrissionPage", "chrome-driver"],
            supported_formats=["HTML", "Screenshots"],
            platform_support=["Windows", "Linux", "macOS"],
            documentation_url="https://github.com/g1879/DrissionPage",
            license="BSD-3-Clause",
            maturity_level="stable",
            performance_tier="medium"
        ))
        
        # Crawling Frameworks
        self._register_integration(IntegrationInfo(
            name="crawlee",
            display_name="Crawlee",
            category=IntegrationCategory.CRAWLING_FRAMEWORKS,
            description="Node.js-powered web crawler via HTTP API interface",
            github_repo="apify/crawlee",
            adapter_module="revolutionary_scraper.adapters.crawlee_adapter",
            adapter_class="CrawleeAdapter",
            primary_features=["Node.js crawling", "Multiple crawler types", "Session management", "Proxy support"],
            dependencies=["requests"],
            optional_dependencies=["node.js", "npm", "crawlee"],
            supported_formats=["HTML", "JSON"],
            platform_support=["Windows", "Linux", "macOS"],
            documentation_url="https://crawlee.dev/",
            license="Apache 2.0",
            maturity_level="stable",
            performance_tier="high"
        ))
        
        logger.info(f"✅ Initialized registry with {len(self._integrations)} integrations")
        self._stats['total_integrations'] = len(self._integrations)
        
    def _register_integration(self, integration_info: IntegrationInfo):
        """Register an integration"""
        self._integrations[integration_info.name] = integration_info
        
    def get_integration(self, name: str) -> Optional[IntegrationInfo]:
        """Get integration by name"""
        return self._integrations.get(name)
        
    def list_integrations(self, 
                         category: Optional[IntegrationCategory] = None,
                         maturity_level: Optional[str] = None,
                         performance_tier: Optional[str] = None) -> List[IntegrationInfo]:
        """List integrations with optional filtering"""
        
        integrations = list(self._integrations.values())
        
        if category:
            integrations = [i for i in integrations if i.category == category]
            
        if maturity_level:
            integrations = [i for i in integrations if i.maturity_level == maturity_level]
            
        if performance_tier:
            integrations = [i for i in integrations if i.performance_tier == performance_tier]
            
        return integrations
        
    def get_by_category(self, category: IntegrationCategory) -> List[IntegrationInfo]:
        """Get all integrations in a category"""
        return [info for info in self._integrations.values() if info.category == category]
        
    async def load_adapter(self, integration_name: str, config: Dict[str, Any] = None) -> Optional[Any]:
        """Load adapter for integration"""
        
        if integration_name in self._loaded_adapters:
            return self._loaded_adapters[integration_name]
            
        integration = self.get_integration(integration_name)
        if not integration:
            logger.error(f"❌ Integration '{integration_name}' not found")
            return None
            
        try:
            # Import adapter module
            module_path = integration.adapter_module
            class_name = integration.adapter_class
            
            # Dynamic import
            import importlib
            module = importlib.import_module(module_path)
            adapter_class = getattr(module, class_name)
            
            # Create adapter instance
            adapter_config = config or {}
            adapter = adapter_class(adapter_config)
            
            # Initialize if it's async
            if hasattr(adapter, 'initialize') and asyncio.iscoroutinefunction(adapter.initialize):
                await adapter.initialize()
            elif hasattr(adapter, 'initialize'):
                adapter.initialize()
                
            self._loaded_adapters[integration_name] = adapter
            self._stats['loaded_adapters'] += 1
            
            logger.info(f"✅ Loaded adapter for '{integration.display_name}'")
            return adapter
            
        except Exception as e:
            self._stats['failed_loads'] += 1
            logger.error(f"❌ Failed to load adapter for '{integration_name}': {str(e)}")
            return None
            
    async def execute_operation(self, 
                              integration_name: str, 
                              operation: str, 
                              *args, 
                              **kwargs) -> Dict[str, Any]:
        """Execute operation on integration adapter"""
        
        start_time = time.time()
        
        try:
            # Load adapter if not already loaded
            adapter = await self.load_adapter(integration_name)
            if not adapter:
                return {
                    'success': False,
                    'error': f'Failed to load adapter for {integration_name}',
                    'integration': integration_name,
                    'operation': operation
                }
                
            # Check if operation exists
            if not hasattr(adapter, operation):
                return {
                    'success': False,
                    'error': f'Operation {operation} not found in {integration_name}',
                    'integration': integration_name,
                    'operation': operation
                }
                
            # Execute operation
            method = getattr(adapter, operation)
            
            if asyncio.iscoroutinefunction(method):
                result = await method(*args, **kwargs)
            else:
                result = method(*args, **kwargs)
                
            execution_time = time.time() - start_time
            self._stats['successful_operations'] += 1
            self._stats['total_execution_time'] += execution_time
            
            # Ensure result is a dict
            if not isinstance(result, dict):
                result = {'result': result}
                
            result.update({
                'integration': integration_name,
                'operation': operation,
                'execution_time': execution_time
            })
            
            return result
            
        except Exception as e:
            execution_time = time.time() - start_time
            self._stats['failed_operations'] += 1
            
            logger.error(f"❌ Operation failed: {integration_name}.{operation}: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'integration': integration_name,
                'operation': operation,
                'execution_time': execution_time
            }
            
    def get_integration_stats(self) -> Dict[str, Any]:
        """Get comprehensive integration statistics"""
        
        # Category breakdown
        category_counts = {}
        for category in IntegrationCategory:
            category_counts[category.value] = len(self.get_by_category(category))
            
        # Maturity breakdown
        maturity_counts = {}
        performance_counts = {}
        
        for integration in self._integrations.values():
            maturity = integration.maturity_level
            maturity_counts[maturity] = maturity_counts.get(maturity, 0) + 1
            
            performance = integration.performance_tier
            performance_counts[performance] = performance_counts.get(performance, 0) + 1
            
        # Calculate success rates
        total_operations = self._stats['successful_operations'] + self._stats['failed_operations']
        success_rate = (self._stats['successful_operations'] / total_operations * 100) if total_operations > 0 else 0
        
        load_success_rate = (self._stats['loaded_adapters'] / (self._stats['loaded_adapters'] + self._stats['failed_loads']) * 100) if (self._stats['loaded_adapters'] + self._stats['failed_loads']) > 0 else 0
        
        avg_execution_time = (self._stats['total_execution_time'] / self._stats['successful_operations']) if self._stats['successful_operations'] > 0 else 0
        
        return {
            'overview': self._stats,
            'category_breakdown': category_counts,
            'maturity_breakdown': maturity_counts,
            'performance_breakdown': performance_counts,
            'success_rate': success_rate,
            'load_success_rate': load_success_rate,
            'average_execution_time': avg_execution_time,
            'loaded_adapters': list(self._loaded_adapters.keys())
        }
        
    def get_recommendations(self, 
                          use_case: str,
                          performance_requirement: str = "medium",
                          maturity_requirement: str = "stable") -> List[IntegrationInfo]:
        """Get integration recommendations for specific use case"""
        
        recommendations = []
        
        # Map use cases to categories
        use_case_mapping = {
            'document_extraction': [IntegrationCategory.CONTENT_EXTRACTION],
            'web_scraping': [IntegrationCategory.BROWSER_AUTOMATION, IntegrationCategory.CRAWLING_FRAMEWORKS],
            'proxy_rotation': [IntegrationCategory.PROXY_MANAGEMENT],
            'bot_avoidance': [IntegrationCategory.ANTI_BOT_DEFENSE],
            'url_discovery': [IntegrationCategory.URL_DISCOVERY],
            'comprehensive_crawling': [
                IntegrationCategory.CONTENT_EXTRACTION,
                IntegrationCategory.PROXY_MANAGEMENT,
                IntegrationCategory.URL_DISCOVERY,
                IntegrationCategory.ANTI_BOT_DEFENSE
            ]
        }
        
        relevant_categories = use_case_mapping.get(use_case, [])
        
        for category in relevant_categories:
            category_integrations = self.get_by_category(category)
            
            # Filter by requirements
            filtered = [
                integration for integration in category_integrations
                if integration.maturity_level == maturity_requirement
            ]
            
            # Sort by performance tier
            performance_priority = ['enterprise', 'high', 'medium', 'low']
            filtered.sort(key=lambda x: performance_priority.index(x.performance_tier))
            
            recommendations.extend(filtered)
            
        return recommendations[:5]  # Return top 5 recommendations
        
    async def health_check(self) -> Dict[str, Any]:
        """Perform health check on all loaded adapters"""
        
        health_results = {}
        
        for name, adapter in self._loaded_adapters.items():
            try:
                # Try to get stats or call a health method
                if hasattr(adapter, 'get_stats'):
                    if asyncio.iscoroutinefunction(adapter.get_stats):
                        stats = await adapter.get_stats()
                    else:
                        stats = adapter.get_stats()
                    health_results[name] = {'status': 'healthy', 'stats': stats}
                else:
                    health_results[name] = {'status': 'healthy', 'stats': {}}
                    
            except Exception as e:
                health_results[name] = {'status': 'unhealthy', 'error': str(e)}
                
        return {
            'overall_status': 'healthy' if all(r['status'] == 'healthy' for r in health_results.values()) else 'partial',
            'adapters': health_results,
            'total_loaded': len(self._loaded_adapters),
            'total_available': len(self._integrations)
        }
        
    async def cleanup(self):
        """Clean up all loaded adapters"""
        
        cleanup_results = {}
        
        for name, adapter in self._loaded_adapters.items():
            try:
                if hasattr(adapter, 'cleanup'):
                    if asyncio.iscoroutinefunction(adapter.cleanup):
                        await adapter.cleanup()
                    else:
                        adapter.cleanup()
                cleanup_results[name] = 'success'
            except Exception as e:
                cleanup_results[name] = f'error: {str(e)}'
                
        self._loaded_adapters.clear()
        self._stats['loaded_adapters'] = 0
        
        logger.info(f"🧹 Cleaned up {len(cleanup_results)} adapters")
        return cleanup_results

# Global registry instance
registry = GitHubIntegrationRegistry()

# Convenience functions
async def load_integration(name: str, config: Dict[str, Any] = None) -> Optional[Any]:
    """Load integration adapter"""
    return await registry.load_adapter(name, config)

async def execute_integration_operation(name: str, operation: str, *args, **kwargs) -> Dict[str, Any]:
    """Execute operation on integration"""
    return await registry.execute_operation(name, operation, *args, **kwargs)

def get_integration_info(name: str) -> Optional[IntegrationInfo]:
    """Get integration information"""
    return registry.get_integration(name)

def list_available_integrations(category: Optional[IntegrationCategory] = None) -> List[IntegrationInfo]:
    """List available integrations"""
    return registry.list_integrations(category=category)

def get_integration_recommendations(use_case: str) -> List[IntegrationInfo]:
    """Get integration recommendations"""
    return registry.get_recommendations(use_case)

async def perform_integration_health_check() -> Dict[str, Any]:
    """Perform health check on all integrations"""
    return await registry.health_check()

def get_integration_statistics() -> Dict[str, Any]:
    """Get comprehensive integration statistics"""
    return registry.get_integration_stats()

# Example usage and testing
async def main():
    """Example usage of the integration registry"""
    
    print("📋 GitHub Integration Registry - Revolutionary Ultimate System v4.0")
    print("=" * 80)
    
    # List all integrations
    all_integrations = list_available_integrations()
    print(f"Total integrations: {len(all_integrations)}")
    
    # Show category breakdown
    for category in IntegrationCategory:
        category_integrations = list_available_integrations(category)
        print(f"{category.value}: {len(category_integrations)}")
        
    print("\n" + "=" * 80)
    
    # Show recommendations
    recommendations = get_integration_recommendations('comprehensive_crawling')
    print(f"Recommendations for comprehensive crawling: {len(recommendations)}")
    for rec in recommendations:
        print(f"  - {rec.display_name} ({rec.category.value})")
        
    print("\n" + "=" * 80)
    
    # Load and test an adapter
    print("Testing Apache Tika adapter...")
    tika_adapter = await load_integration('apache_tika', {'enabled': True})
    
    if tika_adapter:
        print("✅ Apache Tika adapter loaded successfully")
    else:
        print("❌ Failed to load Apache Tika adapter")
        
    # Get statistics
    stats = get_integration_statistics()
    print(f"\nRegistry Statistics:")
    print(f"  - Total integrations: {stats['overview']['total_integrations']}")
    print(f"  - Loaded adapters: {stats['overview']['loaded_adapters']}")
    print(f"  - Success rate: {stats['success_rate']:.1f}%")
    
    # Health check
    health = await perform_integration_health_check()
    print(f"\nHealth Check: {health['overall_status']}")
    print(f"  - Total loaded: {health['total_loaded']}")
    print(f"  - Total available: {health['total_available']}")
    
    # Cleanup
    await registry.cleanup()
    print("\n🧹 Registry cleanup completed")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
