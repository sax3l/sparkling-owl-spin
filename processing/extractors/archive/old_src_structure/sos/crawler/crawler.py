"""
Base Crawler - Core crawling interface
Unified interface for all crawling strategies and methods
"""

import asyncio
import logging
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, field
from enum import Enum
import time
from urllib.parse import urljoin, urlparse

from ..core.config import get_settings
from .fetcher import Fetcher
from .politeness import PolitenessManager
from .robots import RobotsChecker

class CrawlStrategy(Enum):
    BFS = "breadth_first"
    DFS = "depth_first" 
    PRIORITY = "priority_based"
    ADAPTIVE = "adaptive"

@dataclass
class CrawlResult:
    """Result from crawling a single URL"""
    url: str
    status_code: int = 0
    content: str = ""
    headers: Dict[str, str] = field(default_factory=dict)
    links: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    error: Optional[str] = None
    crawl_time: float = 0
    timestamp: float = field(default_factory=time.time)

@dataclass 
class CrawlRequest:
    """Request for crawling a URL"""
    url: str
    priority: int = 0
    depth: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)
    headers: Dict[str, str] = field(default_factory=dict)
    callback: Optional[Callable] = None
    retries: int = 0
    max_retries: int = 3

class BaseCrawler(ABC):
    """Abstract base crawler class"""
    
    def __init__(self, 
                 max_concurrency: int = 5,
                 delay_ms: int = 1000,
                 respect_robots: bool = True,
                 strategy: CrawlStrategy = CrawlStrategy.BFS):
        
        self.max_concurrency = max_concurrency
        self.delay_ms = delay_ms
        self.respect_robots = respect_robots
        self.strategy = strategy
        self.settings = get_settings()
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # Core components
        self.fetcher = Fetcher()
        self.politeness_manager = PolitenessManager(delay_ms=delay_ms)
        self.robots_checker = RobotsChecker() if respect_robots else None
        
        # State
        self.is_running = False
        self.total_requests = 0
        self.successful_requests = 0
        self.failed_requests = 0
        
        # Hooks
        self.request_hooks: List[Callable] = []
        self.response_hooks: List[Callable] = []
        self.error_hooks: List[Callable] = []
    
    @abstractmethod
    async def crawl_url(self, request: CrawlRequest) -> CrawlResult:
        """Crawl a single URL"""
        pass
    
    @abstractmethod  
    async def crawl_urls(self, urls: List[str], **kwargs) -> List[CrawlResult]:
        """Crawl multiple URLs"""
        pass
    
    async def add_request_hook(self, hook: Callable):
        """Add request preprocessing hook"""
        self.request_hooks.append(hook)
    
    async def add_response_hook(self, hook: Callable):
        """Add response postprocessing hook"""
        self.response_hooks.append(hook)
    
    async def add_error_hook(self, hook: Callable):
        """Add error handling hook"""
        self.error_hooks.append(hook)
    
    async def _execute_request_hooks(self, request: CrawlRequest) -> CrawlRequest:
        """Execute all request hooks"""
        for hook in self.request_hooks:
            try:
                request = await hook(request) if asyncio.iscoroutinefunction(hook) else hook(request)
            except Exception as e:
                self.logger.warning(f"Request hook failed: {str(e)}")
        return request
    
    async def _execute_response_hooks(self, result: CrawlResult) -> CrawlResult:
        """Execute all response hooks"""
        for hook in self.response_hooks:
            try:
                result = await hook(result) if asyncio.iscoroutinefunction(hook) else hook(result)
            except Exception as e:
                self.logger.warning(f"Response hook failed: {str(e)}")
        return result
    
    async def _execute_error_hooks(self, error: Exception, request: CrawlRequest):
        """Execute all error hooks"""
        for hook in self.error_hooks:
            try:
                await hook(error, request) if asyncio.iscoroutinefunction(hook) else hook(error, request)
            except Exception as e:
                self.logger.warning(f"Error hook failed: {str(e)}")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get crawler statistics"""
        success_rate = self.successful_requests / max(1, self.total_requests)
        return {
            'total_requests': self.total_requests,
            'successful_requests': self.successful_requests,
            'failed_requests': self.failed_requests,
            'success_rate': success_rate,
            'strategy': self.strategy.value,
            'max_concurrency': self.max_concurrency,
            'delay_ms': self.delay_ms
        }

class StandardCrawler(BaseCrawler):
    """Standard HTTP-based crawler implementation"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._semaphore = asyncio.Semaphore(self.max_concurrency)
    
    async def crawl_url(self, request: CrawlRequest) -> CrawlResult:
        """Crawl a single URL with all standard features"""
        start_time = time.time()
        
        try:
            # Execute request hooks
            request = await self._execute_request_hooks(request)
            
            # Check robots.txt if enabled
            if self.robots_checker:
                can_fetch = await self.robots_checker.can_fetch(request.url)
                if not can_fetch:
                    return CrawlResult(
                        url=request.url,
                        error="Blocked by robots.txt",
                        crawl_time=time.time() - start_time
                    )
            
            # Apply politeness delay
            await self.politeness_manager.wait_for_domain(request.url)
            
            # Fetch the URL
            async with self._semaphore:
                response = await self.fetcher.fetch(request.url, headers=request.headers)
                
                result = CrawlResult(
                    url=request.url,
                    status_code=response.get('status_code', 0),
                    content=response.get('content', ''),
                    headers=response.get('headers', {}),
                    links=response.get('links', []),
                    metadata=response.get('metadata', {}),
                    crawl_time=time.time() - start_time
                )
            
            # Execute response hooks
            result = await self._execute_response_hooks(result)
            
            self.successful_requests += 1
            return result
            
        except Exception as e:
            self.logger.error(f"Failed to crawl {request.url}: {str(e)}")
            
            # Execute error hooks
            await self._execute_error_hooks(e, request)
            
            self.failed_requests += 1
            return CrawlResult(
                url=request.url,
                error=str(e),
                crawl_time=time.time() - start_time
            )
        
        finally:
            self.total_requests += 1
    
    async def crawl_urls(self, urls: List[str], **kwargs) -> List[CrawlResult]:
        """Crawl multiple URLs concurrently"""
        
        # Convert URLs to requests
        requests = []
        for i, url in enumerate(urls):
            request = CrawlRequest(
                url=url,
                priority=kwargs.get('priority', 0),
                depth=kwargs.get('depth', 0),
                metadata=kwargs.get('metadata', {}),
                headers=kwargs.get('headers', {})
            )
            requests.append(request)
        
        # Execute crawling based on strategy
        if self.strategy == CrawlStrategy.BFS:
            return await self._crawl_bfs(requests)
        elif self.strategy == CrawlStrategy.DFS:
            return await self._crawl_dfs(requests)
        elif self.strategy == CrawlStrategy.PRIORITY:
            return await self._crawl_priority(requests)
        else:
            # Default concurrent execution
            tasks = [self.crawl_url(request) for request in requests]
            return await asyncio.gather(*tasks, return_exceptions=False)
    
    async def _crawl_bfs(self, requests: List[CrawlRequest]) -> List[CrawlResult]:
        """Breadth-first crawling"""
        results = []
        queue = requests.copy()
        
        while queue:
            # Process batch of URLs at current depth
            current_batch = queue[:self.max_concurrency]
            queue = queue[self.max_concurrency:]
            
            # Crawl current batch
            tasks = [self.crawl_url(request) for request in current_batch]
            batch_results = await asyncio.gather(*tasks, return_exceptions=False)
            results.extend(batch_results)
        
        return results
    
    async def _crawl_dfs(self, requests: List[CrawlRequest]) -> List[CrawlResult]:
        """Depth-first crawling"""
        results = []
        
        for request in requests:
            result = await self.crawl_url(request)
            results.append(result)
            
            # Small delay between sequential requests
            await asyncio.sleep(self.delay_ms / 1000)
        
        return results
    
    async def _crawl_priority(self, requests: List[CrawlRequest]) -> List[CrawlResult]:
        """Priority-based crawling"""
        # Sort by priority (higher first)
        sorted_requests = sorted(requests, key=lambda x: x.priority, reverse=True)
        
        # Process in priority order with concurrency
        results = []
        semaphore = asyncio.Semaphore(self.max_concurrency)
        
        async def process_request(request):
            async with semaphore:
                return await self.crawl_url(request)
        
        tasks = [process_request(request) for request in sorted_requests]
        results = await asyncio.gather(*tasks, return_exceptions=False)
        
        return results

# Factory function for creating crawlers
def create_crawler(crawler_type: str = "standard", **kwargs) -> BaseCrawler:
    """Factory function to create different types of crawlers"""
    
    if crawler_type.lower() == "standard":
        return StandardCrawler(**kwargs)
    else:
        raise ValueError(f"Unknown crawler type: {crawler_type}")

# Convenience functions
async def crawl_single_url(url: str, **kwargs) -> CrawlResult:
    """Convenience function to crawl a single URL"""
    crawler = create_crawler(**kwargs)
    request = CrawlRequest(url=url)
    return await crawler.crawl_url(request)

async def crawl_multiple_urls(urls: List[str], **kwargs) -> List[CrawlResult]:
    """Convenience function to crawl multiple URLs"""
    crawler = create_crawler(**kwargs)
    return await crawler.crawl_urls(urls, **kwargs)
