#!/usr/bin/env python3
"""
ProxyBroker Integration - Revolutionary Ultimate System v4.0
Asynchronous proxy discovery and management system
"""

import asyncio
import logging
import time
import json
import random
from typing import Dict, Any, Optional, List, Union, Set
from dataclasses import dataclass, asdict
from urllib.parse import urlparse
import ipaddress

try:
    import aiohttp
    from aiohttp_socks import ProxyConnector, ProxyType
    AIOHTTP_AVAILABLE = True
except ImportError:
    AIOHTTP_AVAILABLE = False

try:
    import proxybroker
    from proxybroker import Broker
    PROXYBROKER_AVAILABLE = True
except ImportError:
    PROXYBROKER_AVAILABLE = False

logger = logging.getLogger(__name__)

@dataclass
class ProxyInfo:
    """Container for proxy information"""
    host: str
    port: int
    protocol: str  # HTTP, HTTPS, SOCKS4, SOCKS5
    country: Optional[str] = None
    region: Optional[str] = None
    anonymity: Optional[str] = None  # Transparent, Anonymous, Elite
    response_time: Optional[float] = None
    last_checked: Optional[float] = None
    is_working: bool = False
    error_count: int = 0
    success_count: int = 0
    source: Optional[str] = None
    ssl_support: bool = False
    post_support: bool = False
    referer_support: bool = False
    user_agent_support: bool = False

@dataclass
class ProxyBrokerConfig:
    """Configuration for ProxyBroker"""
    enabled: bool = True
    max_proxies: int = 100
    timeout: int = 10
    max_tries: int = 3
    judge_timeout: int = 8
    provider_timeout: int = 15
    verify_ssl: bool = False
    protocols: List[str] = None  # HTTP, HTTPS, SOCKS4, SOCKS5
    anonymity_levels: List[str] = None  # Transparent, Anonymous, Elite  
    countries: List[str] = None  # Country codes: US, UK, DE, etc.
    providers: List[str] = None  # Specific providers to use
    concurrent_checks: int = 100
    retry_delay: float = 1.0
    refresh_interval: int = 3600  # Seconds
    debug: bool = False

