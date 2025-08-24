"""
Sparkling Owl Spin Fetcher Module
=================================

Provides HTTP/HTTPS content fetching capabilities with advanced features
for the Sparkling Owl Spin webscraping platform.

This module includes:
• Advanced HTTP client with retry logic
• Connection pooling and session management  
• Proxy support with rotation capabilities
• Request throttling and rate limiting
• Response caching and validation
• Error handling and recovery mechanisms
"""

import asyncio
import aiohttp
import time
from typing import Dict, List, Optional, Union, Any
from dataclasses import dataclass
from urllib.parse import urljoin, urlparse
import logging
from ..proxy.pool import ProxyPool

logger = logging.getLogger(__name__)

@dataclass
class FetchRequest:
    """Represents a fetch request with all necessary parameters"""
    url: str
    method: str = "GET"
    headers: Optional[Dict[str, str]] = None
    data: Optional[Union[str, bytes, Dict[str, Any]]] = None
    params: Optional[Dict[str, Any]] = None
    timeout: float = 30.0
    allow_redirects: bool = True
    max_retries: int = 3
    proxy: Optional[str] = None
    verify_ssl: bool = True

@dataclass  
class FetchResponse:
    """Represents a fetch response with metadata"""
    url: str
    status_code: int
    headers: Dict[str, str]
    content: bytes
    text: str
    encoding: str
    history: List[str]
    elapsed_time: float
    from_cache: bool = False
    
    @property
    def is_success(self) -> bool:
        """Check if the response indicates success"""
        return 200 <= self.status_code < 300
    
    @property 
    def is_redirect(self) -> bool:
        """Check if the response is a redirect"""
        return 300 <= self.status_code < 400
    
    @property
    def is_client_error(self) -> bool:
        """Check if the response is a client error"""
        return 400 <= self.status_code < 500
        
    @property
    def is_server_error(self) -> bool:
        """Check if the response is a server error"""
        return 500 <= self.status_code < 600

