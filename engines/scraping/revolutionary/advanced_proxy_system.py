#!/usr/bin/env python3
"""
Revolutionary Advanced Proxy Management System v4.0
Enterprise-grade proxy rotation, quality assessment, and management.

Integrates:
- AWS API Gateway rotation (requests-ip-rotator)
- ProxyBroker for proxy discovery and validation
- Residential proxy management
- Proxy quality scoring and health monitoring
- Advanced rotation algorithms
- IP geolocation and filtering
"""

import asyncio
import logging
import json
import time
import random
import statistics
from pathlib import Path
from typing import Dict, List, Set, Optional, Tuple, Any, Union
from dataclasses import dataclass, field
from urllib.parse import urlparse
from concurrent.futures import ThreadPoolExecutor
import aiohttp
import requests
import yaml
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

# AWS API Gateway integration
try:
    from requests_ip_rotator import ApiGateway
    AWS_AVAILABLE = True
except ImportError:
    AWS_AVAILABLE = False
    logger.warning("requests-ip-rotator not available - AWS rotation disabled")

# ProxyBroker integration  
try:
    from proxybroker import Broker
    PROXYBROKER_AVAILABLE = True
except ImportError:
    PROXYBROKER_AVAILABLE = False
    logger.warning("ProxyBroker not available - proxy discovery disabled")

logger = logging.getLogger(__name__)

@dataclass
class ProxyInfo:
    """Information about a proxy server"""
    host: str
    port: int
    protocol: str = "http"  # http, https, socks4, socks5
    username: Optional[str] = None
    password: Optional[str] = None
    country: Optional[str] = None
    anonymity: Optional[str] = None  # transparent, anonymous, elite
    speed: float = 0.0  # Response time in seconds
    success_rate: float = 0.0  # Success rate (0.0 - 1.0)
    last_checked: float = 0.0
    fail_count: int = 0
    success_count: int = 0
    is_working: bool = False
    is_residential: bool = False
    provider: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def url(self) -> str:
        """Get proxy URL"""
        if self.username and self.password:
            return f"{self.protocol}://{self.username}:{self.password}@{self.host}:{self.port}"
        return f"{self.protocol}://{self.host}:{self.port}"
    
    @property
    def quality_score(self) -> float:
        """Calculate quality score (0.0 - 1.0)"""
        if self.success_count + self.fail_count == 0:
            return 0.5  # Unknown quality
            
        # Base score from success rate
        base_score = self.success_rate
        
        # Speed bonus (faster = better)
        speed_score = max(0, 1 - (self.speed / 10))  # 10s = 0 bonus
        
        # Anonymity bonus
        anonymity_bonus = {
            'elite': 0.3,
            'anonymous': 0.2,
            'transparent': 0.1
        }.get(self.anonymity, 0.1)
        
        # Residential bonus
        residential_bonus = 0.2 if self.is_residential else 0.0
        
        # Recent activity bonus
        time_since_check = time.time() - self.last_checked
        recency_bonus = max(0, 0.1 - (time_since_check / 3600))  # 1 hour = 0 bonus
        
        return min(1.0, base_score + (speed_score * 0.2) + anonymity_bonus + residential_bonus + recency_bonus)