class ProxyBrokerManager:
    """
    ProxyBroker manager for proxy discovery and management.
    
    Features:
    - Automatic proxy discovery from multiple sources
    - Real-time proxy validation and testing  
    - Protocol support (HTTP, HTTPS, SOCKS4, SOCKS5)
    - Anonymity level filtering
    - Geographic filtering
    - Performance monitoring
    - Auto-refresh of proxy lists
    """
    
    def __init__(self, config: ProxyBrokerConfig):
        self.config = config
        self.proxies: List[ProxyInfo] = []
        self.working_proxies: List[ProxyInfo] = []
        self.broker = None
        self.refresh_task = None
        self._stats = {
            'proxies_found': 0,
            'proxies_working': 0,
            'checks_performed': 0,
            'total_response_time': 0.0,
            'last_refresh': None
        }
        
        if not PROXYBROKER_AVAILABLE:
            raise ImportError("proxybroker not available. Install with: pip install proxybroker")
            
        if not AIOHTTP_AVAILABLE:
            raise ImportError("aiohttp not available. Install with: pip install aiohttp aiohttp-socks")
            
        # Set defaults
        if self.config.protocols is None:
            self.config.protocols = ['HTTP', 'HTTPS']
            
        if self.config.anonymity_levels is None:
            self.config.anonymity_levels = ['Anonymous', 'Elite']
            
    async def initialize(self):
        """Initialize ProxyBroker manager"""
        
        if not self.config.enabled:
            return
            
        logger.info("🚀 Initializing ProxyBroker manager...")
        
        # Initialize broker
        self.broker = Broker(
            max_conn=self.config.concurrent_checks,
            max_tries=self.config.max_tries,
            timeout=self.config.timeout,
            judge_timeout=self.config.judge_timeout,
            provider_timeout=self.config.provider_timeout,
            verify_ssl=self.config.verify_ssl
        )
        
        # Start initial proxy discovery
        await self.refresh_proxies()
        
        # Start auto-refresh task
        if self.config.refresh_interval > 0:
            self.refresh_task = asyncio.create_task(self._refresh_loop())
            
        logger.info("✅ ProxyBroker manager initialized")
        
    async def refresh_proxies(self):
        """Discover and refresh proxy list"""
        
        if not self.broker:
            logger.error("❌ ProxyBroker not initialized")
            return
            
        logger.info("🔍 Discovering proxies...")
        start_time = time.time()
        
        try:
            # Configure search criteria
            search_params = {
                'limit': self.config.max_proxies,
                'lvl': self.config.anonymity_levels,
                'types': self.config.protocols
            }
            
            if self.config.countries:
                search_params['countries'] = self.config.countries
                
            if self.config.providers:
                search_params['providers'] = self.config.providers
                
            # Clear existing proxies
            self.proxies.clear()
            self.working_proxies.clear()
            
            # Find proxies
            found_proxies = []
            
            async def proxy_callback(proxy):
                """Callback for each discovered proxy"""
                if proxy:
                    proxy_info = await self._convert_proxy(proxy)
                    if proxy_info:
                        found_proxies.append(proxy_info)
                        self.proxies.append(proxy_info)
                        
            # Start discovery
            await self.broker.find(
                types=search_params['types'],
                lvl=search_params['lvl'],
                limit=search_params['limit'],
                countries=search_params.get('countries'),
                providers=search_params.get('providers'),
                callback=proxy_callback
            )
            
            # Test discovered proxies
            await self._test_proxies(found_proxies)
            
            discovery_time = time.time() - start_time
            
            self._stats['proxies_found'] = len(self.proxies)
            self._stats['proxies_working'] = len(self.working_proxies)
            self._stats['last_refresh'] = time.time()
            
            logger.info(f"✅ Discovery complete: {len(self.proxies)} found, {len(self.working_proxies)} working ({discovery_time:.2f}s)")
            
        except Exception as e:
            logger.error(f"❌ Proxy discovery failed: {str(e)}")
            
    async def _convert_proxy(self, broker_proxy) -> Optional[ProxyInfo]:
        """Convert ProxyBroker proxy object to ProxyInfo"""
        
        try:
            return ProxyInfo(
                host=str(broker_proxy.host),
                port=int(broker_proxy.port),
                protocol=str(broker_proxy.types[0]).upper() if broker_proxy.types else 'HTTP',
                country=getattr(broker_proxy, 'country', None),
                region=getattr(broker_proxy, 'region', None),
                anonymity=str(broker_proxy.lvl) if hasattr(broker_proxy, 'lvl') else None,
                response_time=broker_proxy.avg_resp_time if hasattr(broker_proxy, 'avg_resp_time') else None,
                last_checked=time.time(),
                source='proxybroker',
                ssl_support='HTTPS' in str(broker_proxy.types) if broker_proxy.types else False
            )
            
        except Exception as e:
            logger.error(f"❌ Failed to convert proxy: {str(e)}")
            return None
            
    async def _test_proxies(self, proxies: List[ProxyInfo]):
        """Test proxy functionality"""
        
        if not proxies:
            return
            
        logger.info(f"🧪 Testing {len(proxies)} proxies...")
        
        # Test proxies concurrently
        semaphore = asyncio.Semaphore(self.config.concurrent_checks)
        
        async def test_single_proxy(proxy_info):
            async with semaphore:
                return await self._test_proxy(proxy_info)
                
        tasks = [test_single_proxy(proxy) for proxy in proxies]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process results
        working_count = 0
        for i, result in enumerate(results):
            if isinstance(result, bool) and result:
                proxies[i].is_working = True
                self.working_proxies.append(proxies[i])
                working_count += 1
            elif isinstance(result, Exception):
                logger.debug(f"Proxy test failed: {str(result)}")
                
        logger.info(f"✅ Proxy testing complete: {working_count}/{len(proxies)} working")
        
    async def _test_proxy(self, proxy_info: ProxyInfo) -> bool:
        """Test individual proxy"""
        
        try:
            # Determine proxy type for aiohttp
            if proxy_info.protocol in ['SOCKS4', 'SOCKS5']:
                proxy_type = ProxyType.SOCKS5 if proxy_info.protocol == 'SOCKS5' else ProxyType.SOCKS4
                connector = ProxyConnector(
                    proxy_type=proxy_type,
                    host=proxy_info.host,
                    port=proxy_info.port
                )
            else:
                # HTTP/HTTPS proxy
                connector = aiohttp.TCPConnector()
                proxy_url = f"http://{proxy_info.host}:{proxy_info.port}"
                
            start_time = time.time()
            
            async with aiohttp.ClientSession(
                connector=connector,
                timeout=aiohttp.ClientTimeout(total=self.config.timeout)
            ) as session:
                
                # Test with a simple request
                test_urls = [
                    'http://httpbin.org/ip',
                    'https://httpbin.org/ip'
                ]
                
                for test_url in test_urls:
                    try:
                        kwargs = {}
                        if proxy_info.protocol in ['HTTP', 'HTTPS']:
                            kwargs['proxy'] = proxy_url
                            
                        async with session.get(test_url, **kwargs) as response:
                            if response.status == 200:
                                response_time = time.time() - start_time
                                proxy_info.response_time = response_time
                                proxy_info.success_count += 1
                                
                                # Check if we got different IP (proxy working)
                                try:
                                    result = await response.json()
                                    proxy_ip = result.get('origin', '').split(',')[0].strip()
                                    
                                    if proxy_ip and proxy_ip != proxy_info.host:
                                        # Additional checks
                                        if test_url.startswith('https'):
                                            proxy_info.ssl_support = True
                                            
                                        self._stats['checks_performed'] += 1
                                        self._stats['total_response_time'] += response_time
                                        
                                        return True
                                        
                                except Exception:
                                    pass
                                    
                    except Exception as e:
                        logger.debug(f"Proxy test failed for {test_url}: {str(e)}")
                        continue
                        
            proxy_info.error_count += 1
            return False
            
        except Exception as e:
            logger.debug(f"❌ Proxy test error: {str(e)}")
            proxy_info.error_count += 1
            return False
            
    async def get_working_proxy(self, protocol: Optional[str] = None,
                               country: Optional[str] = None,
                               anonymity: Optional[str] = None) -> Optional[ProxyInfo]:
        """Get a working proxy with optional filters"""
        
        candidates = self.working_proxies.copy()
        
        # Apply filters
        if protocol:
            candidates = [p for p in candidates if p.protocol.upper() == protocol.upper()]
            
        if country:
            candidates = [p for p in candidates if p.country == country]
            
        if anonymity:
            candidates = [p for p in candidates if p.anonymity == anonymity]
            
        if not candidates:
            return None
            
        # Return random proxy or best performing one
        if len(candidates) == 1:
            return candidates[0]
        else:
            # Sort by performance (response time and success rate)
            def proxy_score(proxy):
                success_rate = proxy.success_count / max(proxy.success_count + proxy.error_count, 1)
                response_score = 1.0 / max(proxy.response_time or 1.0, 0.1)
                return success_rate * response_score
                
            candidates.sort(key=proxy_score, reverse=True)
            return candidates[0]
            
    async def get_random_proxy(self, **filters) -> Optional[ProxyInfo]:
        """Get a random working proxy with optional filters"""
        
        candidates = self.working_proxies.copy()
        
        # Apply filters
        for key, value in filters.items():
            if hasattr(ProxyInfo, key):
                candidates = [p for p in candidates if getattr(p, key) == value]
                
        return random.choice(candidates) if candidates else None
        
    async def get_proxy_list(self, working_only: bool = True,
                           limit: Optional[int] = None,
                           **filters) -> List[ProxyInfo]:
        """Get list of proxies with optional filters"""
        
        proxies = self.working_proxies if working_only else self.proxies
        candidates = proxies.copy()
        
        # Apply filters
        for key, value in filters.items():
            if hasattr(ProxyInfo, key):
                candidates = [p for p in candidates if getattr(p, key) == value]
                
        # Apply limit
        if limit and len(candidates) > limit:
            candidates = candidates[:limit]
            
        return candidates
        
    async def test_proxy_url(self, proxy_info: ProxyInfo, 
                           test_url: str = "http://httpbin.org/ip") -> Dict[str, Any]:
        """Test proxy with specific URL"""
        
        try:
            start_time = time.time()
            
            if proxy_info.protocol in ['SOCKS4', 'SOCKS5']:
                proxy_type = ProxyType.SOCKS5 if proxy_info.protocol == 'SOCKS5' else ProxyType.SOCKS4
                connector = ProxyConnector(
                    proxy_type=proxy_type,
                    host=proxy_info.host,
                    port=proxy_info.port
                )
                proxy_url = None
            else:
                connector = aiohttp.TCPConnector()
                proxy_url = f"http://{proxy_info.host}:{proxy_info.port}"
                
            async with aiohttp.ClientSession(
                connector=connector,
                timeout=aiohttp.ClientTimeout(total=self.config.timeout)
            ) as session:
                
                kwargs = {}
                if proxy_url:
                    kwargs['proxy'] = proxy_url
                    
                async with session.get(test_url, **kwargs) as response:
                    response_time = time.time() - start_time
                    content = await response.text()
                    
                    return {
                        'success': True,
                        'status_code': response.status,
                        'response_time': response_time,
                        'content': content,
                        'proxy': f"{proxy_info.host}:{proxy_info.port}"
                    }
                    
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'proxy': f"{proxy_info.host}:{proxy_info.port}"
            }
            
    async def remove_dead_proxies(self):
        """Remove non-working proxies"""
        
        before_count = len(self.working_proxies)
        
        # Test all working proxies
        tasks = [self._test_proxy(proxy) for proxy in self.working_proxies]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Keep only working proxies
        new_working = []
        for i, result in enumerate(results):
            if isinstance(result, bool) and result:
                new_working.append(self.working_proxies[i])
                
        self.working_proxies = new_working
        removed = before_count - len(self.working_proxies)
        
        if removed > 0:
            logger.info(f"🧹 Removed {removed} dead proxies")
            
    def get_stats(self) -> Dict[str, Any]:
        """Get proxy statistics"""
        
        avg_response_time = 0.0
        if self._stats['checks_performed'] > 0:
            avg_response_time = self._stats['total_response_time'] / self._stats['checks_performed']
            
        # Group by protocol
        by_protocol = {}
        for proxy in self.working_proxies:
            protocol = proxy.protocol
            if protocol not in by_protocol:
                by_protocol[protocol] = 0
            by_protocol[protocol] += 1
            
        # Group by country
        by_country = {}
        for proxy in self.working_proxies:
            country = proxy.country or 'Unknown'
            if country not in by_country:
                by_country[country] = 0
            by_country[country] += 1
            
        return {
            **self._stats,
            'total_proxies': len(self.proxies),
            'working_proxies': len(self.working_proxies),
            'average_response_time': avg_response_time,
            'by_protocol': by_protocol,
            'by_country': by_country,
            'config': asdict(self.config)
        }
        
    async def _refresh_loop(self):
        """Background proxy refresh loop"""
        
        while True:
            try:
                await asyncio.sleep(self.config.refresh_interval)
                logger.info("🔄 Auto-refreshing proxy list...")
                await self.refresh_proxies()
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"❌ Auto-refresh failed: {str(e)}")
                
    async def cleanup(self):
        """Clean up resources"""
        
        if self.refresh_task:
            self.refresh_task.cancel()
            try:
                await self.refresh_task
            except asyncio.CancelledError:
                pass
                
        if self.broker:
            try:
                await self.broker.stop()
            except Exception as e:
                logger.error(f"❌ Failed to stop broker: {str(e)}")

