#!/usr/bin/env python3
"""
GitHub Repository Adapter Registry - Revolutionary Ultimate System v4.0
Central registry for managing all GitHub repository integrations
"""

import asyncio
import logging
from typing import Dict, Any, Optional, List, Union, Type
from dataclasses import dataclass, asdict
import importlib
import inspect

logger = logging.getLogger(__name__)

@dataclass
class AdapterInfo:
    """Information about a registered adapter"""
    name: str
    category: str
    priority: int
    description: str
    github_repo: str
    adapter_class: Type
    config_template: Dict[str, Any]
    dependencies: List[str]
    enabled: bool = True
    initialized: bool = False

class GitHubAdapterRegistry:
    """
    Central registry for managing all GitHub repository adapters.
    
    Features:
    - Centralized adapter registration and discovery
    - Category-based organization (anti-bot, content extraction, etc.)
    - Priority-based loading and execution
    - Configuration management
    - Dependency tracking
    - Health monitoring
    """
    
    def __init__(self):
        self.adapters: Dict[str, AdapterInfo] = {}
        self.instances: Dict[str, Any] = {}
        self.categories = {
            'anti_bot_defense': [],
            'content_extraction': [],
            'url_discovery': [],
            'proxy_management': [],
            'browser_automation': [],
            'captcha_solving': [],
            'osint_intelligence': [],
            'advanced_crawlers': [],
            'specialized_tools': []
        }
        
    def register_adapter(self, adapter_info: AdapterInfo) -> bool:
        """Register a new adapter"""
        
        try:
            # Validate adapter class
            if not hasattr(adapter_info.adapter_class, '__call__'):
                logger.error(f"❌ Invalid adapter class for {adapter_info.name}")
                return False
                
            # Register in main registry
            self.adapters[adapter_info.name] = adapter_info
            
            # Add to category
            if adapter_info.category in self.categories:
                self.categories[adapter_info.category].append(adapter_info.name)
                
            logger.info(f"✅ Registered adapter: {adapter_info.name} ({adapter_info.category})")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to register adapter {adapter_info.name}: {str(e)}")
            return False
            
    def get_adapter_info(self, name: str) -> Optional[AdapterInfo]:
        """Get adapter information"""
        return self.adapters.get(name)
        
    def get_adapters_by_category(self, category: str) -> List[AdapterInfo]:
        """Get all adapters in a category"""
        adapter_names = self.categories.get(category, [])
        return [self.adapters[name] for name in adapter_names if name in self.adapters]
        
    def get_adapters_by_priority(self, category: Optional[str] = None) -> List[AdapterInfo]:
        """Get adapters sorted by priority"""
        if category:
            adapters = self.get_adapters_by_category(category)
        else:
            adapters = list(self.adapters.values())
            
        return sorted(adapters, key=lambda x: x.priority)
        
    async def initialize_adapter(self, name: str, config: Dict[str, Any]) -> bool:
        """Initialize a specific adapter"""
        
        adapter_info = self.adapters.get(name)
        if not adapter_info:
            logger.error(f"❌ Adapter {name} not found")
            return False
            
        if name in self.instances:
            logger.warning(f"⚠️ Adapter {name} already initialized")
            return True
            
        try:
            logger.info(f"🚀 Initializing adapter: {name}")
            
            # Create adapter instance
            instance = adapter_info.adapter_class(config)
            
            # Initialize if method exists
            if hasattr(instance, 'initialize'):
                await instance.initialize()
                
            self.instances[name] = instance
            adapter_info.initialized = True
            
            logger.info(f"✅ Adapter initialized: {name}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize adapter {name}: {str(e)}")
            return False
            
    async def initialize_category(self, category: str, 
                                config_overrides: Optional[Dict[str, Dict[str, Any]]] = None) -> Dict[str, bool]:
        """Initialize all adapters in a category"""
        
        adapters = self.get_adapters_by_priority(category)
        results = {}
        
        for adapter_info in adapters:
            if not adapter_info.enabled:
                continue
                
            # Get config
            config = adapter_info.config_template.copy()
            if config_overrides and adapter_info.name in config_overrides:
                config.update(config_overrides[adapter_info.name])
                
            # Initialize
            success = await self.initialize_adapter(adapter_info.name, config)
            results[adapter_info.name] = success
            
        return results
        
    async def get_adapter(self, name: str) -> Optional[Any]:
        """Get an initialized adapter instance"""
        return self.instances.get(name)
        
    async def call_adapter_method(self, name: str, method: str, 
                                *args, **kwargs) -> Any:
        """Call a method on an adapter"""
        
        instance = await self.get_adapter(name)
        if not instance:
            raise ValueError(f"Adapter {name} not initialized")
            
        if not hasattr(instance, method):
            raise AttributeError(f"Adapter {name} has no method {method}")
            
        method_obj = getattr(instance, method)
        
        # Call method (handle both sync and async)
        if inspect.iscoroutinefunction(method_obj):
            return await method_obj(*args, **kwargs)
        else:
            return method_obj(*args, **kwargs)
            
    def get_registry_stats(self) -> Dict[str, Any]:
        """Get registry statistics"""
        
        stats = {
            'total_adapters': len(self.adapters),
            'initialized_adapters': len(self.instances),
            'categories': {},
            'by_status': {
                'enabled': 0,
                'disabled': 0,
                'initialized': 0,
                'not_initialized': 0
            }
        }
        
        # Category stats
        for category, adapter_names in self.categories.items():
            stats['categories'][category] = {
                'total': len(adapter_names),
                'enabled': sum(1 for name in adapter_names 
                             if name in self.adapters and self.adapters[name].enabled),
                'initialized': sum(1 for name in adapter_names 
                                 if name in self.instances)
            }
            
        # Status stats
        for adapter_info in self.adapters.values():
            if adapter_info.enabled:
                stats['by_status']['enabled'] += 1
            else:
                stats['by_status']['disabled'] += 1
                
            if adapter_info.initialized:
                stats['by_status']['initialized'] += 1
            else:
                stats['by_status']['not_initialized'] += 1
                
        return stats
        
    async def cleanup_adapter(self, name: str) -> bool:
        """Clean up a specific adapter"""
        
        instance = self.instances.get(name)
        if not instance:
            return True
            
        try:
            if hasattr(instance, 'cleanup'):
                await instance.cleanup()
                
            del self.instances[name]
            
            if name in self.adapters:
                self.adapters[name].initialized = False
                
            logger.info(f"🧹 Cleaned up adapter: {name}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to cleanup adapter {name}: {str(e)}")
            return False
            
    async def cleanup_all(self) -> Dict[str, bool]:
        """Clean up all adapters"""
        
        results = {}
        
        for name in list(self.instances.keys()):
            results[name] = await self.cleanup_adapter(name)
            
        return results