@dataclass
class ProxyPool:
    """Pool of managed proxies"""
    proxies: List[ProxyInfo] = field(default_factory=list)
    blacklist: Set[str] = field(default_factory=set)  # host:port
    rotation_index: int = 0
    last_rotation: float = 0.0
    
    def add_proxy(self, proxy: ProxyInfo):
        """Add proxy to pool"""
        proxy_key = f"{proxy.host}:{proxy.port}"
        if proxy_key not in self.blacklist:
            # Remove existing proxy with same host:port
            self.proxies = [p for p in self.proxies if f"{p.host}:{p.port}" != proxy_key]
            self.proxies.append(proxy)
    
    def remove_proxy(self, proxy: ProxyInfo):
        """Remove proxy from pool"""
        proxy_key = f"{proxy.host}:{proxy.port}"
        self.proxies = [p for p in self.proxies if f"{p.host}:{p.port}" != proxy_key]
        self.blacklist.add(proxy_key)
    
    def get_working_proxies(self, min_quality: float = 0.5) -> List[ProxyInfo]:
        """Get working proxies above quality threshold"""
        return [p for p in self.proxies if p.is_working and p.quality_score >= min_quality]
    
    def get_next_proxy(self, strategy: str = "round_robin") -> Optional[ProxyInfo]:
        """Get next proxy based on strategy"""
        working_proxies = self.get_working_proxies()
        if not working_proxies:
            return None
            
        if strategy == "round_robin":
            proxy = working_proxies[self.rotation_index % len(working_proxies)]
            self.rotation_index += 1
            return proxy
        elif strategy == "random":
            return random.choice(working_proxies)
        elif strategy == "best_quality":
            return max(working_proxies, key=lambda p: p.quality_score)
        elif strategy == "fastest":
            return min(working_proxies, key=lambda p: p.speed)
        else:
            return working_proxies[0]

