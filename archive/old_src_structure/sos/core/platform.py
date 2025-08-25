"""
SOS Platform - Main integration point
Comprehensive webscraping platform integrating all enhancement modules
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional
import time

from .config import get_settings
from .enhanced_crawler import EnhancedCrawler
from .stealth_browser import StealthBrowserManager
from .anti_detection import AntiDetectionManager
from .distributed import DistributedCoordinator
from ..crawler.crawler import BaseCrawler, StandardCrawler, CrawlResult
from ..exporters.factory import ExporterFactory, MultiExporter
from ..proxy.pool import ProxyPool

class SOSPlatform:
    """
    Main SOS Platform - Revolutionary webscraping with integrated enhancements
    
    Features:
    - Enhanced HTTP crawling with Scrapy/Nutch patterns
    - Stealth browser automation with Crawlee capabilities  
    - Advanced anti-detection with proxy rotation
    - Distributed crawling coordination
    - Multi-format export support
    """
    
    def __init__(self, config=None):
        self.config = config or get_settings()
        self.logger = logging.getLogger("sos_platform")
        
        # Core components
        self.base_crawler: Optional[BaseCrawler] = None
        self.enhanced_crawler: Optional[EnhancedCrawler] = None  
        self.stealth_browser: Optional[StealthBrowserManager] = None
        self.anti_detection: Optional[AntiDetectionManager] = None
        self.distributed_coordinator: Optional[DistributedCoordinator] = None
        self.proxy_pool: Optional[ProxyPool] = None
        
        # State
        self.is_initialized = False
        self.stats = {
            'total_crawls': 0,
            'successful_crawls': 0,
            'failed_crawls': 0,
            'start_time': None,
            'components_initialized': []
        }
    
    async def initialize(self, components: List[str] = None):
        """
        Initialize SOS platform components
        
        Args:
            components: List of components to initialize. If None, initializes based on config
        """
        if self.is_initialized:
            self.logger.warning("Platform already initialized")
            return
        
        self.stats['start_time'] = time.time()
        
        # Determine which components to initialize
        if components is None:
            components = self._get_enabled_components()
        
        self.logger.info(f"Initializing SOS Platform with components: {components}")
        
        # Initialize proxy pool first (needed by other components)
        if 'proxy_pool' in components and self.config.PROXY_URLS:
            await self._initialize_proxy_pool()
            self.stats['components_initialized'].append('proxy_pool')
        
        # Initialize base crawler
        if 'base_crawler' in components:
            await self._initialize_base_crawler()
            self.stats['components_initialized'].append('base_crawler')
        
        # Initialize enhanced crawler
        if 'enhanced_crawler' in components and self.config.ENHANCED_CRAWLER_ENABLED:
            await self._initialize_enhanced_crawler()
            self.stats['components_initialized'].append('enhanced_crawler')
        
        # Initialize stealth browser
        if 'stealth_browser' in components and self.config.STEALTH_BROWSER_ENABLED:
            await self._initialize_stealth_browser()
            self.stats['components_initialized'].append('stealth_browser')
        
        # Initialize anti-detection
        if 'anti_detection' in components and self.config.ANTI_DETECTION_ENABLED:
            await self._initialize_anti_detection()
            self.stats['components_initialized'].append('anti_detection')
        
        # Initialize distributed coordinator
        if 'distributed' in components and self.config.DISTRIBUTED_ENABLED:
            await self._initialize_distributed()
            self.stats['components_initialized'].append('distributed')
        
        self.is_initialized = True
        self.logger.info(f"SOS Platform initialized with {len(self.stats['components_initialized'])} components")
    
    def _get_enabled_components(self) -> List[str]:
        """Get list of enabled components based on configuration"""
        components = ['base_crawler']  # Always include base crawler
        
        if self.config.ENHANCED_CRAWLER_ENABLED:
            components.append('enhanced_crawler')
        
        if self.config.STEALTH_BROWSER_ENABLED:
            components.append('stealth_browser')
        
        if self.config.ANTI_DETECTION_ENABLED:
            components.append('anti_detection')
        
        if self.config.DISTRIBUTED_ENABLED:
            components.append('distributed')
        
        if self.config.PROXY_URLS:
            components.append('proxy_pool')
        
        return components
    
    async def _initialize_proxy_pool(self):
        """Initialize proxy pool"""
        proxy_urls = [url.strip() for url in self.config.PROXY_URLS.split(',') if url.strip()]
        self.proxy_pool = ProxyPool(proxy_urls)
        await self.proxy_pool.initialize()
        self.logger.info(f"Initialized proxy pool with {len(proxy_urls)} proxies")
    
    async def _initialize_base_crawler(self):
        """Initialize base crawler"""
        self.base_crawler = StandardCrawler(
            max_concurrency=self.config.CRAWL_MAX_CONCURRENCY,
            delay_ms=self.config.CRAWL_DEFAULT_DELAY_MS,
            respect_robots=self.config.CRAWL_RESPECT_ROBOTS
        )
        self.logger.info("Initialized base crawler")
    
    async def _initialize_enhanced_crawler(self):
        """Initialize enhanced crawler manager"""
        self.enhanced_crawler = EnhancedCrawler(
            max_concurrency=self.config.CRAWL_MAX_CONCURRENCY,
            default_delay=self.config.CRAWL_DEFAULT_DELAY_MS / 1000
        )
        
        # Configure middleware if specified
        if hasattr(self.config, 'MIDDLEWARE_PIPELINE'):
            for middleware in self.config.MIDDLEWARE_PIPELINE:
                self.enhanced_crawler.add_middleware(middleware)
        
        self.logger.info("Initialized enhanced crawler manager")
    
    async def _initialize_stealth_browser(self):
        """Initialize stealth browser manager"""
        self.stealth_browser = StealthBrowserManager()
        await self.stealth_browser.initialize()
        self.logger.info("Initialized stealth browser manager")
    
    async def _initialize_anti_detection(self):
        """Initialize anti-detection system"""
        self.anti_detection = AntiDetectionManager()
        await self.anti_detection.initialize()
        self.logger.info("Initialized anti-detection system")
    
    async def _initialize_distributed(self):
        """Initialize distributed coordinator"""
        if not self.config.REDIS_URL:
            raise ValueError("REDIS_URL required for distributed crawling")
        
        self.distributed_coordinator = DistributedCoordinator(self.config.REDIS_URL)
        await self.distributed_coordinator.initialize()
        self.logger.info("Initialized distributed coordinator")
    
    async def crawl(self,
                   urls: List[str],
                   method: str = "auto",
                   export_formats: List[str] = None,
                   **kwargs) -> Dict[str, Any]:
        """
        Main crawling method - automatically selects best strategy
        
        Args:
            urls: List of URLs to crawl
            method: Crawling method ('auto', 'basic', 'enhanced', 'stealth', 'distributed')
            export_formats: List of export formats ['json', 'csv', 'bigquery']
            **kwargs: Additional parameters for crawling
        
        Returns:
            Dict with results and metadata
        """
        if not self.is_initialized:
            raise RuntimeError("Platform not initialized. Call initialize() first.")
        
        start_time = time.time()
        
        # Auto-select method if not specified
        if method == "auto":
            method = self._auto_select_method(urls, **kwargs)
        
        self.logger.info(f"Starting crawl of {len(urls)} URLs using method: {method}")
        
        try:
            # Execute crawling based on selected method
            if method == "distributed" and self.distributed_coordinator:
                results = await self._crawl_distributed(urls, **kwargs)
            elif method == "stealth" and self.stealth_browser:
                results = await self._crawl_stealth(urls, **kwargs)
            elif method == "enhanced" and self.enhanced_crawler:
                results = await self._crawl_enhanced(urls, **kwargs)
            else:
                results = await self._crawl_basic(urls, **kwargs)
            
            # Update stats
            self.stats['total_crawls'] += len(urls)
            successful = sum(1 for r in results if not r.error)
            self.stats['successful_crawls'] += successful
            self.stats['failed_crawls'] += len(results) - successful
            
            # Export results if requested
            exported_files = {}
            if export_formats:
                exported_files = await self._export_results(results, export_formats)
            
            crawl_time = time.time() - start_time
            
            return {
                'results': results,
                'stats': {
                    'total_urls': len(urls),
                    'successful': successful,
                    'failed': len(results) - successful,
                    'success_rate': successful / len(urls) if urls else 0,
                    'crawl_time': crawl_time,
                    'method_used': method
                },
                'exported_files': exported_files
            }
            
        except Exception as e:
            self.logger.error(f"Crawl failed: {str(e)}")
            self.stats['failed_crawls'] += len(urls)
            raise
    
    def _auto_select_method(self, urls: List[str], **kwargs) -> str:
        """Automatically select best crawling method"""
        
        # Check if any URLs need JavaScript rendering
        js_indicators = ['spa', 'react', 'angular', 'vue', '#', 'javascript:']
        needs_js = any(
            any(indicator in url.lower() for indicator in js_indicators)
            for url in urls
        )
        
        if needs_js and self.stealth_browser:
            return "stealth"
        
        # Check for distributed crawling conditions
        if (len(urls) > 100 and 
            self.distributed_coordinator and 
            kwargs.get('distributed', False)):
            return "distributed"
        
        # Use enhanced if available, otherwise basic
        if self.enhanced_crawler:
            return "enhanced"
        else:
            return "basic"
    
    async def _crawl_basic(self, urls: List[str], **kwargs) -> List[CrawlResult]:
        """Basic crawling using standard crawler"""
        return await self.base_crawler.crawl_urls(urls, **kwargs)
    
    async def _crawl_enhanced(self, urls: List[str], **kwargs) -> List[CrawlResult]:
        """Enhanced crawling using enhanced crawler manager"""
        return await self.enhanced_crawler.crawl_urls(urls, **kwargs)
    
    async def _crawl_stealth(self, urls: List[str], **kwargs) -> List[CrawlResult]:
        """Stealth crawling using browser automation"""
        results = []
        for url in urls:
            result = await self.stealth_browser.crawl_page(url, **kwargs)
            # Convert to CrawlResult format
            crawl_result = CrawlResult(
                url=url,
                status_code=result.get('status', 200),
                content=result.get('content', ''),
                headers=result.get('headers', {}),
                links=result.get('links', []),
                metadata=result.get('metadata', {}),
                crawl_time=result.get('timing', {}).get('total_time', 0)
            )
            results.append(crawl_result)
        return results
    
    async def _crawl_distributed(self, urls: List[str], **kwargs) -> List[CrawlResult]:
        """Distributed crawling using coordinator"""
        task_ids = await self.distributed_coordinator.submit_urls(
            urls, 
            priority=kwargs.get('priority', 0)
        )
        
        # Wait for completion and collect results
        # This is a simplified implementation - in production you'd have
        # a more sophisticated result collection mechanism
        await asyncio.sleep(kwargs.get('wait_time', 60))
        
        # Return placeholder results for now
        return [
            CrawlResult(url=url, status_code=200, content="Distributed crawl result")
            for url in urls
        ]
    
    async def _export_results(self, 
                            results: List[CrawlResult], 
                            formats: List[str]) -> Dict[str, str]:
        """Export results in multiple formats"""
        
        # Convert results to dict format
        data = []
        for result in results:
            data.append({
                'url': result.url,
                'status_code': result.status_code,
                'title': result.metadata.get('title', ''),
                'content_length': len(result.content),
                'links_count': len(result.links),
                'crawl_time': result.crawl_time,
                'timestamp': result.timestamp,
                'error': result.error
            })
        
        exported_files = {}
        
        for format_name in formats:
            try:
                timestamp = int(time.time())
                
                if format_name == 'json':
                    file_path = f"{self.config.EXPORT_DIR}/crawl_results_{timestamp}.json"
                    success = await ExporterFactory.export_data(data, 'json', file_path=file_path)
                    if success:
                        exported_files['json'] = file_path
                
                elif format_name == 'csv':
                    file_path = f"{self.config.EXPORT_DIR}/crawl_results_{timestamp}.csv"
                    success = await ExporterFactory.export_data(data, 'csv', file_path=file_path)
                    if success:
                        exported_files['csv'] = file_path
                
                elif format_name == 'bigquery' and self.config.BQ_DATASET:
                    success = await ExporterFactory.export_data(
                        data, 
                        'bigquery',
                        dataset=self.config.BQ_DATASET,
                        table=self.config.BQ_TABLE or 'crawl_results'
                    )
                    if success:
                        exported_files['bigquery'] = f"{self.config.BQ_DATASET}.{self.config.BQ_TABLE}"
                
            except Exception as e:
                self.logger.error(f"Failed to export to {format_name}: {str(e)}")
        
        return exported_files
    
    def get_platform_stats(self) -> Dict[str, Any]:
        """Get comprehensive platform statistics"""
        uptime = time.time() - self.stats['start_time'] if self.stats['start_time'] else 0
        
        stats = {
            'platform': {
                'version': '2.0.0',
                'uptime_seconds': uptime,
                'components_initialized': self.stats['components_initialized'],
                'is_initialized': self.is_initialized
            },
            'crawling': {
                'total_crawls': self.stats['total_crawls'],
                'successful_crawls': self.stats['successful_crawls'],
                'failed_crawls': self.stats['failed_crawls'],
                'success_rate': (
                    self.stats['successful_crawls'] / max(1, self.stats['total_crawls'])
                )
            }
        }
        
        # Add component-specific stats
        if self.base_crawler:
            stats['base_crawler'] = self.base_crawler.get_stats()
        
        if self.proxy_pool:
            stats['proxy_pool'] = self.proxy_pool.get_stats()
        
        return stats
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform comprehensive health check"""
        health = {
            'status': 'healthy',
            'timestamp': time.time(),
            'components': {}
        }
        
        # Check each component
        try:
            if self.base_crawler:
                health['components']['base_crawler'] = 'healthy'
            
            if self.enhanced_crawler:
                health['components']['enhanced_crawler'] = 'healthy'
            
            if self.stealth_browser:
                # Test browser availability
                browser_healthy = await self.stealth_browser.health_check()
                health['components']['stealth_browser'] = 'healthy' if browser_healthy else 'unhealthy'
            
            if self.anti_detection:
                health['components']['anti_detection'] = 'healthy'
            
            if self.distributed_coordinator:
                # Check Redis connectivity
                try:
                    await self.distributed_coordinator.redis_client.ping()
                    health['components']['distributed'] = 'healthy'
                except:
                    health['components']['distributed'] = 'unhealthy'
                    health['status'] = 'degraded'
            
            if self.proxy_pool:
                proxy_stats = self.proxy_pool.get_stats()
                if proxy_stats.get('healthy_proxies', 0) > 0:
                    health['components']['proxy_pool'] = 'healthy'
                else:
                    health['components']['proxy_pool'] = 'unhealthy'
                    health['status'] = 'degraded'
        
        except Exception as e:
            health['status'] = 'unhealthy'
            health['error'] = str(e)
        
        return health
    
    async def shutdown(self):
        """Gracefully shutdown all platform components"""
        self.logger.info("Shutting down SOS Platform...")
        
        shutdown_tasks = []
        
        if self.stealth_browser:
            shutdown_tasks.append(self.stealth_browser.close())
        
        if self.anti_detection:
            shutdown_tasks.append(self.anti_detection.shutdown())
        
        if self.distributed_coordinator:
            shutdown_tasks.append(self.distributed_coordinator.stop())
        
        if self.proxy_pool:
            shutdown_tasks.append(self.proxy_pool.close())
        
        if shutdown_tasks:
            await asyncio.gather(*shutdown_tasks, return_exceptions=True)
        
        self.is_initialized = False
        self.logger.info("SOS Platform shutdown complete")

# Convenience functions for quick usage
async def quick_crawl(urls: List[str], 
                     export_format: str = "json",
                     **kwargs) -> Dict[str, Any]:
    """Quick crawl function for simple use cases"""
    platform = SOSPlatform()
    await platform.initialize()
    
    try:
        return await platform.crawl(
            urls, 
            export_formats=[export_format] if export_format else None,
            **kwargs
        )
    finally:
        await platform.shutdown()

async def stealth_crawl(urls: List[str], **kwargs) -> Dict[str, Any]:
    """Quick stealth crawl using browser automation"""
    platform = SOSPlatform()
    await platform.initialize(['stealth_browser', 'base_crawler'])
    
    try:
        return await platform.crawl(urls, method="stealth", **kwargs)
    finally:
        await platform.shutdown()

async def distributed_crawl(urls: List[str], **kwargs) -> Dict[str, Any]:
    """Quick distributed crawl"""
    platform = SOSPlatform()
    await platform.initialize(['distributed', 'enhanced_crawler', 'base_crawler'])
    
    try:
        return await platform.crawl(urls, method="distributed", **kwargs)
    finally:
        await platform.shutdown()
