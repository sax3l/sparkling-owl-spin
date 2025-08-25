#!/usr/bin/env python3
"""
Requests IP Rotator Integration - Revolutionary Ultimate System v4.0
Intelligent IP rotation and request management system
"""

import asyncio
import logging
import time
import json
import random
import hashlib
from typing import Dict, Any, Optional, List, Union, Set, Callable
from dataclasses import dataclass, asdict
from collections import defaultdict, deque
from urllib.parse import urlparse, urljoin
import threading
from concurrent.futures import ThreadPoolExecutor

try:
    import requests
    from requests.adapters import HTTPAdapter
    from urllib3.util.retry import Retry
    from urllib3 import disable_warnings
    from urllib3.exceptions import InsecureRequestWarning
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False

try:
    import aiohttp
    import aiofiles
    AIOHTTP_AVAILABLE = True
except ImportError:
    AIOHTTP_AVAILABLE = False

# Disable SSL warnings for development
if REQUESTS_AVAILABLE:
    disable_warnings(InsecureRequestWarning)

logger = logging.getLogger(__name__)

@dataclass
class IPEndpoint:
    """IP endpoint information"""
    ip: str
    port: Optional[int] = None
    protocol: str = 'HTTP'  # HTTP, HTTPS, SOCKS
    region: Optional[str] = None
    country: Optional[str] = None
    provider: Optional[str] = None
    response_time: float = 0.0
    success_count: int = 0
    failure_count: int = 0
    last_used: float = 0.0
    last_tested: float = 0.0
    is_active: bool = False
    concurrent_requests: int = 0
    max_concurrent: int = 50
    bandwidth_usage: float = 0.0
    created_at: float = 0.0
    source: str = 'manual'

    def __post_init__(self):
        if self.created_at == 0.0:
            self.created_at = time.time()
            
    @property
    def endpoint_url(self) -> str:
        """Get endpoint URL"""
        if self.port:
            return f"{self.protocol.lower()}://{self.ip}:{self.port}"
        else:
            return f"{self.protocol.lower()}://{self.ip}"
            
    @property
    def success_rate(self) -> float:
        """Calculate success rate"""
        total = self.success_count + self.failure_count
        return self.success_count / total if total > 0 else 0.0
        
    @property
    def load_factor(self) -> float:
        """Calculate current load factor"""
        return self.concurrent_requests / self.max_concurrent
        
    def can_handle_request(self) -> bool:
        """Check if endpoint can handle another request"""
        return (self.is_active and 
                self.concurrent_requests < self.max_concurrent and
                time.time() - self.last_used > 0.1)  # 100ms cooldown

@dataclass
class RotatorConfig:
    """Configuration for IP rotator"""
    enabled: bool = True
    rotation_strategy: str = 'round_robin'  # round_robin, random, weighted, least_used
    max_endpoints: int = 100
    request_timeout: int = 30
    retry_attempts: int = 3
    retry_backoff: float = 1.0
    health_check_interval: int = 300  # 5 minutes
    health_check_url: str = "http://httpbin.org/ip"
    concurrent_health_checks: int = 10
    session_persistence: bool = True
    user_agent_rotation: bool = True
    header_randomization: bool = True
    rate_limiting: bool = True
    requests_per_minute: int = 60
    adaptive_rotation: bool = True
    geographic_distribution: bool = True
    load_balancing: bool = True
    failover_enabled: bool = True
    debug: bool = False

class UserAgentRotator:
    """Manages user agent rotation"""
    
    def __init__(self):
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:121.0) Gecko/20100101 Firefox/121.0',
            'Mozilla/5.0 (X11; Linux x86_64; rv:121.0) Gecko/20100101 Firefox/121.0',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/120.0.0.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15',
        ]
        self.current_index = 0
        
    def get_random_user_agent(self) -> str:
        """Get random user agent"""
        return random.choice(self.user_agents)
        
    def get_rotating_user_agent(self) -> str:
        """Get user agent using round-robin"""
        ua = self.user_agents[self.current_index]
        self.current_index = (self.current_index + 1) % len(self.user_agents)
        return ua