class AWSRotatorManager:
    """Manager for AWS API Gateway proxy rotation"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.gateways: Dict[str, Any] = {}
        self.aws_available = AWS_AVAILABLE
        
    async def setup_gateway(self, domain: str, regions: Optional[List[str]] = None) -> bool:
        """Setup API Gateway for domain"""
        if not self.aws_available:
            logger.error("AWS API Gateway not available")
            return False
            
        try:
            if regions is None:
                regions = self.config.get('regions', ['us-east-1', 'eu-west-1', 'ap-southeast-1'])
                
            gateway = ApiGateway(domain, regions=regions)
            
            # Start gateway
            gateway.start()
            
            # Test gateway
            test_session = requests.Session()
            test_session.mount(f"https://{domain}", gateway)
            
            response = test_session.get(f"https://{domain}", timeout=30)
            if response.status_code < 500:  # Accept any non-server error
                self.gateways[domain] = {
                    'gateway': gateway,
                    'session': test_session,
                    'regions': regions,
                    'created': time.time()
                }
                logger.info(f"AWS Gateway setup successful for {domain} in regions: {regions}")
                return True
            else:
                logger.warning(f"AWS Gateway test failed for {domain}: {response.status_code}")
                gateway.shutdown()
                return False
                
        except Exception as e:
            logger.error(f"Failed to setup AWS Gateway for {domain}: {str(e)}")
            return False
    
    async def get_session(self, domain: str) -> Optional[requests.Session]:
        """Get configured session for domain"""
        if domain in self.gateways:
            return self.gateways[domain]['session']
        return None
    
    async def cleanup_gateway(self, domain: str):
        """Cleanup gateway for domain"""
        if domain in self.gateways:
            try:
                self.gateways[domain]['gateway'].shutdown()
                logger.info(f"AWS Gateway cleaned up for {domain}")
            except Exception as e:
                logger.warning(f"Error cleaning up AWS Gateway for {domain}: {str(e)}")
            finally:
                del self.gateways[domain]
    
    async def cleanup_all(self):
        """Cleanup all gateways"""
        domains = list(self.gateways.keys())
        for domain in domains:
            await self.cleanup_gateway(domain)

class ProxyDiscovery:
    """Proxy discovery using ProxyBroker and other sources"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.broker_available = PROXYBROKER_AVAILABLE
        
    async def discover_proxies(self, limit: int = 100, countries: Optional[List[str]] = None) -> List[ProxyInfo]:
        """Discover proxies using ProxyBroker"""
        if not self.broker_available:
            logger.warning("ProxyBroker not available")
            return await self._discover_from_sources()
            
        proxies = []
        
        try:
            # Setup ProxyBroker
            broker_config = {
                'timeout': self.config.get('timeout', 10),
                'max_tries': self.config.get('max_tries', 3),
                'judges': self.config.get('judges', ['httpbin.org/ip']),
                'providers': self.config.get('providers', ['freeproxy-list', 'proxylist-plus'])
            }
            
            broker = Broker(**broker_config)
            
            # Setup filters
            filters = {
                'limit': limit,
                'level': 'Anonymous'  # Anonymous or Elite
            }
            
            if countries:
                filters['countries'] = countries
                
            # Discover proxies
            discovered = []
            async for proxy in broker.find(types=['HTTP', 'HTTPS'], **filters):
                proxy_info = ProxyInfo(
                    host=proxy.host,
                    port=proxy.port,
                    protocol='http',
                    country=proxy.geo.get('country') if proxy.geo else None,
                    anonymity=proxy.types.get('level', 'unknown').lower(),
                    speed=proxy.avg_resp_time or 0.0,
                    last_checked=time.time(),
                    provider='proxybroker'
                )
                discovered.append(proxy_info)
                
            logger.info(f"ProxyBroker discovered {len(discovered)} proxies")
            proxies.extend(discovered)
            
        except Exception as e:
            logger.error(f"ProxyBroker discovery failed: {str(e)}")
            
        # Fallback to other sources
        if not proxies:
            proxies = await self._discover_from_sources()
            
        return proxies
    
    async def _discover_from_sources(self) -> List[ProxyInfo]:
        """Discover proxies from free sources"""
        proxies = []
        sources = self.config.get('sources', [])
        
        for source in sources:
            try:
                if source['type'] == 'url_list':
                    source_proxies = await self._fetch_from_url_list(source)
                    proxies.extend(source_proxies)
                elif source['type'] == 'api':
                    source_proxies = await self._fetch_from_api(source)
                    proxies.extend(source_proxies)
                    
            except Exception as e:
                logger.error(f"Failed to fetch from source {source.get('name', 'unknown')}: {str(e)}")
                
        return proxies
    
    async def _fetch_from_url_list(self, source: Dict[str, Any]) -> List[ProxyInfo]:
        """Fetch proxies from URL list source"""
        proxies = []
        
        async with aiohttp.ClientSession() as session:
            async with session.get(source['url'], timeout=30) as response:
                if response.status == 200:
                    text = await response.text()
                    lines = text.strip().split('\n')
                    
                    for line in lines:
                        line = line.strip()
                        if ':' in line:
                            try:
                                host, port = line.split(':', 1)
                                proxy_info = ProxyInfo(
                                    host=host.strip(),
                                    port=int(port.strip()),
                                    protocol='http',
                                    provider=source.get('name', 'unknown'),
                                    last_checked=time.time()
                                )
                                proxies.append(proxy_info)
                            except ValueError:
                                continue
                                
        logger.info(f"Fetched {len(proxies)} proxies from {source.get('name')}")
        return proxies
    
    async def _fetch_from_api(self, source: Dict[str, Any]) -> List[ProxyInfo]:
        """Fetch proxies from API source"""
        proxies = []
        
        try:
            async with aiohttp.ClientSession() as session:
                headers = source.get('headers', {})
                async with session.get(source['url'], headers=headers, timeout=30) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        # Parse based on API format
                        proxy_list = data
                        if 'proxies' in data:
                            proxy_list = data['proxies']
                        elif 'data' in data:
                            proxy_list = data['data']
                            
                        for item in proxy_list:
                            try:
                                proxy_info = ProxyInfo(
                                    host=item.get('ip', item.get('host')),
                                    port=int(item.get('port')),
                                    protocol=item.get('protocol', 'http').lower(),
                                    country=item.get('country'),
                                    anonymity=item.get('anonymity', 'unknown').lower(),
                                    provider=source.get('name', 'unknown'),
                                    last_checked=time.time()
                                )
                                proxies.append(proxy_info)
                            except (ValueError, KeyError):
                                continue
                                
        except Exception as e:
            logger.error(f"API source {source.get('name')} failed: {str(e)}")
            
        logger.info(f"Fetched {len(proxies)} proxies from API {source.get('name')}")
        return proxies