# Global registry instance
_global_registry = GitHubAdapterRegistry()

def get_global_registry() -> GitHubAdapterRegistry:
    """Get the global adapter registry"""
    return _global_registry

def register_github_adapters():
    """Register all available GitHub adapters"""
    
    registry = get_global_registry()
    
    # Anti-bot defense adapters
    
    # FlareSolverr adapter
    try:
        from .flaresolverr_adapter import create_flaresolverr_adapter
        registry.register_adapter(AdapterInfo(
            name='flaresolverr',
            category='anti_bot_defense',
            priority=1,
            description='FlareSolverr proxy server for CloudFlare bypass',
            github_repo='https://github.com/FlareSolverr/FlareSolverr',
            adapter_class=create_flaresolverr_adapter,
            config_template={
                'enabled': True,
                'endpoint': 'http://localhost:8191/v1',
                'timeout': 60,
                'max_timeout': 120,
                'session_ttl': 600
            },
            dependencies=['aiohttp', 'requests']
        ))
    except ImportError as e:
        logger.warning(f"⚠️ FlareSolverr adapter not available: {e}")
        
    # Undetected Chrome adapter
    try:
        from .undetected_chrome_adapter import create_undetected_chrome_adapter
        registry.register_adapter(AdapterInfo(
            name='undetected_chrome',
            category='anti_bot_defense',
            priority=2,
            description='Undetected ChromeDriver for stealth automation',
            github_repo='https://github.com/ultrafunkamsterdam/undetected-chromedriver',
            adapter_class=create_undetected_chrome_adapter,
            config_template={
                'enabled': True,
                'headless': True,
                'no_sandbox': True,
                'page_load_timeout': 30,
                'implicit_wait': 10
            },
            dependencies=['undetected-chromedriver', 'selenium']
        ))
    except ImportError as e:
        logger.warning(f"⚠️ Undetected Chrome adapter not available: {e}")
        
    # CloudScraper adapter
    try:
        from .cloudscraper_adapter import create_cloudscraper_adapter
        registry.register_adapter(AdapterInfo(
            name='cloudscraper',
            category='anti_bot_defense',
            priority=3,
            description='CloudScraper for CloudFlare bypass',
            github_repo='https://github.com/venomous/cloudscraper',
            adapter_class=create_cloudscraper_adapter,
            config_template={
                'enabled': True,
                'browser': 'chrome',
                'delay': 1.0,
                'timeout': 30,
                'max_retries': 3
            },
            dependencies=['cloudscraper', 'requests']
        ))
    except ImportError as e:
        logger.warning(f"⚠️ CloudScraper adapter not available: {e}")
        
    # CloudFlare-Scrape adapter
    try:
        from .cloudflare_scrape_adapter import create_cloudflare_scrape_adapter
        registry.register_adapter(AdapterInfo(
            name='cloudflare_scrape',
            category='anti_bot_defense',
            priority=4,
            description='Node.js CloudFlare bypass with Puppeteer',
            github_repo='https://github.com/cloudflarejs/cloudflare-scraper',
            adapter_class=create_cloudflare_scrape_adapter,
            config_template={
                'enabled': True,
                'nodejs_path': 'node',
                'timeout': 60,
                'auto_install': True,
                'headless': True
            },
            dependencies=['aiofiles']
        ))
    except ImportError as e:
        logger.warning(f"⚠️ CloudFlare-Scrape adapter not available: {e}")
        
    # Content extraction adapters
    
    # Trafilatura adapter
    try:
        from .trafilatura_adapter import create_trafilatura_adapter
        registry.register_adapter(AdapterInfo(
            name='trafilatura',
            category='content_extraction',
            priority=1,
            description='Trafilatura for advanced web content extraction',
            github_repo='https://github.com/adbar/trafilatura',
            adapter_class=create_trafilatura_adapter,
            config_template={
                'enabled': True,
                'include_images': True,
                'include_links': True,
                'include_tables': True,
                'extract_metadata': True,
                'favor_recall': True
            },
            dependencies=['trafilatura', 'lxml', 'beautifulsoup4']
        ))
    except ImportError as e:
        logger.warning(f"⚠️ Trafilatura adapter not available: {e}")
        
    # URL discovery adapters
    
    # Katana adapter
    try:
        from .katana_adapter import create_katana_adapter
        registry.register_adapter(AdapterInfo(
            name='katana',
            category='url_discovery',
            priority=1,
            description='Katana for advanced URL discovery and crawling',
            github_repo='https://github.com/projectdiscovery/katana',
            adapter_class=create_katana_adapter,
            config_template={
                'enabled': True,
                'max_depth': 3,
                'max_urls': 1000,
                'js_crawling': True,
                'xhr_extraction': True,
                'form_extraction': True
            },
            dependencies=[]
        ))
    except ImportError as e:
        logger.warning(f"⚠️ Katana adapter not available: {e}")
        
    logger.info(f"✅ Registered {len(registry.adapters)} GitHub adapters")

