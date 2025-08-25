#!/usr/bin/env python3
"""
Proxy Pool Integration - Revolutionary Ultimate System v4.0
Advanced proxy pool management and rotation system
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
from urllib.parse import urlparse, parse_qs
import threading
from concurrent.futures import ThreadPoolExecutor

try:
    import requests
    from requests.adapters import HTTPAdapter
    from urllib3.util.retry import Retry
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False

try:
    import aiohttp
    import aiofiles
    AIOHTTP_AVAILABLE = True
except ImportError:
    AIOHTTP_AVAILABLE = False

logger = logging.getLogger(__name__)

@dataclass 
class ProxyEntry:
    """Individual proxy entry with metadata"""
    host: str
    port: int
    protocol: str = 'HTTP'  # HTTP, HTTPS, SOCKS4, SOCKS5
    username: Optional[str] = None
    password: Optional[str] = None
    country: Optional[str] = None
    city: Optional[str] = None
    provider: Optional[str] = None
    anonymity: str = 'Unknown'  # Elite, Anonymous, Transparent
    response_time: float = 0.0
    success_count: int = 0
    failure_count: int = 0
    last_used: float = 0.0
    last_tested: float = 0.0
    is_working: bool = False
    concurrent_users: int = 0
    max_concurrent: int = 10
    created_at: float = 0.0
    source: str = 'manual'

    def __post_init__(self):
        if self.created_at == 0.0:
            self.created_at = time.time()
            
    @property
    def proxy_url(self) -> str:
        """Get proxy URL"""
        auth = f"{self.username}:{self.password}@" if self.username and self.password else ""
        
        if self.protocol.upper() in ['SOCKS4', 'SOCKS5']:
            return f"socks{self.protocol[-1]}://{auth}{self.host}:{self.port}"
        else:
            return f"http://{auth}{self.host}:{self.port}"
            
    @property
    def success_rate(self) -> float:
        """Calculate success rate"""
        total = self.success_count + self.failure_count
        return self.success_count / total if total > 0 else 0.0
        
    @property
    def reliability_score(self) -> float:
        """Calculate overall reliability score"""
        success_rate = self.success_rate
        response_score = min(1.0, 10.0 / max(self.response_time, 0.1))
        age_score = min(1.0, (time.time() - self.created_at) / 3600)  # Hours active
        
        return (success_rate * 0.5 + response_score * 0.3 + age_score * 0.2)
        
    def can_handle_request(self) -> bool:
        """Check if proxy can handle another request"""
        return (self.is_working and 
                self.concurrent_users < self.max_concurrent and
                time.time() - self.last_used > 1.0)  # 1 second cooldown

@dataclass
class ProxyPoolConfig:
    """Configuration for proxy pool manager"""
    enabled: bool = True
    min_proxies: int = 10
    max_proxies: int = 1000
    test_timeout: int = 10
    test_interval: int = 300  # Test proxies every 5 minutes
    rotation_strategy: str = 'round_robin'  # round_robin, random, best_first
    max_failures: int = 5
    failure_backoff: float = 60.0  # Seconds to wait after failure
    concurrent_tests: int = 20
    proxy_sources: List[str] = None  # URLs to fetch proxies from
    test_urls: List[str] = None
    geo_distribution: bool = True
    load_balancing: bool = True
    persistent_storage: bool = True
    storage_file: str = "proxy_pool.json"
    refresh_interval: int = 3600  # Refresh from sources every hour
    debug: bool = False

class ProxyRotator:
    """Handles different proxy rotation strategies"""
    
    def __init__(self, strategy: str = 'round_robin'):
        self.strategy = strategy
        self.last_used = {}
        self.usage_counts = defaultdict(int)
        
    def select_proxy(self, proxies: List[ProxyEntry], 
                    session_id: Optional[str] = None) -> Optional[ProxyEntry]:
        """Select proxy based on strategy"""
        
        if not proxies:
            return None
            
        available_proxies = [p for p in proxies if p.can_handle_request()]
        
        if not available_proxies:
            return None
            
        if self.strategy == 'round_robin':
            return self._round_robin_select(available_proxies, session_id)
        elif self.strategy == 'random':
            return random.choice(available_proxies)
        elif self.strategy == 'best_first':
            return self._best_first_select(available_proxies)
        elif self.strategy == 'least_used':
            return self._least_used_select(available_proxies)
        else:
            return available_proxies[0]
            
    def _round_robin_select(self, proxies: List[ProxyEntry], 
                          session_id: Optional[str]) -> ProxyEntry:
        """Round-robin selection"""
        key = session_id or 'default'
        
        if key not in self.last_used:
            self.last_used[key] = -1
            
        self.last_used[key] = (self.last_used[key] + 1) % len(proxies)
        return proxies[self.last_used[key]]
        
    def _best_first_select(self, proxies: List[ProxyEntry]) -> ProxyEntry:
        """Select proxy with best reliability score"""
        return max(proxies, key=lambda p: p.reliability_score)
        
    def _least_used_select(self, proxies: List[ProxyEntry]) -> ProxyEntry:
        """Select least used proxy"""
        return min(proxies, key=lambda p: self.usage_counts[f"{p.host}:{p.port}"])

class ProxyValidator:
    """Validates proxy functionality"""
    
    def __init__(self, config: ProxyPoolConfig):
        self.config = config
        self.test_urls = config.test_urls or [
            'http://httpbin.org/ip',
            'https://httpbin.org/ip',
            'http://httpbin.org/headers',
            'https://httpbin.org/headers'
        ]
        
    async def validate_proxy(self, proxy: ProxyEntry) -> Dict[str, Any]:
        """Validate single proxy"""
        
        start_time = time.time()
        results = {'proxy': f"{proxy.host}:{proxy.port}"}
        
        try:
            # Test with different URLs
            test_results = []
            
            for test_url in self.test_urls:
                result = await self._test_single_url(proxy, test_url)
                test_results.append(result)
                
            # Analyze results
            successful_tests = [r for r in test_results if r.get('success')]
            
            if successful_tests:
                proxy.response_time = sum(r['response_time'] for r in successful_tests) / len(successful_tests)
                proxy.success_count += len(successful_tests)
                proxy.failure_count += len(test_results) - len(successful_tests)
                proxy.is_working = len(successful_tests) >= len(test_results) * 0.5  # At least 50% success
                proxy.last_tested = time.time()
                
                results.update({
                    'success': True,
                    'working': proxy.is_working,
                    'response_time': proxy.response_time,
                    'success_rate': proxy.success_rate,
                    'tests_passed': len(successful_tests),
                    'tests_total': len(test_results)
                })
                
                # Extract additional info from successful responses
                if successful_tests:
                    self._extract_proxy_info(proxy, successful_tests[0])
                    
            else:
                proxy.failure_count += len(test_results)
                proxy.is_working = False
                proxy.last_tested = time.time()
                
                results.update({
                    'success': False,
                    'working': False,
                    'error': 'All tests failed',
                    'tests_passed': 0,
                    'tests_total': len(test_results)
                })
                
        except Exception as e:
            proxy.failure_count += 1
            proxy.is_working = False
            proxy.last_tested = time.time()
            
            results.update({
                'success': False,
                'working': False,
                'error': str(e)
            })
            
        results['validation_time'] = time.time() - start_time
        return results
        
    async def _test_single_url(self, proxy: ProxyEntry, test_url: str) -> Dict[str, Any]:
        """Test proxy with single URL"""
        
        start_time = time.time()
        
        try:
            if AIOHTTP_AVAILABLE:
                return await self._test_with_aiohttp(proxy, test_url, start_time)
            elif REQUESTS_AVAILABLE:
                return await asyncio.get_event_loop().run_in_executor(
                    None, self._test_with_requests, proxy, test_url, start_time
                )
            else:
                return {
                    'success': False,
                    'error': 'No HTTP client available',
                    'url': test_url
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'url': test_url,
                'response_time': time.time() - start_time
            }
            
    async def _test_with_aiohttp(self, proxy: ProxyEntry, test_url: str, start_time: float) -> Dict[str, Any]:
        """Test proxy using aiohttp"""
        
        try:
            timeout = aiohttp.ClientTimeout(total=self.config.test_timeout)
            proxy_url = proxy.proxy_url
            
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.get(test_url, proxy=proxy_url) as response:
                    content = await response.text()
                    response_time = time.time() - start_time
                    
                    return {
                        'success': response.status == 200,
                        'status_code': response.status,
                        'response_time': response_time,
                        'content': content[:1000],  # Limit content size
                        'url': test_url
                    }
                    
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'url': test_url,
                'response_time': time.time() - start_time
            }
            
    def _test_with_requests(self, proxy: ProxyEntry, test_url: str, start_time: float) -> Dict[str, Any]:
        """Test proxy using requests (synchronous)"""
        
        try:
            proxies = {
                'http': proxy.proxy_url,
                'https': proxy.proxy_url
            }
            
            response = requests.get(
                test_url,
                proxies=proxies,
                timeout=self.config.test_timeout,
                verify=False
            )
            
            response_time = time.time() - start_time
            
            return {
                'success': response.status_code == 200,
                'status_code': response.status_code,
                'response_time': response_time,
                'content': response.text[:1000],
                'url': test_url
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'url': test_url,
                'response_time': time.time() - start_time
            }
            
    def _extract_proxy_info(self, proxy: ProxyEntry, test_result: Dict[str, Any]):
        """Extract proxy information from test response"""
        
        try:
            content = test_result.get('content', '')
            
            # Try to parse as JSON (from httpbin.org)
            if 'httpbin.org' in test_result.get('url', ''):
                try:
                    data = json.loads(content)
                    
                    # Extract origin IP
                    if 'origin' in data:
                        origin_ip = data['origin'].split(',')[0].strip()
                        # Check if proxy is working (different IP)
                        if origin_ip != proxy.host:
                            proxy.is_working = True
                            
                    # Extract headers info for anonymity detection
                    if 'headers' in data:
                        headers = data['headers']
                        
                        # Check anonymity level
                        if any(header in headers for header in ['X-Forwarded-For', 'X-Real-Ip']):
                            proxy.anonymity = 'Transparent'
                        elif 'Via' in headers:
                            proxy.anonymity = 'Anonymous'
                        else:
                            proxy.anonymity = 'Elite'
                            
                except json.JSONDecodeError:
                    pass
                    
        except Exception as e:
            logger.debug(f"Failed to extract proxy info: {str(e)}")

class ProxyPoolManager:
    """
    Advanced proxy pool manager with rotation, validation, and load balancing.
    
    Features:
    - Multiple rotation strategies
    - Automatic proxy validation and testing
    - Load balancing and concurrent request handling
    - Geographic distribution awareness
    - Persistent storage and recovery
    - Dynamic proxy source integration
    """
    
    def __init__(self, config: ProxyPoolConfig):
        self.config = config
        self.proxies: Dict[str, ProxyEntry] = {}  # key: host:port
        self.working_proxies: List[str] = []
        self.rotator = ProxyRotator(config.rotation_strategy)
        self.validator = ProxyValidator(config)
        self.validation_task = None
        self.refresh_task = None
        self.executor = ThreadPoolExecutor(max_workers=config.concurrent_tests)
        
        self._stats = {
            'total_requests': 0,
            'successful_requests': 0,
            'failed_requests': 0,
            'proxy_changes': 0,
            'validation_runs': 0,
            'last_refresh': None
        }
        
    async def initialize(self):
        """Initialize proxy pool manager"""
        
        if not self.config.enabled:
            return
            
        logger.info("🚀 Initializing proxy pool manager...")
        
        # Load persisted proxies
        if self.config.persistent_storage:
            await self._load_persisted_proxies()
            
        # Start background tasks
        if self.config.test_interval > 0:
            self.validation_task = asyncio.create_task(self._validation_loop())
            
        if self.config.refresh_interval > 0 and self.config.proxy_sources:
            self.refresh_task = asyncio.create_task(self._refresh_loop())
            
        logger.info(f"✅ Proxy pool initialized with {len(self.proxies)} proxies")
        
    async def add_proxy(self, host: str, port: int, **kwargs) -> bool:
        """Add single proxy to pool"""
        
        proxy_key = f"{host}:{port}"
        
        if proxy_key in self.proxies:
            # Update existing proxy
            existing = self.proxies[proxy_key]
            for key, value in kwargs.items():
                if hasattr(existing, key):
                    setattr(existing, key, value)
        else:
            # Create new proxy
            proxy = ProxyEntry(host=host, port=port, **kwargs)
            self.proxies[proxy_key] = proxy
            
            # Validate new proxy
            result = await self.validator.validate_proxy(proxy)
            if result.get('working'):
                self.working_proxies.append(proxy_key)
                logger.info(f"✅ Added working proxy: {proxy_key}")
                
        return True
        
    async def add_proxy_list(self, proxy_list: List[Dict[str, Any]]) -> int:
        """Add multiple proxies to pool"""
        
        added_count = 0
        
        for proxy_data in proxy_list:
            if 'host' in proxy_data and 'port' in proxy_data:
                try:
                    success = await self.add_proxy(**proxy_data)
                    if success:
                        added_count += 1
                except Exception as e:
                    logger.error(f"❌ Failed to add proxy {proxy_data.get('host')}:{proxy_data.get('port')}: {str(e)}")
                    
        logger.info(f"✅ Added {added_count}/{len(proxy_list)} proxies to pool")
        return added_count
        
    async def get_proxy(self, session_id: Optional[str] = None,
                       filters: Optional[Dict[str, Any]] = None) -> Optional[ProxyEntry]:
        """Get proxy for request"""
        
        if not self.working_proxies:
            await self._refresh_working_proxies()
            
        if not self.working_proxies:
            return None
            
        # Apply filters
        available_proxies = []
        for proxy_key in self.working_proxies:
            proxy = self.proxies[proxy_key]
            
            if filters:
                if not self._matches_filters(proxy, filters):
                    continue
                    
            available_proxies.append(proxy)
            
        if not available_proxies:
            return None
            
        # Select proxy using rotation strategy
        selected_proxy = self.rotator.select_proxy(available_proxies, session_id)
        
        if selected_proxy:
            selected_proxy.concurrent_users += 1
            selected_proxy.last_used = time.time()
            self._stats['total_requests'] += 1
            
        return selected_proxy
        
    async def release_proxy(self, proxy: ProxyEntry, success: bool = True):
        """Release proxy after use"""
        
        proxy.concurrent_users = max(0, proxy.concurrent_users - 1)
        
        if success:
            proxy.success_count += 1
            self._stats['successful_requests'] += 1
        else:
            proxy.failure_count += 1
            self._stats['failed_requests'] += 1
            
            # Remove proxy if too many failures
            if proxy.failure_count >= self.config.max_failures:
                await self._remove_proxy(f"{proxy.host}:{proxy.port}")
                
    def _matches_filters(self, proxy: ProxyEntry, filters: Dict[str, Any]) -> bool:
        """Check if proxy matches filters"""
        
        for key, value in filters.items():
            if hasattr(proxy, key):
                proxy_value = getattr(proxy, key)
                
                if isinstance(value, list):
                    if proxy_value not in value:
                        return False
                elif proxy_value != value:
                    return False
                    
        return True
        
    async def _refresh_working_proxies(self):
        """Refresh list of working proxies"""
        
        working = []
        
        for proxy_key, proxy in self.proxies.items():
            if proxy.is_working and proxy.failure_count < self.config.max_failures:
                working.append(proxy_key)
                
        self.working_proxies = working
        logger.debug(f"🔄 Refreshed working proxies: {len(working)}")
        
    async def _remove_proxy(self, proxy_key: str):
        """Remove proxy from pool"""
        
        if proxy_key in self.proxies:
            del self.proxies[proxy_key]
            
        if proxy_key in self.working_proxies:
            self.working_proxies.remove(proxy_key)
            
        logger.info(f"🗑️ Removed proxy: {proxy_key}")
        
    async def validate_all_proxies(self) -> Dict[str, Any]:
        """Validate all proxies in pool"""
        
        if not self.proxies:
            return {'working': 0, 'failed': 0, 'total': 0}
            
        logger.info(f"🧪 Validating {len(self.proxies)} proxies...")
        start_time = time.time()
        
        # Create validation tasks
        tasks = []
        semaphore = asyncio.Semaphore(self.config.concurrent_tests)
        
        async def validate_with_semaphore(proxy):
            async with semaphore:
                return await self.validator.validate_proxy(proxy)
                
        for proxy in self.proxies.values():
            task = asyncio.create_task(validate_with_semaphore(proxy))
            tasks.append(task)
            
        # Wait for all validations
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process results
        working_count = 0
        failed_count = 0
        
        for i, result in enumerate(results):
            if isinstance(result, dict) and result.get('working'):
                working_count += 1
            else:
                failed_count += 1
                
        # Update working proxies list
        await self._refresh_working_proxies()
        
        validation_time = time.time() - start_time
        self._stats['validation_runs'] += 1
        
        logger.info(f"✅ Validation complete: {working_count} working, {failed_count} failed ({validation_time:.2f}s)")
        
        return {
            'working': working_count,
            'failed': failed_count,
            'total': len(self.proxies),
            'validation_time': validation_time
        }
        
    async def _validation_loop(self):
        """Background validation loop"""
        
        while True:
            try:
                await asyncio.sleep(self.config.test_interval)
                await self.validate_all_proxies()
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"❌ Validation loop error: {str(e)}")
                
    async def _refresh_loop(self):
        """Background refresh loop for proxy sources"""
        
        while True:
            try:
                await asyncio.sleep(self.config.refresh_interval)
                await self._refresh_from_sources()
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"❌ Refresh loop error: {str(e)}")
                
    async def _refresh_from_sources(self):
        """Refresh proxies from configured sources"""
        
        if not self.config.proxy_sources:
            return
            
        logger.info("🔄 Refreshing proxies from sources...")
        
        for source_url in self.config.proxy_sources:
            try:
                await self._fetch_proxies_from_source(source_url)
            except Exception as e:
                logger.error(f"❌ Failed to fetch from {source_url}: {str(e)}")
                
        self._stats['last_refresh'] = time.time()
        
    async def _fetch_proxies_from_source(self, source_url: str):
        """Fetch proxies from single source"""
        
        try:
            if AIOHTTP_AVAILABLE:
                async with aiohttp.ClientSession() as session:
                    async with session.get(source_url, timeout=aiohttp.ClientTimeout(total=30)) as response:
                        if response.status == 200:
                            content = await response.text()
                            proxies = self._parse_proxy_list(content)
                            await self.add_proxy_list(proxies)
            elif REQUESTS_AVAILABLE:
                response = requests.get(source_url, timeout=30)
                if response.status_code == 200:
                    proxies = self._parse_proxy_list(response.text)
                    await self.add_proxy_list(proxies)
                    
        except Exception as e:
            logger.error(f"❌ Failed to fetch proxies from {source_url}: {str(e)}")
            
    def _parse_proxy_list(self, content: str) -> List[Dict[str, Any]]:
        """Parse proxy list from various formats"""
        
        proxies = []
        lines = content.strip().split('\n')
        
        for line in lines:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
                
            try:
                # Handle different formats
                if ':' in line:
                    # Simple format: host:port
                    if line.count(':') == 1:
                        host, port = line.split(':')
                        proxies.append({
                            'host': host.strip(),
                            'port': int(port.strip()),
                            'source': 'external'
                        })
                    # Format with auth: host:port:user:pass
                    elif line.count(':') == 3:
                        parts = line.split(':')
                        proxies.append({
                            'host': parts[0].strip(),
                            'port': int(parts[1].strip()),
                            'username': parts[2].strip(),
                            'password': parts[3].strip(),
                            'source': 'external'
                        })
                        
                # JSON format
                elif line.startswith('{') and line.endswith('}'):
                    proxy_data = json.loads(line)
                    if 'host' in proxy_data and 'port' in proxy_data:
                        proxy_data['source'] = 'external'
                        proxies.append(proxy_data)
                        
            except Exception as e:
                logger.debug(f"Failed to parse proxy line '{line}': {str(e)}")
                continue
                
        return proxies
        
    async def _load_persisted_proxies(self):
        """Load proxies from persistent storage"""
        
        try:
            if AIOHTTP_AVAILABLE:
                async with aiofiles.open(self.config.storage_file, 'r') as f:
                    data = json.loads(await f.read())
            else:
                with open(self.config.storage_file, 'r') as f:
                    data = json.load(f)
                    
            # Restore proxies
            for proxy_data in data.get('proxies', []):
                proxy = ProxyEntry(**proxy_data)
                proxy_key = f"{proxy.host}:{proxy.port}"
                self.proxies[proxy_key] = proxy
                
                if proxy.is_working:
                    self.working_proxies.append(proxy_key)
                    
            logger.info(f"📂 Loaded {len(self.proxies)} persisted proxies")
            
        except FileNotFoundError:
            logger.info("📂 No persisted proxy file found")
        except Exception as e:
            logger.error(f"❌ Failed to load persisted proxies: {str(e)}")
            
    async def _save_proxies(self):
        """Save proxies to persistent storage"""
        
        try:
            data = {
                'proxies': [asdict(proxy) for proxy in self.proxies.values()],
                'stats': self._stats,
                'saved_at': time.time()
            }
            
            if AIOHTTP_AVAILABLE:
                async with aiofiles.open(self.config.storage_file, 'w') as f:
                    await f.write(json.dumps(data, indent=2))
            else:
                with open(self.config.storage_file, 'w') as f:
                    json.dump(data, f, indent=2)
                    
            logger.debug("💾 Saved proxy pool state")
            
        except Exception as e:
            logger.error(f"❌ Failed to save proxy pool: {str(e)}")
            
    def get_stats(self) -> Dict[str, Any]:
        """Get proxy pool statistics"""
        
        # Calculate stats
        total_proxies = len(self.proxies)
        working_proxies = len(self.working_proxies)
        
        # Protocol distribution
        by_protocol = defaultdict(int)
        by_country = defaultdict(int)
        by_anonymity = defaultdict(int)
        
        response_times = []
        success_rates = []
        
        for proxy in self.proxies.values():
            by_protocol[proxy.protocol] += 1
            by_country[proxy.country or 'Unknown'] += 1
            by_anonymity[proxy.anonymity] += 1
            
            if proxy.response_time > 0:
                response_times.append(proxy.response_time)
            if proxy.success_count + proxy.failure_count > 0:
                success_rates.append(proxy.success_rate)
                
        avg_response_time = sum(response_times) / len(response_times) if response_times else 0.0
        avg_success_rate = sum(success_rates) / len(success_rates) if success_rates else 0.0
        
        return {
            **self._stats,
            'total_proxies': total_proxies,
            'working_proxies': working_proxies,
            'working_percentage': (working_proxies / total_proxies * 100) if total_proxies > 0 else 0,
            'average_response_time': avg_response_time,
            'average_success_rate': avg_success_rate,
            'by_protocol': dict(by_protocol),
            'by_country': dict(by_country),
            'by_anonymity': dict(by_anonymity),
            'config': asdict(self.config)
        }
        
    async def cleanup(self):
        """Clean up resources"""
        
        if self.validation_task:
            self.validation_task.cancel()
            
        if self.refresh_task:
            self.refresh_task.cancel()
            
        if self.config.persistent_storage:
            await self._save_proxies()
            
        self.executor.shutdown(wait=False)

class ProxyPoolAdapter:
    """High-level adapter for proxy pool management"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = ProxyPoolConfig(**config)
        self.manager = ProxyPoolManager(self.config) if self.config.enabled else None
        
    async def initialize(self):
        """Initialize the adapter"""
        if not self.config.enabled:
            logger.info("Proxy pool adapter disabled")
            return
            
        if self.manager:
            await self.manager.initialize()
            logger.info("✅ Proxy pool adapter initialized")
        else:
            logger.error("❌ Proxy pool manager not available")
            
    async def get_proxy_for_request(self, session_id: Optional[str] = None,
                                  **filters) -> Dict[str, Any]:
        """
        Get a proxy for making requests.
        
        Returns:
        {
            'success': bool,
            'proxy_url': str,
            'host': str,
            'port': int,
            'protocol': str,
            'country': str,
            'success_rate': float,
            'response_time': float
        }
        """
        
        if not self.config.enabled or not self.manager:
            return {
                'success': False,
                'error': 'Proxy pool is disabled or not available'
            }
            
        try:
            proxy = await self.manager.get_proxy(session_id, filters)
            
            if proxy:
                return {
                    'success': True,
                    'proxy_url': proxy.proxy_url,
                    'host': proxy.host,
                    'port': proxy.port,
                    'protocol': proxy.protocol,
                    'country': proxy.country,
                    'anonymity': proxy.anonymity,
                    'success_rate': proxy.success_rate,
                    'response_time': proxy.response_time,
                    'method': 'proxy-pool'
                }
            else:
                return {
                    'success': False,
                    'error': 'No working proxy available',
                    'method': 'proxy-pool'
                }
                
        except Exception as e:
            logger.error(f"❌ Failed to get proxy: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'method': 'proxy-pool'
            }
            
    async def release_proxy(self, proxy_url: str, success: bool = True) -> Dict[str, Any]:
        """Release proxy after use"""
        
        if not self.config.enabled or not self.manager:
            return {'success': False, 'error': 'Proxy pool not available'}
            
        try:
            # Parse proxy URL to find proxy in pool
            parsed_url = urlparse(proxy_url)
            host = parsed_url.hostname
            port = parsed_url.port
            
            proxy_key = f"{host}:{port}"
            
            if proxy_key in self.manager.proxies:
                proxy = self.manager.proxies[proxy_key]
                await self.manager.release_proxy(proxy, success)
                
                return {
                    'success': True,
                    'method': 'proxy-pool'
                }
            else:
                return {
                    'success': False,
                    'error': 'Proxy not found in pool',
                    'method': 'proxy-pool'
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'method': 'proxy-pool'
            }
            
    async def add_proxies(self, proxy_list: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Add proxies to pool"""
        
        if not self.config.enabled or not self.manager:
            return {'success': False, 'error': 'Proxy pool not available'}
            
        try:
            added_count = await self.manager.add_proxy_list(proxy_list)
            
            return {
                'success': True,
                'added_count': added_count,
                'total_requested': len(proxy_list),
                'method': 'proxy-pool'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'method': 'proxy-pool'
            }
            
    async def validate_proxies(self) -> Dict[str, Any]:
        """Validate all proxies in pool"""
        
        if not self.config.enabled or not self.manager:
            return {'success': False, 'error': 'Proxy pool not available'}
            
        try:
            result = await self.manager.validate_all_proxies()
            result['success'] = True
            result['method'] = 'proxy-pool'
            
            return result
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'method': 'proxy-pool'
            }
            
    async def get_stats(self) -> Dict[str, Any]:
        """Get proxy pool statistics"""
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
def create_proxy_pool_adapter(config: Dict[str, Any]) -> ProxyPoolAdapter:
    """Create and configure proxy pool adapter"""
    return ProxyPoolAdapter(config)

# Example usage
async def main():
    """Example usage"""
    config = {
        'enabled': True,
        'max_proxies': 50,
        'rotation_strategy': 'best_first',
        'test_interval': 300,
        'debug': True
    }
    
    adapter = create_proxy_pool_adapter(config)
    
    try:
        await adapter.initialize()
        
        # Add some test proxies
        test_proxies = [
            {'host': '127.0.0.1', 'port': 8080, 'protocol': 'HTTP'},
            {'host': '127.0.0.1', 'port': 8081, 'protocol': 'HTTP'}
        ]
        
        result = await adapter.add_proxies(test_proxies)
        print(f"Added proxies: {result}")
        
        # Get proxy for request
        proxy_result = await adapter.get_proxy_for_request()
        
        if proxy_result['success']:
            print(f"✅ Got proxy: {proxy_result['proxy_url']}")
            print(f"Success rate: {proxy_result['success_rate']:.2%}")
            
            # Simulate successful request
            await adapter.release_proxy(proxy_result['proxy_url'], success=True)
        else:
            print(f"❌ Failed to get proxy: {proxy_result['error']}")
            
    finally:
        await adapter.cleanup()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