class Fetcher:
    """
    Advanced HTTP/HTTPS fetcher with enterprise-grade capabilities
    
    Features:
    • Asynchronous HTTP client with connection pooling
    • Intelligent retry logic with exponential backoff
    • Proxy support with automatic rotation
    • Request rate limiting and throttling
    • Response caching for performance optimization
    • Comprehensive error handling and logging
    • Session persistence and cookie management
    • Custom header injection and user agent rotation
    """
    
    def __init__(
        self,
        max_concurrent: int = 10,
        max_retries: int = 3,
        timeout: float = 30.0,
        enable_caching: bool = True,
        proxy_pool: Optional[ProxyPool] = None,
        user_agents: Optional[List[str]] = None,
        rate_limit: float = 0.0
    ):
        """
        Initialize the Fetcher
        
        Args:
            max_concurrent: Maximum number of concurrent requests
            max_retries: Maximum number of retry attempts
            timeout: Default request timeout in seconds
            enable_caching: Whether to enable response caching
            proxy_pool: Optional proxy pool for request routing
            user_agents: List of user agents for rotation
            rate_limit: Minimum delay between requests in seconds
        """
        self.max_concurrent = max_concurrent
        self.max_retries = max_retries
        self.timeout = timeout
        self.enable_caching = enable_caching
        self.proxy_pool = proxy_pool
        self.rate_limit = rate_limit
        
        # User agents for rotation
        self.user_agents = user_agents or [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        ]
        
        # Internal state
        self._session: Optional[aiohttp.ClientSession] = None
        self._semaphore: Optional[asyncio.Semaphore] = None
        self._cache: Dict[str, FetchResponse] = {}
        self._last_request_time = 0.0
        self._user_agent_index = 0
        
        logger.info(f"Fetcher initialized with {max_concurrent} max concurrent requests")
    
    async def __aenter__(self):
        """Async context manager entry"""
        await self.start()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.close()
    
    async def start(self):
        """Initialize the fetcher session and resources"""
        if self._session is None:
            # Create connector with connection limits
            connector = aiohttp.TCPConnector(
                limit=self.max_concurrent * 2,
                limit_per_host=self.max_concurrent,
                enable_cleanup_closed=True,
                ttl_dns_cache=300,
                use_dns_cache=True,
            )
            
            # Create session with default settings
            timeout_config = aiohttp.ClientTimeout(total=self.timeout)
            self._session = aiohttp.ClientSession(
                connector=connector,
                timeout=timeout_config,
                headers={"User-Agent": self._get_next_user_agent()}
            )
            
            # Initialize concurrency limiter
            self._semaphore = asyncio.Semaphore(self.max_concurrent)
            
            logger.info("Fetcher session started successfully")
    
    async def close(self):
        """Clean up fetcher resources"""
        if self._session:
            await self._session.close()
            self._session = None
            
        self._semaphore = None
        self._cache.clear()
        logger.info("Fetcher session closed")
    
    def _get_next_user_agent(self) -> str:
        """Get the next user agent in rotation"""
        user_agent = self.user_agents[self._user_agent_index]
        self._user_agent_index = (self._user_agent_index + 1) % len(self.user_agents)
        return user_agent
    
    async def _enforce_rate_limit(self):
        """Enforce rate limiting between requests"""
        if self.rate_limit > 0:
            current_time = time.time()
            time_since_last = current_time - self._last_request_time
            if time_since_last < self.rate_limit:
                await asyncio.sleep(self.rate_limit - time_since_last)
            self._last_request_time = time.time()
    
    async def fetch(self, request: FetchRequest) -> FetchResponse:
        """
        Fetch a single URL with comprehensive error handling and retries
        
        Args:
            request: FetchRequest object with request parameters
            
        Returns:
            FetchResponse object with response data
            
        Raises:
            Exception: If all retry attempts fail
        """
        if not self._session:
            await self.start()
        
        # Check cache first if enabled
        cache_key = f"{request.method}:{request.url}"
        if self.enable_caching and cache_key in self._cache:
            cached_response = self._cache[cache_key]
            logger.debug(f"Cache hit for {request.url}")
            return cached_response
        
        # Acquire semaphore for concurrency control
        async with self._semaphore:
            return await self._fetch_with_retries(request)
    
    async def _fetch_with_retries(self, request: FetchRequest) -> FetchResponse:
        """Execute fetch with retry logic"""
        last_exception = None
        
        for attempt in range(request.max_retries + 1):
            try:
                # Enforce rate limiting
                await self._enforce_rate_limit()
                
                # Get proxy if available
                proxy_url = request.proxy
                if not proxy_url and self.proxy_pool:
                    proxy = await self.proxy_pool.get_proxy()
                    proxy_url = f"http://{proxy.host}:{proxy.port}" if proxy else None
                
                # Prepare request parameters
                kwargs = {
                    "method": request.method,
                    "url": request.url,
                    "headers": request.headers or {},
                    "timeout": aiohttp.ClientTimeout(total=request.timeout),
                    "allow_redirects": request.allow_redirects,
                    "ssl": request.verify_ssl,
                    "proxy": proxy_url
                }
                
                # Add data/params based on method
                if request.data:
                    if request.method.upper() in ["POST", "PUT", "PATCH"]:
                        if isinstance(request.data, dict):
                            kwargs["json"] = request.data
                        else:
                            kwargs["data"] = request.data
                
                if request.params:
                    kwargs["params"] = request.params
                
                # Add rotating user agent
                kwargs["headers"]["User-Agent"] = self._get_next_user_agent()
                
                # Execute request
                start_time = time.time()
                async with self._session.request(**kwargs) as response:
                    # Read response content
                    content = await response.read()
                    text = await response.text(errors='ignore')
                    elapsed = time.time() - start_time
                    
                    # Build response object
                    fetch_response = FetchResponse(
                        url=str(response.url),
                        status_code=response.status,
                        headers=dict(response.headers),
                        content=content,
                        text=text,
                        encoding=response.charset or 'utf-8',
                        history=[str(h.url) for h in response.history],
                        elapsed_time=elapsed
                    )
                    
                    # Cache successful responses
                    if self.enable_caching and fetch_response.is_success:
                        cache_key = f"{request.method}:{request.url}"
                        self._cache[cache_key] = fetch_response
                    
                    logger.debug(f"Fetch successful: {request.url} ({response.status}) in {elapsed:.2f}s")
                    return fetch_response
                    
            except Exception as e:
                last_exception = e
                if attempt < request.max_retries:
                    # Exponential backoff
                    delay = (2 ** attempt) + (asyncio.get_event_loop().time() % 1)
                    logger.warning(f"Fetch attempt {attempt + 1} failed for {request.url}: {str(e)}. Retrying in {delay:.2f}s")
                    await asyncio.sleep(delay)
                else:
                    logger.error(f"All fetch attempts failed for {request.url}: {str(e)}")
        
        # All retries failed
        raise last_exception or Exception(f"Failed to fetch {request.url} after {request.max_retries} retries")
    
    async def fetch_multiple(self, requests: List[FetchRequest]) -> List[FetchResponse]:
        """
        Fetch multiple URLs concurrently
        
        Args:
            requests: List of FetchRequest objects
            
        Returns:
            List of FetchResponse objects in the same order as requests
        """
        if not self._session:
            await self.start()
        
        # Create fetch tasks
        tasks = [self.fetch(request) for request in requests]
        
        # Execute all tasks concurrently
        logger.info(f"Starting concurrent fetch of {len(requests)} URLs")
        start_time = time.time()
        
        try:
            responses = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Process results and handle exceptions
            results = []
            for i, response in enumerate(responses):
                if isinstance(response, Exception):
                    logger.error(f"Failed to fetch {requests[i].url}: {str(response)}")
                    # Create error response
                    error_response = FetchResponse(
                        url=requests[i].url,
                        status_code=0,
                        headers={},
                        content=b'',
                        text='',
                        encoding='utf-8',
                        history=[],
                        elapsed_time=0.0
                    )
                    results.append(error_response)
                else:
                    results.append(response)
            
            elapsed = time.time() - start_time
            success_count = sum(1 for r in results if r.is_success)
            logger.info(f"Completed {len(requests)} fetches in {elapsed:.2f}s ({success_count} successful)")
            
            return results
            
        except Exception as e:
            logger.error(f"Error in concurrent fetch: {str(e)}")
            raise
    
    def clear_cache(self):
        """Clear the response cache"""
        self._cache.clear()
        logger.info("Fetcher cache cleared")
    
    def get_cache_stats(self) -> Dict[str, int]:
        """Get cache statistics"""
        return {
            "cache_size": len(self._cache),
            "max_concurrent": self.max_concurrent,
            "rate_limit": self.rate_limit
        }

# Convenience functions for quick fetching
async def fetch_url(
    url: str, 
    method: str = "GET",
    headers: Optional[Dict[str, str]] = None,
    **kwargs
) -> FetchResponse:
    """
    Quick utility function to fetch a single URL
    
    Args:
        url: URL to fetch
        method: HTTP method
        headers: Request headers
        **kwargs: Additional parameters for FetchRequest
        
    Returns:
        FetchResponse object
    """
    async with Fetcher() as fetcher:
        request = FetchRequest(url=url, method=method, headers=headers, **kwargs)
        return await fetcher.fetch(request)

async def fetch_urls(urls: List[str], **kwargs) -> List[FetchResponse]:
    """
    Quick utility function to fetch multiple URLs
    
    Args:
        urls: List of URLs to fetch
        **kwargs: Additional parameters for FetchRequest
        
    Returns:
        List of FetchResponse objects
    """
    async with Fetcher() as fetcher:
        requests = [FetchRequest(url=url, **kwargs) for url in urls]
        return await fetcher.fetch_multiple(requests)

# Export main components
__all__ = [
    "Fetcher",
    "FetchRequest", 
    "FetchResponse",
    "fetch_url",
    "fetch_urls"
]