class ProxyValidator:
    """Proxy validation and quality assessment"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.test_urls = config.get('test_urls', [
            'http://httpbin.org/ip',
            'https://httpbin.org/headers',
            'http://icanhazip.com/'
        ])
        
    async def validate_proxy(self, proxy: ProxyInfo, timeout: float = 10.0) -> bool:
        """Validate single proxy"""
        try:
            proxy_dict = {
                'http': proxy.url,
                'https': proxy.url
            }
            
            start_time = time.time()
            
            # Test with first available test URL
            for test_url in self.test_urls:
                try:
                    response = requests.get(
                        test_url,
                        proxies=proxy_dict,
                        timeout=timeout,
                        headers={'User-Agent': self._get_random_user_agent()}
                    )
                    
                    end_time = time.time()
                    proxy.speed = end_time - start_time
                    
                    if response.status_code == 200:
                        # Test successful
                        proxy.is_working = True
                        proxy.success_count += 1
                        proxy.last_checked = time.time()
                        
                        # Try to determine anonymity level
                        if 'httpbin.org' in test_url:
                            await self._check_anonymity(proxy, response)
                            
                        return True
                        
                except requests.exceptions.RequestException:
                    continue
                    
            # All tests failed
            proxy.is_working = False
            proxy.fail_count += 1
            proxy.last_checked = time.time()
            return False
            
        except Exception as e:
            logger.debug(f"Proxy validation error for {proxy.host}:{proxy.port}: {str(e)}")
            proxy.is_working = False
            proxy.fail_count += 1
            proxy.last_checked = time.time()
            return False
    
    async def validate_proxies(self, proxies: List[ProxyInfo], max_workers: int = 50) -> List[ProxyInfo]:
        """Validate multiple proxies concurrently"""
        logger.info(f"Validating {len(proxies)} proxies with {max_workers} workers")
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Create validation tasks
            tasks = []
            for proxy in proxies:
                task = executor.submit(asyncio.run, self.validate_proxy(proxy))
                tasks.append((proxy, task))
                
            # Wait for results
            validated_proxies = []
            for proxy, task in tasks:
                try:
                    is_valid = task.result(timeout=30)
                    if is_valid:
                        validated_proxies.append(proxy)
                except Exception as e:
                    logger.debug(f"Validation timeout for {proxy.host}:{proxy.port}")
                    
        working_count = len(validated_proxies)
        total_count = len(proxies)
        success_rate = working_count / total_count if total_count > 0 else 0
        
        logger.info(f"Validation complete: {working_count}/{total_count} proxies working ({success_rate:.1%})")
        return validated_proxies
    
    async def _check_anonymity(self, proxy: ProxyInfo, response: requests.Response):
        """Check proxy anonymity level"""
        try:
            data = response.json()
            
            # Check if our real IP is exposed
            if 'headers' in data:
                headers = data['headers']
                
                # Check for forwarded headers that expose real IP
                forwarded_headers = [
                    'X-Forwarded-For', 'X-Real-Ip', 'X-Originating-Ip',
                    'X-Remote-Ip', 'X-Client-Ip', 'Client-Ip'
                ]
                
                has_forwarded = any(header in headers for header in forwarded_headers)
                
                if has_forwarded:
                    proxy.anonymity = 'transparent'
                else:
                    # Check if proxy headers are present
                    proxy_headers = ['Via', 'X-Proxy-Id', 'Proxy-Connection']
                    has_proxy_headers = any(header in headers for header in proxy_headers)
                    
                    if has_proxy_headers:
                        proxy.anonymity = 'anonymous'
                    else:
                        proxy.anonymity = 'elite'
                        
        except Exception as e:
            logger.debug(f"Anonymity check failed for {proxy.host}:{proxy.port}: {str(e)}")
            proxy.anonymity = 'unknown'
    
    def _get_random_user_agent(self) -> str:
        """Get random user agent"""
        user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0'
        ]
        return random.choice(user_agents)

class ProxyManager:
    """Main proxy management system"""
    
    def __init__(self, config_path: Optional[str] = None):
        self.config = self._load_config(config_path)
        self.pool = ProxyPool()
        self.discovery = ProxyDiscovery(self.config.get('discovery', {}))
        self.validator = ProxyValidator(self.config.get('validation', {}))
        self.aws_rotator = AWSRotatorManager(self.config.get('aws', {}))
        self._health_check_task = None
        
    def _load_config(self, config_path: Optional[str]) -> Dict[str, Any]:
        """Load configuration from file or defaults"""
        default_config = {
            'discovery': {
                'timeout': 10,
                'max_tries': 3,
                'sources': [
                    {
                        'name': 'free-proxy-list',
                        'type': 'url_list',
                        'url': 'https://raw.githubusercontent.com/clarketm/proxy-list/master/proxy-list-raw.txt'
                    }
                ]
            },
            'validation': {
                'timeout': 10,
                'test_urls': [
                    'http://httpbin.org/ip',
                    'https://httpbin.org/headers'
                ]
            },
            'aws': {
                'enabled': False,
                'regions': ['us-east-1', 'eu-west-1', 'ap-southeast-1']
            },
            'rotation': {
                'strategy': 'round_robin',  # round_robin, random, best_quality, fastest
                'health_check_interval': 300,  # 5 minutes
                'min_quality_score': 0.5
            }
        }
        
        if config_path and Path(config_path).exists():
            try:
                with open(config_path, 'r') as f:
                    file_config = yaml.safe_load(f)
                    # Deep merge configurations
                    self._deep_merge(default_config, file_config)
            except Exception as e:
                logger.warning(f"Failed to load config from {config_path}: {str(e)}")
                
        return default_config
    
    def _deep_merge(self, base: dict, update: dict):
        """Deep merge two dictionaries"""
        for key, value in update.items():
            if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                self._deep_merge(base[key], value)
            else:
                base[key] = value
    
    async def initialize(self):
        """Initialize proxy manager"""
        logger.info("Initializing Advanced Proxy Management System v4.0")
        
        # Discover initial proxies
        await self.refresh_proxies()
        
        # Start health check task
        health_check_interval = self.config['rotation']['health_check_interval']
        self._health_check_task = asyncio.create_task(
            self._health_check_loop(health_check_interval)
        )
        
        logger.info(f"Proxy manager initialized with {len(self.pool.proxies)} proxies")
    
    async def refresh_proxies(self, limit: int = 100):
        """Refresh proxy pool with new discoveries"""
        logger.info(f"Discovering up to {limit} new proxies...")
        
        # Discover proxies
        discovered = await self.discovery.discover_proxies(limit)
        
        if discovered:
            # Validate discovered proxies
            validated = await self.validator.validate_proxies(discovered)
            
            # Add to pool
            for proxy in validated:
                self.pool.add_proxy(proxy)
                
            logger.info(f"Added {len(validated)} working proxies to pool")
        else:
            logger.warning("No proxies discovered")
    
    async def get_proxy(self, domain: Optional[str] = None) -> Optional[Union[ProxyInfo, requests.Session]]:
        """Get next proxy for use"""
        # Check if AWS rotation is enabled and available for this domain
        if (self.config.get('aws', {}).get('enabled', False) and 
            domain and 
            domain not in self.aws_rotator.gateways):
            
            if await self.aws_rotator.setup_gateway(domain):
                session = await self.aws_rotator.get_session(domain)
                if session:
                    return session
        
        # Use regular proxy pool
        strategy = self.config['rotation']['strategy']
        min_quality = self.config['rotation']['min_quality_score']
        
        working_proxies = self.pool.get_working_proxies(min_quality)
        if not working_proxies:
            logger.warning("No working proxies available, refreshing...")
            await self.refresh_proxies()
            working_proxies = self.pool.get_working_proxies(min_quality)
            
        if not working_proxies:
            logger.error("No working proxies available after refresh")
            return None
            
        return self.pool.get_next_proxy(strategy)
    
    async def report_proxy_result(self, proxy: ProxyInfo, success: bool, response_time: Optional[float] = None):
        """Report proxy usage result for quality tracking"""
        if success:
            proxy.success_count += 1
        else:
            proxy.fail_count += 1
            
        if response_time:
            proxy.speed = response_time
            
        # Update success rate
        total_attempts = proxy.success_count + proxy.fail_count
        if total_attempts > 0:
            proxy.success_rate = proxy.success_count / total_attempts
            
        # Remove proxy if it's consistently failing
        if proxy.fail_count >= 5 and proxy.success_rate < 0.2:
            logger.info(f"Removing failing proxy {proxy.host}:{proxy.port}")
            self.pool.remove_proxy(proxy)
    
    async def get_proxy_stats(self) -> Dict[str, Any]:
        """Get proxy pool statistics"""
        total = len(self.pool.proxies)
        working = len(self.pool.get_working_proxies())
        
        if total == 0:
            return {
                'total': 0,
                'working': 0,
                'success_rate': 0.0,
                'avg_quality': 0.0,
                'avg_speed': 0.0,
                'countries': {},
                'providers': {},
                'anonymity_levels': {}
            }
        
        # Calculate statistics
        working_proxies = self.pool.get_working_proxies()
        
        avg_quality = statistics.mean([p.quality_score for p in working_proxies]) if working_proxies else 0.0
        avg_speed = statistics.mean([p.speed for p in working_proxies if p.speed > 0]) if working_proxies else 0.0
        
        # Count by categories
        countries = {}
        providers = {}
        anonymity_levels = {}
        
        for proxy in working_proxies:
            # Countries
            country = proxy.country or 'Unknown'
            countries[country] = countries.get(country, 0) + 1
            
            # Providers
            provider = proxy.provider or 'Unknown'
            providers[provider] = providers.get(provider, 0) + 1
            
            # Anonymity levels
            anonymity = proxy.anonymity or 'Unknown'
            anonymity_levels[anonymity] = anonymity_levels.get(anonymity, 0) + 1
        
        return {
            'total': total,
            'working': working,
            'success_rate': working / total,
            'avg_quality': avg_quality,
            'avg_speed': avg_speed,
            'countries': countries,
            'providers': providers,
            'anonymity_levels': anonymity_levels,
            'aws_gateways': len(self.aws_rotator.gateways)
        }
    
    async def _health_check_loop(self, interval: float):
        """Background health check loop"""
        while True:
            try:
                await asyncio.sleep(interval)
                logger.info("Running proxy health check...")
                
                # Get proxies that haven't been checked recently
                stale_proxies = [
                    p for p in self.pool.proxies 
                    if time.time() - p.last_checked > interval
                ]
                
                if stale_proxies:
                    # Re-validate stale proxies
                    validated = await self.validator.validate_proxies(stale_proxies[:50])  # Limit batch size
                    
                    # Update pool
                    for proxy in stale_proxies:
                        if proxy not in validated:
                            proxy.is_working = False
                            
                    logger.info(f"Health check: {len(validated)}/{len(stale_proxies)} proxies still working")
                    
                # Refresh pool if running low on working proxies
                working_count = len(self.pool.get_working_proxies())
                if working_count < 10:
                    logger.info("Low proxy count, refreshing pool...")
                    await self.refresh_proxies(50)
                    
            except Exception as e:
                logger.error(f"Health check error: {str(e)}")
                
    async def cleanup(self):
        """Cleanup resources"""
        # Cancel health check task
        if self._health_check_task:
            self._health_check_task.cancel()
            try:
                await self._health_check_task
            except asyncio.CancelledError:
                pass
                
        # Cleanup AWS gateways
        await self.aws_rotator.cleanup_all()
        
        logger.info("Proxy manager cleanup complete")

# Example usage and CLI interface
async def main():
    """Example usage of Advanced Proxy Management System"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Revolutionary Advanced Proxy Management System v4.0")
    parser.add_argument("--config", help="Configuration file path")
    parser.add_argument("--discover", type=int, default=50, help="Number of proxies to discover")
    parser.add_argument("--test", help="Test URL for proxy validation")
    parser.add_argument("--aws-domain", help="Setup AWS rotation for domain")
    parser.add_argument("--stats", action="store_true", help="Show proxy statistics")
    
    args = parser.parse_args()
    
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Create proxy manager
    manager = ProxyManager(args.config)
    
    try:
        # Initialize manager
        await manager.initialize()
        
        # Setup AWS rotation if requested
        if args.aws_domain:
            success = await manager.aws_rotator.setup_gateway(args.aws_domain)
            print(f"🌐 AWS Gateway for {args.aws_domain}: {'✅ Success' if success else '❌ Failed'}")
            
        # Show statistics
        if args.stats:
            stats = await manager.get_proxy_stats()
            print(f"\n📊 Proxy Statistics:")
            print(f"   Total proxies: {stats['total']}")
            print(f"   Working proxies: {stats['working']}")
            print(f"   Success rate: {stats['success_rate']:.1%}")
            print(f"   Average quality: {stats['avg_quality']:.2f}")
            print(f"   Average speed: {stats['avg_speed']:.2f}s")
            print(f"   AWS gateways: {stats['aws_gateways']}")
            
            if stats['countries']:
                print(f"   Countries: {', '.join(f'{k}({v})' for k, v in stats['countries'].items())}")
                
        # Test proxy functionality
        if args.test:
            print(f"\n🔍 Testing proxy with {args.test}")
            proxy = await manager.get_proxy()
            
            if isinstance(proxy, ProxyInfo):
                # Regular proxy
                print(f"   Using proxy: {proxy.host}:{proxy.port} (quality: {proxy.quality_score:.2f})")
                
                try:
                    start_time = time.time()
                    response = requests.get(
                        args.test,
                        proxies={'http': proxy.url, 'https': proxy.url},
                        timeout=10
                    )
                    end_time = time.time()
                    
                    print(f"   ✅ Success: {response.status_code} in {end_time - start_time:.2f}s")
                    await manager.report_proxy_result(proxy, True, end_time - start_time)
                    
                except Exception as e:
                    print(f"   ❌ Failed: {str(e)}")
                    await manager.report_proxy_result(proxy, False)
                    
            elif hasattr(proxy, 'get'):  # AWS session
                # AWS session
                print(f"   Using AWS Gateway session")
                
                try:
                    start_time = time.time()
                    response = proxy.get(args.test, timeout=10)
                    end_time = time.time()
                    
                    print(f"   ✅ Success: {response.status_code} in {end_time - start_time:.2f}s")
                    
                except Exception as e:
                    print(f"   ❌ Failed: {str(e)}")
            else:
                print("   ❌ No proxy available")
                
        print(f"\n🎯 Proxy Management System Ready!")
        print(f"   Working proxies: {len(manager.pool.get_working_proxies())}")
        print(f"   AWS gateways: {len(manager.aws_rotator.gateways)}")
        
    except KeyboardInterrupt:
        print("\n🛑 Interrupted by user")
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        logger.exception("Manager failed")
    finally:
        await manager.cleanup()

if __name__ == "__main__":
    asyncio.run(main())