class RequestHeaders:
    """Manages request header randomization"""
    
    def __init__(self):
        self.accept_headers = [
            'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'application/json, text/plain, */*',
            'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8'
        ]
        
        self.accept_language = [
            'en-US,en;q=0.9',
            'en-US,en;q=0.8',
            'en-GB,en-US;q=0.9,en;q=0.8',
            'en-US,en;q=0.5'
        ]
        
        self.accept_encoding = [
            'gzip, deflate, br',
            'gzip, deflate',
            'gzip'
        ]
        
    def get_random_headers(self, user_agent: str) -> Dict[str, str]:
        """Generate random headers"""
        return {
            'User-Agent': user_agent,
            'Accept': random.choice(self.accept_headers),
            'Accept-Language': random.choice(self.accept_language),
            'Accept-Encoding': random.choice(self.accept_encoding),
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Cache-Control': 'max-age=0'
        }

class RateLimiter:
    """Rate limiting functionality"""
    
    def __init__(self, requests_per_minute: int = 60):
        self.requests_per_minute = requests_per_minute
        self.requests = deque()
        self.lock = threading.Lock()
        
    def can_make_request(self) -> bool:
        """Check if we can make a request"""
        with self.lock:
            now = time.time()
            minute_ago = now - 60
            
            # Remove old requests
            while self.requests and self.requests[0] < minute_ago:
                self.requests.popleft()
                
            return len(self.requests) < self.requests_per_minute
            
    def record_request(self):
        """Record a request"""
        with self.lock:
            self.requests.append(time.time())

class IPRotatorManager:
    """
    Advanced IP rotation manager with intelligent request distribution.
    
    Features:
    - Multiple rotation strategies
    - Load balancing and failover
    - Health monitoring and endpoint validation
    - Rate limiting and adaptive throttling
    - Geographic distribution awareness
    - Session persistence and sticky routing
    """
    
    def __init__(self, config: RotatorConfig):
        self.config = config
        self.endpoints: Dict[str, IPEndpoint] = {}  # key: ip:port or ip
        self.active_endpoints: List[str] = []
        self.user_agent_rotator = UserAgentRotator()
        self.header_generator = RequestHeaders()
        self.rate_limiter = RateLimiter(config.requests_per_minute)
        self.health_check_task = None
        self.current_index = 0
        self.session_cache = {}  # For session persistence
        
        self._stats = {
            'total_requests': 0,
            'successful_requests': 0,
            'failed_requests': 0,
            'endpoint_rotations': 0,
            'health_checks': 0,
            'rate_limited_requests': 0,
            'last_health_check': None
        }
        
        if not REQUESTS_AVAILABLE:
            raise ImportError("requests not available. Install with: pip install requests")
        
    async def initialize(self):
        """Initialize IP rotator manager"""
        
        if not self.config.enabled:
            return
            
        logger.info("🚀 Initializing IP rotator manager...")
        
        # Start health check task
        if self.config.health_check_interval > 0:
            self.health_check_task = asyncio.create_task(self._health_check_loop())
            
        logger.info("✅ IP rotator manager initialized")
        
    async def add_endpoint(self, ip: str, port: Optional[int] = None, **kwargs) -> bool:
        """Add IP endpoint to rotation"""
        
        endpoint_key = f"{ip}:{port}" if port else ip
        
        if endpoint_key in self.endpoints:
            # Update existing endpoint
            existing = self.endpoints[endpoint_key]
            for key, value in kwargs.items():
                if hasattr(existing, key):
                    setattr(existing, key, value)
        else:
            # Create new endpoint
            endpoint = IPEndpoint(ip=ip, port=port, **kwargs)
            self.endpoints[endpoint_key] = endpoint
            
            # Test new endpoint
            if await self._test_endpoint(endpoint):
                self.active_endpoints.append(endpoint_key)
                logger.info(f"✅ Added active endpoint: {endpoint_key}")
            else:
                logger.warning(f"⚠️ Added inactive endpoint: {endpoint_key}")
                
        return True
        
    async def add_endpoint_list(self, endpoint_list: List[Dict[str, Any]]) -> int:
        """Add multiple endpoints"""
        
        added_count = 0
        
        for endpoint_data in endpoint_list:
            if 'ip' in endpoint_data:
                try:
                    success = await self.add_endpoint(**endpoint_data)
                    if success:
                        added_count += 1
                except Exception as e:
                    logger.error(f"❌ Failed to add endpoint {endpoint_data.get('ip')}: {str(e)}")
                    
        logger.info(f"✅ Added {added_count}/{len(endpoint_list)} endpoints")
        return added_count
        
    async def make_request(self, method: str, url: str, 
                          session_id: Optional[str] = None,
                          **kwargs) -> Dict[str, Any]:
        """
        Make HTTP request with IP rotation.
        
        Returns:
        {
            'success': bool,
            'status_code': int,
            'content': str,
            'headers': dict,
            'endpoint': str,
            'response_time': float,
            'attempts': int
        }
        """
        
        if not self.config.enabled:
            return await self._make_direct_request(method, url, **kwargs)
            
        if not self.active_endpoints:
            await self._refresh_active_endpoints()
            
        if not self.active_endpoints:
            return {
                'success': False,
                'error': 'No active endpoints available',
                'method': 'ip-rotator'
            }
            
        # Rate limiting
        if self.config.rate_limiting:
            while not self.rate_limiter.can_make_request():
                await asyncio.sleep(0.1)
                self._stats['rate_limited_requests'] += 1
                
            self.rate_limiter.record_request()
            
        # Select endpoint
        endpoint = await self._select_endpoint(session_id)
        
        if not endpoint:
            return {
                'success': False,
                'error': 'Failed to select endpoint',
                'method': 'ip-rotator'
            }
            
        # Make request with retries
        for attempt in range(self.config.retry_attempts):
            try:
                result = await self._make_request_with_endpoint(
                    method, url, endpoint, attempt, **kwargs
                )
                
                if result['success']:
                    self._stats['successful_requests'] += 1
                    endpoint.success_count += 1
                    return result
                else:
                    endpoint.failure_count += 1
                    
                    if attempt < self.config.retry_attempts - 1:
                        # Try different endpoint for retry
                        endpoint = await self._select_endpoint(session_id, exclude=[endpoint])
                        if not endpoint:
                            break
                            
                        await asyncio.sleep(self.config.retry_backoff * (attempt + 1))
                        
            except Exception as e:
                endpoint.failure_count += 1
                logger.error(f"❌ Request failed on attempt {attempt + 1}: {str(e)}")
                
                if attempt < self.config.retry_attempts - 1:
                    await asyncio.sleep(self.config.retry_backoff * (attempt + 1))
                    
        self._stats['failed_requests'] += 1
        
        return {
            'success': False,
            'error': 'All retry attempts failed',
            'attempts': self.config.retry_attempts,
            'method': 'ip-rotator'
        }
        
    async def _make_request_with_endpoint(self, method: str, url: str, 
                                        endpoint: IPEndpoint, attempt: int,
                                        **kwargs) -> Dict[str, Any]:
        """Make request using specific endpoint"""
        
        start_time = time.time()
        endpoint.concurrent_requests += 1
        endpoint.last_used = start_time
        
        try:
            # Prepare session
            session = self._get_session()
            
            # Prepare headers
            headers = kwargs.get('headers', {})
            
            if self.config.user_agent_rotation:
                headers['User-Agent'] = self.user_agent_rotator.get_rotating_user_agent()
                
            if self.config.header_randomization:
                random_headers = self.header_generator.get_random_headers(
                    headers.get('User-Agent', '')
                )
                # Merge with existing headers, giving priority to user headers
                merged_headers = {**random_headers, **headers}
                headers = merged_headers
                
            kwargs['headers'] = headers
            
            # Configure proxy if endpoint requires it
            if endpoint.protocol in ['SOCKS', 'SOCKS4', 'SOCKS5']:
                kwargs['proxies'] = {
                    'http': endpoint.endpoint_url,
                    'https': endpoint.endpoint_url
                }
            elif endpoint.port and endpoint.protocol in ['HTTP', 'HTTPS']:
                kwargs['proxies'] = {
                    'http': endpoint.endpoint_url,
                    'https': endpoint.endpoint_url
                }
                
            # Set timeout
            kwargs.setdefault('timeout', self.config.request_timeout)
            kwargs.setdefault('verify', False)  # Disable SSL verification for development
            
            # Make request
            response = session.request(method.upper(), url, **kwargs)
            response_time = time.time() - start_time
            
            endpoint.response_time = response_time
            self._stats['total_requests'] += 1
            
            return {
                'success': True,
                'status_code': response.status_code,
                'content': response.text,
                'headers': dict(response.headers),
                'endpoint': f"{endpoint.ip}:{endpoint.port}" if endpoint.port else endpoint.ip,
                'response_time': response_time,
                'attempt': attempt + 1,
                'method': 'ip-rotator'
            }
            
        except Exception as e:
            response_time = time.time() - start_time
            
            return {
                'success': False,
                'error': str(e),
                'endpoint': f"{endpoint.ip}:{endpoint.port}" if endpoint.port else endpoint.ip,
                'response_time': response_time,
                'attempt': attempt + 1,
                'method': 'ip-rotator'
            }
            
        finally:
            endpoint.concurrent_requests = max(0, endpoint.concurrent_requests - 1)
            
    async def _make_direct_request(self, method: str, url: str, **kwargs) -> Dict[str, Any]:
        """Make direct request without rotation"""
        
        start_time = time.time()
        
        try:
            session = self._get_session()
            
            # Add user agent if not present
            headers = kwargs.get('headers', {})
            if 'User-Agent' not in headers:
                headers['User-Agent'] = self.user_agent_rotator.get_random_user_agent()
                kwargs['headers'] = headers
                
            kwargs.setdefault('timeout', self.config.request_timeout)
            
            response = session.request(method.upper(), url, **kwargs)
            response_time = time.time() - start_time
            
            return {
                'success': True,
                'status_code': response.status_code,
                'content': response.text,
                'headers': dict(response.headers),
                'response_time': response_time,
                'method': 'direct'
            }
            
        except Exception as e:
            response_time = time.time() - start_time
            
            return {
                'success': False,
                'error': str(e),
                'response_time': response_time,
                'method': 'direct'
            }
            
    def _get_session(self) -> requests.Session:
        """Get or create requests session"""
        
        session = requests.Session()
        
        # Configure retry strategy
        retry_strategy = Retry(
            total=0,  # We handle retries ourselves
            backoff_factor=self.config.retry_backoff,
            status_forcelist=[429, 500, 502, 503, 504]
        )
        
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        
        return session
        
    async def _select_endpoint(self, session_id: Optional[str] = None,
                             exclude: Optional[List[IPEndpoint]] = None) -> Optional[IPEndpoint]:
        """Select endpoint based on strategy"""
        
        if not self.active_endpoints:
            return None
            
        exclude_keys = []
        if exclude:
            exclude_keys = [f"{ep.ip}:{ep.port}" if ep.port else ep.ip for ep in exclude]
            
        available_endpoints = [
            self.endpoints[key] for key in self.active_endpoints
            if key not in exclude_keys and self.endpoints[key].can_handle_request()
        ]
        
        if not available_endpoints:
            return None
            
        # Session persistence
        if session_id and self.config.session_persistence:
            if session_id in self.session_cache:
                cached_endpoint = self.session_cache[session_id]
                if cached_endpoint in available_endpoints:
                    return cached_endpoint
                    
        # Select based on strategy
        if self.config.rotation_strategy == 'round_robin':
            endpoint = self._round_robin_select(available_endpoints)
        elif self.config.rotation_strategy == 'random':
            endpoint = random.choice(available_endpoints)
        elif self.config.rotation_strategy == 'weighted':
            endpoint = self._weighted_select(available_endpoints)
        elif self.config.rotation_strategy == 'least_used':
            endpoint = self._least_used_select(available_endpoints)
        else:
            endpoint = available_endpoints[0]
            
        # Cache for session persistence
        if session_id and self.config.session_persistence:
            self.session_cache[session_id] = endpoint
            
        self._stats['endpoint_rotations'] += 1
        
        return endpoint
        
    def _round_robin_select(self, endpoints: List[IPEndpoint]) -> IPEndpoint:
        """Round-robin selection"""
        endpoint = endpoints[self.current_index % len(endpoints)]
        self.current_index += 1
        return endpoint
        
    def _weighted_select(self, endpoints: List[IPEndpoint]) -> IPEndpoint:
        """Weighted selection based on success rate and response time"""
        
        def calculate_weight(endpoint):
            success_rate = endpoint.success_rate or 0.1
            response_time_factor = min(1.0, 5.0 / max(endpoint.response_time, 0.1))
            load_factor = 1.0 - endpoint.load_factor
            return success_rate * response_time_factor * load_factor
            
        weights = [calculate_weight(ep) for ep in endpoints]
        total_weight = sum(weights)
        
        if total_weight == 0:
            return random.choice(endpoints)
            
        r = random.uniform(0, total_weight)
        cumulative = 0
        
        for i, weight in enumerate(weights):
            cumulative += weight
            if r <= cumulative:
                return endpoints[i]
                
        return endpoints[-1]
        
    def _least_used_select(self, endpoints: List[IPEndpoint]) -> IPEndpoint:
        """Select endpoint with lowest usage"""
        return min(endpoints, key=lambda ep: ep.success_count + ep.failure_count)
        
    async def _refresh_active_endpoints(self):
        """Refresh list of active endpoints"""
        
        active = []
        
        for key, endpoint in self.endpoints.items():
            if endpoint.is_active and endpoint.failure_count < 10:
                active.append(key)
                
        self.active_endpoints = active
        logger.debug(f"🔄 Refreshed active endpoints: {len(active)}")
        
    async def _test_endpoint(self, endpoint: IPEndpoint) -> bool:
        """Test single endpoint"""
        
        try:
            session = self._get_session()
            
            # Configure proxy if needed
            proxies = None
            if endpoint.protocol in ['SOCKS', 'SOCKS4', 'SOCKS5']:
                proxies = {
                    'http': endpoint.endpoint_url,
                    'https': endpoint.endpoint_url
                }
            elif endpoint.port and endpoint.protocol in ['HTTP', 'HTTPS']:
                proxies = {
                    'http': endpoint.endpoint_url,
                    'https': endpoint.endpoint_url
                }
                
            start_time = time.time()
            
            response = session.get(
                self.config.health_check_url,
                proxies=proxies,
                timeout=self.config.request_timeout,
                verify=False
            )
            
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                endpoint.response_time = response_time
                endpoint.success_count += 1
                endpoint.is_active = True
                endpoint.last_tested = time.time()
                return True
            else:
                endpoint.failure_count += 1
                endpoint.is_active = False
                return False
                
        except Exception as e:
            endpoint.failure_count += 1
            endpoint.is_active = False
            endpoint.last_tested = time.time()
            logger.debug(f"❌ Endpoint test failed: {str(e)}")
            return False
            
    async def health_check_all_endpoints(self) -> Dict[str, Any]:
        """Health check all endpoints"""
        
        if not self.endpoints:
            return {'active': 0, 'inactive': 0, 'total': 0}
            
        logger.info(f"🏥 Health checking {len(self.endpoints)} endpoints...")
        start_time = time.time()
        
        # Create tasks with semaphore for concurrency control
        semaphore = asyncio.Semaphore(self.config.concurrent_health_checks)
        
        async def test_with_semaphore(endpoint):
            async with semaphore:
                return await asyncio.get_event_loop().run_in_executor(
                    None, lambda: asyncio.run(self._test_endpoint(endpoint))
                )
                
        tasks = [test_with_semaphore(endpoint) for endpoint in self.endpoints.values()]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process results
        active_count = sum(1 for result in results if result is True)
        inactive_count = len(results) - active_count
        
        # Update active endpoints list
        await self._refresh_active_endpoints()
        
        health_check_time = time.time() - start_time
        self._stats['health_checks'] += 1
        self._stats['last_health_check'] = time.time()
        
        logger.info(f"✅ Health check complete: {active_count} active, {inactive_count} inactive ({health_check_time:.2f}s)")
        
        return {
            'active': active_count,
            'inactive': inactive_count,
            'total': len(self.endpoints),
            'health_check_time': health_check_time
        }
        
    async def _health_check_loop(self):
        """Background health check loop"""
        
        while True:
            try:
                await asyncio.sleep(self.config.health_check_interval)
                await self.health_check_all_endpoints()
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"❌ Health check loop error: {str(e)}")
                
    def get_stats(self) -> Dict[str, Any]:
        """Get rotator statistics"""
        
        # Calculate endpoint stats
        total_endpoints = len(self.endpoints)
        active_endpoints = len(self.active_endpoints)
        
        # Response time stats
        response_times = [ep.response_time for ep in self.endpoints.values() if ep.response_time > 0]
        avg_response_time = sum(response_times) / len(response_times) if response_times else 0.0
        
        # Success rate stats
        success_rates = [ep.success_rate for ep in self.endpoints.values()]
        avg_success_rate = sum(success_rates) / len(success_rates) if success_rates else 0.0
        
        # Geographic distribution
        by_country = defaultdict(int)
        by_region = defaultdict(int)
        
        for endpoint in self.endpoints.values():
            by_country[endpoint.country or 'Unknown'] += 1
            by_region[endpoint.region or 'Unknown'] += 1
            
        return {
            **self._stats,
            'total_endpoints': total_endpoints,
            'active_endpoints': active_endpoints,
            'average_response_time': avg_response_time,
            'average_success_rate': avg_success_rate,
            'by_country': dict(by_country),
            'by_region': dict(by_region),
            'config': asdict(self.config)
        }
        
    async def cleanup(self):
        """Clean up resources"""
        
        if self.health_check_task:
            self.health_check_task.cancel()
            try:
                await self.health_check_task
            except asyncio.CancelledError:
                pass

class RequestsIPRotatorAdapter:
    """High-level adapter for IP rotation with requests"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = RotatorConfig(**config)
        self.manager = IPRotatorManager(self.config) if self.config.enabled else None
        
    async def initialize(self):
        """Initialize the adapter"""
        if not self.config.enabled:
            logger.info("IP rotator adapter disabled")
            return
            
        if not REQUESTS_AVAILABLE:
            logger.error("❌ requests not available")
            if self.config.enabled:
                raise ImportError("requests package required")
            return
            
        if self.manager:
            await self.manager.initialize()
            logger.info("✅ IP rotator adapter initialized")
        else:
            logger.error("❌ IP rotator manager not available")
            
    async def make_request(self, method: str, url: str, **kwargs) -> Dict[str, Any]:
        """
        Make HTTP request with IP rotation.
        
        Returns:
        {
            'success': bool,
            'status_code': int,
            'content': str,
            'headers': dict,
            'endpoint': str,
            'response_time': float
        }
        """
        
        if not self.config.enabled or not self.manager:
            return {
                'success': False,
                'error': 'IP rotator is disabled or not available'
            }
            
        try:
            result = await self.manager.make_request(method, url, **kwargs)
            return result
            
        except Exception as e:
            logger.error(f"❌ Failed to make request: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'method': 'ip-rotator'
            }
            
    async def add_endpoints(self, endpoint_list: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Add IP endpoints for rotation"""
        
        if not self.config.enabled or not self.manager:
            return {'success': False, 'error': 'IP rotator not available'}
            
        try:
            added_count = await self.manager.add_endpoint_list(endpoint_list)
            
            return {
                'success': True,
                'added_count': added_count,
                'total_requested': len(endpoint_list),
                'method': 'ip-rotator'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'method': 'ip-rotator'
            }
            
    async def health_check(self) -> Dict[str, Any]:
        """Health check all endpoints"""
        
        if not self.config.enabled or not self.manager:
            return {'success': False, 'error': 'IP rotator not available'}
            
        try:
            result = await self.manager.health_check_all_endpoints()
            result['success'] = True
            result['method'] = 'ip-rotator'
            
            return result
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'method': 'ip-rotator'
            }
            
    async def get_stats(self) -> Dict[str, Any]:
        """Get adapter statistics"""
        base_stats = {
            'enabled': self.config.enabled,
            'config': asdict(self.config)
        }
        
        if self.manager:
            base_stats['manager_stats'] = self.manager.get_stats()
        else:
            base_stats['manager_stats'] = {}
            
        return base_stats
        
    async def cleanup(self):
        """Clean up all resources"""
        if self.manager:
            await self.manager.cleanup()

# Factory function
def create_ip_rotator_adapter(config: Dict[str, Any]) -> RequestsIPRotatorAdapter:
    """Create and configure IP rotator adapter"""
    return RequestsIPRotatorAdapter(config)

# Example usage
async def main():
    """Example usage"""
    config = {
        'enabled': True,
        'rotation_strategy': 'weighted',
        'rate_limiting': True,
        'requests_per_minute': 30,
        'debug': True
    }
    
    adapter = create_ip_rotator_adapter(config)
    
    try:
        await adapter.initialize()
        
        # Add some test endpoints (these are dummy IPs)
        test_endpoints = [
            {'ip': '127.0.0.1', 'port': 8080, 'protocol': 'HTTP'},
            {'ip': '127.0.0.1', 'port': 8081, 'protocol': 'HTTP'}
        ]
        
        result = await adapter.add_endpoints(test_endpoints)
        print(f"Added endpoints: {result}")
        
        # Make request
        request_result = await adapter.make_request('GET', 'http://httpbin.org/ip')
        
        if request_result['success']:
            print(f"✅ Request successful: {request_result['status_code']}")
            print(f"Response time: {request_result['response_time']:.2f}s")
            print(f"Endpoint: {request_result.get('endpoint', 'direct')}")
        else:
            print(f"❌ Request failed: {request_result['error']}")
            
    finally:
        await adapter.cleanup()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