# High-level interface functions

async def get_page_with_best_method(url: str, **kwargs) -> Dict[str, Any]:
    """Get page using the best available method"""
    
    registry = get_global_registry()
    
    # Try anti-bot methods in priority order
    anti_bot_adapters = registry.get_adapters_by_priority('anti_bot_defense')
    
    for adapter_info in anti_bot_adapters:
        if not adapter_info.enabled or adapter_info.name not in registry.instances:
            continue
            
        try:
            instance = registry.instances[adapter_info.name]
            
            # Try different method names based on adapter
            method_mapping = {
                'flaresolverr': 'solve_challenge',
                'undetected_chrome': 'get_page_stealth',
                'cloudscraper': 'get_page_cloudflare',
                'cloudflare_scrape': 'get_page_bypass'
            }
            
            method_name = method_mapping.get(adapter_info.name)
            if method_name and hasattr(instance, method_name):
                result = await registry.call_adapter_method(
                    adapter_info.name, method_name, url, **kwargs
                )
                
                if result.get('success'):
                    logger.info(f"✅ Success with {adapter_info.name}")
                    return result
                    
        except Exception as e:
            logger.error(f"❌ {adapter_info.name} failed: {str(e)}")
            continue
            
    # Fallback to regular request
    import aiohttp
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url, timeout=30) as response:
                content = await response.text()
                return {
                    'success': True,
                    'url': str(response.url),
                    'status_code': response.status,
                    'html_content': content,
                    'method': 'aiohttp'
                }
        except Exception as e:
            return {
                'success': False,
                'url': url,
                'error': str(e),
                'method': 'aiohttp'
            }