class ProxyBrokerAdapter:
    """High-level adapter for ProxyBroker integration"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = ProxyBrokerConfig(**config)
        self.manager = ProxyBrokerManager(self.config) if self.config.enabled else None
        
    async def initialize(self):
        """Initialize the adapter"""
        if not self.config.enabled:
            logger.info("ProxyBroker adapter disabled")
            return
            
        if not PROXYBROKER_AVAILABLE:
            logger.error("❌ proxybroker not available")
            if self.config.enabled:
                raise ImportError("proxybroker package required")
            return
            
        if self.manager:
            await self.manager.initialize()
            logger.info("✅ ProxyBroker adapter initialized")
        else:
            logger.error("❌ ProxyBroker manager not available")
            
    async def get_proxy_for_request(self, protocol: str = 'HTTP',
                                  country: Optional[str] = None,
                                  anonymity: str = 'Anonymous') -> Dict[str, Any]:
        """
        Get a proxy suitable for making requests.
        
        Returns:
        {
            'success': bool,
            'proxy_url': str,
            'protocol': str,
            'host': str,
            'port': int,
            'country': str,
            'response_time': float
        }
        """
        
        if not self.config.enabled or not self.manager:
            return {
                'success': False,
                'error': 'ProxyBroker is disabled or not available'
            }
            
        try:
            proxy = await self.manager.get_working_proxy(
                protocol=protocol,
                country=country,
                anonymity=anonymity
            )
            
            if proxy:
                proxy_url = f"http://{proxy.host}:{proxy.port}"
                if proxy.protocol in ['SOCKS4', 'SOCKS5']:
                    proxy_url = f"socks{proxy.protocol[-1]}://{proxy.host}:{proxy.port}"
                    
                return {
                    'success': True,
                    'proxy_url': proxy_url,
                    'protocol': proxy.protocol,
                    'host': proxy.host,
                    'port': proxy.port,
                    'country': proxy.country,
                    'anonymity': proxy.anonymity,
                    'response_time': proxy.response_time,
                    'method': 'proxybroker'
                }
            else:
                return {
                    'success': False,
                    'error': 'No working proxy found with specified criteria',
                    'method': 'proxybroker'
                }
                
        except Exception as e:
            logger.error(f"❌ Failed to get proxy: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'method': 'proxybroker'
            }
            
    async def get_proxy_list(self, limit: int = 10,
                           protocol: Optional[str] = None,
                           country: Optional[str] = None) -> Dict[str, Any]:
        """Get list of working proxies"""
        
        if not self.config.enabled or not self.manager:
            return {
                'success': False,
                'error': 'ProxyBroker is disabled or not available'
            }
            
        try:
            filters = {}
            if protocol:
                filters['protocol'] = protocol.upper()
            if country:
                filters['country'] = country
                
            proxies = await self.manager.get_proxy_list(
                working_only=True,
                limit=limit,
                **filters
            )
            
            proxy_data = []
            for proxy in proxies:
                proxy_data.append({
                    'host': proxy.host,
                    'port': proxy.port,
                    'protocol': proxy.protocol,
                    'country': proxy.country,
                    'anonymity': proxy.anonymity,
                    'response_time': proxy.response_time,
                    'ssl_support': proxy.ssl_support
                })
                
            return {
                'success': True,
                'proxies': proxy_data,
                'total_count': len(proxy_data),
                'method': 'proxybroker'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'method': 'proxybroker'
            }
            
    async def test_proxy(self, host: str, port: int, protocol: str = 'HTTP',
                        test_url: str = "http://httpbin.org/ip") -> Dict[str, Any]:
        """Test a specific proxy"""
        
        if not self.config.enabled or not self.manager:
            return {
                'success': False,
                'error': 'ProxyBroker is disabled or not available'
            }
            
        try:
            proxy_info = ProxyInfo(
                host=host,
                port=port,
                protocol=protocol.upper()
            )
            
            result = await self.manager.test_proxy_url(proxy_info, test_url)
            result['method'] = 'proxybroker-test'
            
            return result
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'method': 'proxybroker-test'
            }
            
    async def refresh_proxies(self) -> Dict[str, Any]:
        """Refresh proxy list"""
        
        if not self.config.enabled or not self.manager:
            return {
                'success': False,
                'error': 'ProxyBroker is disabled or not available'
            }
            
        try:
            start_time = time.time()
            await self.manager.refresh_proxies()
            refresh_time = time.time() - start_time
            
            stats = self.manager.get_stats()
            
            return {
                'success': True,
                'refresh_time': refresh_time,
                'proxies_found': stats['proxies_found'],
                'proxies_working': stats['proxies_working'],
                'method': 'proxybroker'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'method': 'proxybroker'
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
def create_proxybroker_adapter(config: Dict[str, Any]) -> ProxyBrokerAdapter:
    """Create and configure ProxyBroker adapter"""
    return ProxyBrokerAdapter(config)

# Example usage
async def main():
    """Example usage"""
    config = {
        'enabled': True,
        'max_proxies': 20,
        'protocols': ['HTTP', 'HTTPS'],
        'anonymity_levels': ['Anonymous', 'Elite'],
        'debug': True
    }
    
    adapter = create_proxybroker_adapter(config)
    
    try:
        await adapter.initialize()
        
        # Get proxy for request
        proxy_result = await adapter.get_proxy_for_request(
            protocol='HTTP',
            anonymity='Anonymous'
        )
        
        if proxy_result['success']:
            print(f"✅ Got proxy: {proxy_result['proxy_url']}")
            print(f"Country: {proxy_result['country']}")
            print(f"Response time: {proxy_result['response_time']:.2f}s")
            
            # Test the proxy
            test_result = await adapter.test_proxy(
                proxy_result['host'],
                proxy_result['port'],
                proxy_result['protocol']
            )
            
            if test_result['success']:
                print(f"✅ Proxy test successful: {test_result['status_code']}")
            else:
                print(f"❌ Proxy test failed: {test_result['error']}")
        else:
            print(f"❌ Failed to get proxy: {proxy_result['error']}")
            
    finally:
        await adapter.cleanup()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