async def extract_content_with_best_method(html_content: str, url: str, 
                                         **kwargs) -> Dict[str, Any]:
    """Extract content using the best available method"""
    
    registry = get_global_registry()
    
    # Try content extraction methods
    extraction_adapters = registry.get_adapters_by_priority('content_extraction')
    
    for adapter_info in extraction_adapters:
        if not adapter_info.enabled or adapter_info.name not in registry.instances:
            continue
            
        try:
            result = await registry.call_adapter_method(
                adapter_info.name, 'extract_article_content', 
                html_content, url, **kwargs
            )
            
            if result.get('success'):
                logger.info(f"✅ Content extracted with {adapter_info.name}")
                return result
                
        except Exception as e:
            logger.error(f"❌ {adapter_info.name} failed: {str(e)}")
            continue
            
    # Fallback to basic extraction
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Remove script and style elements
    for script in soup(["script", "style"]):
        script.decompose()
        
    text = soup.get_text()
    lines = (line.strip() for line in text.splitlines())
    chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
    text = ' '.join(chunk for chunk in chunks if chunk)
    
    return {
        'success': True,
        'url': url,
        'title': soup.title.string if soup.title else '',
        'text_content': text,
        'method': 'beautifulsoup'
    }

async def discover_urls_with_best_method(target: str, **kwargs) -> Dict[str, Any]:
    """Discover URLs using the best available method"""
    
    registry = get_global_registry()
    
    # Try URL discovery methods
    discovery_adapters = registry.get_adapters_by_priority('url_discovery')
    
    for adapter_info in discovery_adapters:
        if not adapter_info.enabled or adapter_info.name not in registry.instances:
            continue
            
        try:
            result = await registry.call_adapter_method(
                adapter_info.name, 'discover_urls_comprehensive', 
                target, **kwargs
            )
            
            if result.get('success'):
                logger.info(f"✅ URLs discovered with {adapter_info.name}")
                return result
                
        except Exception as e:
            logger.error(f"❌ {adapter_info.name} failed: {str(e)}")
            continue
            
    # Fallback to basic crawling
    return {
        'success': False,
        'target': target,
        'error': 'No URL discovery methods available',
        'method': 'none'
    }

# Auto-register adapters when module is imported
try:
    register_github_adapters()
except Exception as e:
    logger.error(f"❌ Failed to register adapters: {str(e)}")

# Example usage
async def main():
    """Example usage of the registry"""
    
    registry = get_global_registry()
    
    # Initialize anti-bot category
    await registry.initialize_category('anti_bot_defense')
    
    # Test with best available method
    result = await get_page_with_best_method('https://example.com')
    print(f"Page result: {result.get('success', False)}")
    
    # Get stats
    stats = registry.get_registry_stats()
    print(f"Registry stats: {stats}")
    
    # Cleanup
    await registry.cleanup_all()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
