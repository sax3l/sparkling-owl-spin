"""
Ultimate Proxy Rotator System - World's Most Advanced IP Rotation
Implements residential proxy pools, geographic targeting, and intelligent rotation strategies.
"""

import asyncio
import aiohttp
import random
import time
import json
import hashlib
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from collections import defaultdict, deque
import logging
import statistics
from urllib.parse import urlparse


@dataclass
class ProxyInfo:
    """Advanced proxy information with health monitoring"""
    host: str
    port: int
    username: Optional[str] = None
    password: Optional[str] = None
    proxy_type: str = 'http'  # http, https, socks4, socks5
    country: Optional[str] = None
    city: Optional[str] = None
    provider: str = 'unknown'
    session_id: Optional[str] = None
    
    # Performance metrics
    response_times: List[float] = field(default_factory=list)
    success_count: int = 0
    failure_count: int = 0
    last_used: Optional[datetime] = None
    last_test: Optional[datetime] = None
    
    # Advanced features
    is_residential: bool = False
    is_sticky: bool = False
    max_requests: int = 1000
    current_requests: int = 0
    cooldown_until: Optional[datetime] = None
    
    @property
    def success_rate(self) -> float:
        """Calculate success rate percentage"""
        total = self.success_count + self.failure_count
        return (self.success_count / total * 100) if total > 0 else 100.0
    
    @property
    def average_response_time(self) -> float:
        """Calculate average response time"""
        return statistics.mean(self.response_times) if self.response_times else 0.0
    
    @property
    def is_healthy(self) -> bool:
        """Determine if proxy is healthy"""
        if self.cooldown_until and datetime.now() < self.cooldown_until:
            return False
        return self.success_rate > 70.0 and len(self.response_times) > 0
    
    @property
    def url(self) -> str:
        """Get proxy URL for requests"""
        auth = f"{self.username}:{self.password}@" if self.username and self.password else ""
        return f"{self.proxy_type}://{auth}{self.host}:{self.port}"
    
    def record_success(self, response_time: float):
        """Record successful request"""
        self.success_count += 1
        self.current_requests += 1
        self.last_used = datetime.now()
        
        # Keep only last 20 response times for rolling average
        self.response_times.append(response_time)
        if len(self.response_times) > 20:
            self.response_times.pop(0)
    
    def record_failure(self):
        """Record failed request"""
        self.failure_count += 1
        self.current_requests += 1
        self.last_used = datetime.now()
        
        # Set cooldown for repeated failures
        if self.failure_count > 3 and self.success_rate < 50:
            self.cooldown_until = datetime.now() + timedelta(minutes=5)


@dataclass
class ProxyProviderConfig:
    """Configuration for proxy providers"""
    name: str
    enabled: bool = False
    endpoint_url: Optional[str] = None
    username: Optional[str] = None
    password: Optional[str] = None
    api_key: Optional[str] = None
    zone: Optional[str] = None
    countries: List[str] = field(default_factory=list)
    max_concurrent: int = 10
    rotation_interval: int = 300  # seconds
    session_duration: int = 600   # seconds for sticky sessions


class UltimateProxyRotator:
    """Ultimate proxy rotation system with advanced features"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.proxy_providers = self._initialize_providers()
        self.proxy_pools: Dict[str, List[ProxyInfo]] = defaultdict(list)
        self.active_proxies: List[ProxyInfo] = []
        self.failed_proxies: List[ProxyInfo] = []
        
        # Rotation strategies
        self.rotation_strategies = {
            'round_robin': self._round_robin_strategy,
            'random': self._random_strategy,
            'performance_based': self._performance_based_strategy,
            'geographic': self._geographic_strategy,
            'intelligent': self._intelligent_strategy
        }
        
        # Current rotation state
        self.current_strategy = config.get('rotation_strategy', 'intelligent')
        self.current_index = 0
        self.request_count = 0
        self.strategy_performance = defaultdict(list)
        
        # Session management
        self.sticky_sessions: Dict[str, ProxyInfo] = {}
        self.session_requests: Dict[str, int] = defaultdict(int)
        
        # Health monitoring
        self.health_check_interval = 300  # 5 minutes
        self.last_health_check = datetime.now()
        
        # Performance metrics
        self.performance_metrics = {
            'total_requests': 0,
            'successful_requests': 0,
            'failed_requests': 0,
            'average_response_time': 0.0,
            'proxy_switches': 0,
            'geographic_coverage': set()
        }
    
    def _initialize_providers(self) -> Dict[str, ProxyProviderConfig]:
        """Initialize proxy provider configurations"""
        providers = {}
        
        provider_configs = self.config.get('proxy_rotator', {}).get('providers', {})
        
        # Bright Data (Premium Residential)
        if provider_configs.get('bright_data', {}).get('enabled', False):
            bright_data_config = provider_configs['bright_data']
            providers['bright_data'] = ProxyProviderConfig(
                name='bright_data',
                enabled=True,
                endpoint_url="zproxy.lum-superproxy.io",
                username=bright_data_config.get('username'),
                password=bright_data_config.get('password'),
                zone=bright_data_config.get('zone', 'static_residential'),
                countries=bright_data_config.get('countries', ['US', 'GB', 'DE']),
                max_concurrent=50
            )
        
        # Oxylabs (Premium Datacenter & Residential)
        if provider_configs.get('oxylabs', {}).get('enabled', False):
            oxylabs_config = provider_configs['oxylabs']
            providers['oxylabs'] = ProxyProviderConfig(
                name='oxylabs',
                enabled=True,
                endpoint_url="pr.oxylabs.io",
                username=oxylabs_config.get('username'),
                password=oxylabs_config.get('password'),
                countries=oxylabs_config.get('countries', ['US', 'GB']),
                max_concurrent=30
            )
        
        # Smartproxy (Fast Residential)
        if provider_configs.get('smartproxy', {}).get('enabled', False):
            smartproxy_config = provider_configs['smartproxy']
            providers['smartproxy'] = ProxyProviderConfig(
                name='smartproxy',
                enabled=True,
                endpoint_url="gate.smartproxy.com",
                username=smartproxy_config.get('username'),
                password=smartproxy_config.get('password'),
                countries=smartproxy_config.get('countries', ['US']),
                max_concurrent=20
            )
        
        # ScraperAPI (Managed Service)
        if provider_configs.get('scraperapi', {}).get('enabled', False):
            scraperapi_config = provider_configs['scraperapi']
            providers['scraperapi'] = ProxyProviderConfig(
                name='scraperapi',
                enabled=True,
                endpoint_url="proxy-server.scraperapi.com",
                api_key=scraperapi_config.get('api_key'),
                countries=scraperapi_config.get('countries', ['US']),
                max_concurrent=25
            )
        
        # ZenRows (All-in-One)
        if provider_configs.get('zenrows', {}).get('enabled', False):
            zenrows_config = provider_configs['zenrows']
            providers['zenrows'] = ProxyProviderConfig(
                name='zenrows',
                enabled=True,
                endpoint_url="superproxy.zenrows.com",
                api_key=zenrows_config.get('api_key'),
                countries=zenrows_config.get('countries', ['US']),
                max_concurrent=15
            )
        
        return providers
    
    async def initialize(self):
        """Initialize proxy pools from all enabled providers"""
        print("🔄 Initializing Ultimate Proxy Rotator...")
        
        initialization_tasks = []
        for provider_name, provider in self.proxy_providers.items():
            if provider.enabled:
                task = self._initialize_provider_pool(provider_name, provider)
                initialization_tasks.append(task)
        
        if initialization_tasks:
            results = await asyncio.gather(*initialization_tasks, return_exceptions=True)
            
            total_proxies = sum(len(pool) for pool in self.proxy_pools.values())
            print(f"✅ Initialized {total_proxies} proxies from {len(self.proxy_providers)} providers")
            
            # Build active proxy list
            for pool in self.proxy_pools.values():
                self.active_proxies.extend(pool)
            
            # Initial health check
            await self._perform_health_check()
        else:
            print("⚠️ No proxy providers configured!")
    
    async def _initialize_provider_pool(self, provider_name: str, provider: ProxyProviderConfig):
        """Initialize proxy pool for specific provider"""
        try:
            if provider_name == 'bright_data':
                proxies = await self._initialize_bright_data(provider)
            elif provider_name == 'oxylabs':
                proxies = await self._initialize_oxylabs(provider)
            elif provider_name == 'smartproxy':
                proxies = await self._initialize_smartproxy(provider)
            elif provider_name == 'scraperapi':
                proxies = await self._initialize_scraperapi(provider)
            elif provider_name == 'zenrows':
                proxies = await self._initialize_zenrows(provider)
            else:
                proxies = []
            
            self.proxy_pools[provider_name] = proxies
            print(f"✅ {provider_name}: {len(proxies)} proxies initialized")
            
        except Exception as e:
            print(f"❌ Failed to initialize {provider_name}: {e}")
            self.proxy_pools[provider_name] = []
    
    async def _initialize_bright_data(self, provider: ProxyProviderConfig) -> List[ProxyInfo]:
        """Initialize Bright Data residential proxies"""
        proxies = []
        
        # Bright Data uses different ports and zones for different countries
        zone_ports = {
            'static_residential': 22225,
            'residential': 22000,
            'datacenter': 22900,
            'mobile': 22400
        }
        
        port = zone_ports.get(provider.zone, 22225)
        
        # Create proxy instances for each country
        for country in provider.countries:
            for session_id in range(1, 21):  # 20 sessions per country
                proxy = ProxyInfo(
                    host=provider.endpoint_url,
                    port=port,
                    username=f"{provider.username}-zone-{provider.zone}-country-{country.lower()}-session-{session_id}",
                    password=provider.password,
                    country=country,
                    provider='bright_data',
                    session_id=str(session_id),
                    is_residential=True,
                    is_sticky=True,
                    max_requests=1000
                )
                proxies.append(proxy)
        
        return proxies
    
    async def _initialize_oxylabs(self, provider: ProxyProviderConfig) -> List[ProxyInfo]:
        """Initialize Oxylabs proxies"""
        proxies = []
        
        # Oxylabs endpoint ports
        ports = [8000, 8001, 8002, 8003, 8004]  # Different endpoints
        
        for country in provider.countries:
            for session_id in range(1, 16):  # 15 sessions per country
                proxy = ProxyInfo(
                    host=provider.endpoint_url,
                    port=random.choice(ports),
                    username=f"{provider.username}-country-{country}",
                    password=provider.password,
                    country=country,
                    provider='oxylabs',
                    session_id=str(session_id),
                    is_residential=True,
                    max_requests=800
                )
                proxies.append(proxy)
        
        return proxies
    
    async def _initialize_smartproxy(self, provider: ProxyProviderConfig) -> List[ProxyInfo]:
        """Initialize Smartproxy residential proxies"""
        proxies = []
        
        # Smartproxy sticky session format
        for country in provider.countries:
            for session_id in range(1, 11):  # 10 sessions per country
                proxy = ProxyInfo(
                    host=provider.endpoint_url,
                    port=10000,  # Standard port
                    username=f"{provider.username}-country-{country.lower()}-session-{session_id}",
                    password=provider.password,
                    country=country,
                    provider='smartproxy',
                    session_id=str(session_id),
                    is_residential=True,
                    is_sticky=True,
                    max_requests=500
                )
                proxies.append(proxy)
        
        return proxies
    
    async def _initialize_scraperapi(self, provider: ProxyProviderConfig) -> List[ProxyInfo]:
        """Initialize ScraperAPI proxies"""
        proxies = []
        
        for country in provider.countries:
            proxy = ProxyInfo(
                host=provider.endpoint_url,
                port=8001,
                username='scraperapi',
                password=provider.api_key,
                country=country,
                provider='scraperapi',
                is_residential=True,
                max_requests=1000
            )
            proxies.append(proxy)
        
        return proxies
    
    async def _initialize_zenrows(self, provider: ProxyProviderConfig) -> List[ProxyInfo]:
        """Initialize ZenRows proxies"""
        proxies = []
        
        for country in provider.countries:
            proxy = ProxyInfo(
                host=provider.endpoint_url,
                port=8001,
                username=provider.api_key,
                password='premium_proxy',
                country=country,
                provider='zenrows',
                is_residential=True,
                max_requests=800
            )
            proxies.append(proxy)
        
        return proxies
    
    async def get_proxy(self, 
                      session_id: Optional[str] = None,
                      country: Optional[str] = None,
                      provider: Optional[str] = None) -> Optional[ProxyInfo]:
        """Get next proxy based on current rotation strategy"""
        
        # Check if health check is needed
        if (datetime.now() - self.last_health_check).seconds > self.health_check_interval:
            await self._perform_health_check()
        
        # Handle sticky sessions
        if session_id and session_id in self.sticky_sessions:
            proxy = self.sticky_sessions[session_id]
            if proxy.is_healthy and proxy.current_requests < proxy.max_requests:
                return proxy
        
        # Filter proxies based on criteria
        available_proxies = self._filter_proxies(country, provider)
        
        if not available_proxies:
            print("⚠️ No healthy proxies available!")
            return None
        
        # Apply rotation strategy
        strategy_func = self.rotation_strategies.get(self.current_strategy, self._intelligent_strategy)
        proxy = await strategy_func(available_proxies)
        
        # Set up sticky session if requested
        if session_id and proxy:
            self.sticky_sessions[session_id] = proxy
            self.session_requests[session_id] = 0
        
        self.request_count += 1
        return proxy
    
    def _filter_proxies(self, country: Optional[str] = None, provider: Optional[str] = None) -> List[ProxyInfo]:
        """Filter proxies based on criteria"""
        available_proxies = [p for p in self.active_proxies if p.is_healthy]
        
        if country:
            available_proxies = [p for p in available_proxies if p.country and p.country.lower() == country.lower()]
        
        if provider:
            available_proxies = [p for p in available_proxies if p.provider == provider]
        
        return available_proxies
    
    async def _round_robin_strategy(self, proxies: List[ProxyInfo]) -> Optional[ProxyInfo]:
        """Round-robin proxy selection"""
        if not proxies:
            return None
        
        proxy = proxies[self.current_index % len(proxies)]
        self.current_index += 1
        return proxy
    
    async def _random_strategy(self, proxies: List[ProxyInfo]) -> Optional[ProxyInfo]:
        """Random proxy selection"""
        return random.choice(proxies) if proxies else None
    
    async def _performance_based_strategy(self, proxies: List[ProxyInfo]) -> Optional[ProxyInfo]:
        """Select proxy based on performance metrics"""
        if not proxies:
            return None
        
        # Sort by success rate and response time
        sorted_proxies = sorted(proxies, key=lambda p: (p.success_rate, -p.average_response_time), reverse=True)
        
        # Use weighted random selection favoring better proxies
        weights = [proxy.success_rate + 1 for proxy in sorted_proxies]
        return random.choices(sorted_proxies, weights=weights)[0]
    
    async def _geographic_strategy(self, proxies: List[ProxyInfo]) -> Optional[ProxyInfo]:
        """Geographic-based proxy selection"""
        if not proxies:
            return None
        
        # Group by country and rotate between them
        country_groups = defaultdict(list)
        for proxy in proxies:
            if proxy.country:
                country_groups[proxy.country].append(proxy)
        
        if not country_groups:
            return random.choice(proxies)
        
        # Round-robin between countries, then within country
        countries = list(country_groups.keys())
        selected_country = countries[self.current_index % len(countries)]
        self.current_index += 1
        
        return random.choice(country_groups[selected_country])
    
    async def _intelligent_strategy(self, proxies: List[ProxyInfo]) -> Optional[ProxyInfo]:
        """AI-powered intelligent proxy selection"""
        if not proxies:
            return None
        
        # Multi-factor scoring system
        scored_proxies = []
        
        for proxy in proxies:
            score = 0.0
            
            # Success rate factor (40% weight)
            score += proxy.success_rate * 0.4
            
            # Response time factor (30% weight)
            if proxy.average_response_time > 0:
                response_score = max(0, 100 - proxy.average_response_time * 10)
                score += response_score * 0.3
            
            # Usage distribution factor (20% weight)
            usage_factor = max(0, 100 - (proxy.current_requests / proxy.max_requests * 100))
            score += usage_factor * 0.2
            
            # Provider diversity factor (10% weight)
            provider_bonus = 10 if proxy.provider == 'bright_data' else 5
            score += provider_bonus * 0.1
            
            scored_proxies.append((proxy, score))
        
        # Sort by score and use weighted selection
        scored_proxies.sort(key=lambda x: x[1], reverse=True)
        
        # Top 20% get higher probability
        top_count = max(1, len(scored_proxies) // 5)
        top_proxies = scored_proxies[:top_count]
        
        # Weighted random selection
        weights = [score for _, score in top_proxies]
        selected_proxy = random.choices([proxy for proxy, _ in top_proxies], weights=weights)[0]
        
        return selected_proxy
    
    async def record_request_result(self, proxy: ProxyInfo, success: bool, response_time: float = 0.0):
        """Record the result of a request for proxy health monitoring"""
        if success:
            proxy.record_success(response_time)
            self.performance_metrics['successful_requests'] += 1
        else:
            proxy.record_failure()
            self.performance_metrics['failed_requests'] += 1
        
        self.performance_metrics['total_requests'] += 1
        
        # Update average response time
        if response_time > 0:
            current_avg = self.performance_metrics['average_response_time']
            total_requests = self.performance_metrics['total_requests']
            self.performance_metrics['average_response_time'] = (
                (current_avg * (total_requests - 1) + response_time) / total_requests
            )
        
        # Track geographic coverage
        if proxy.country:
            self.performance_metrics['geographic_coverage'].add(proxy.country)
    
    async def _perform_health_check(self):
        """Perform health check on all proxies"""
        print("🔍 Performing proxy health check...")
        
        health_check_tasks = []
        for proxy in self.active_proxies:
            if (not proxy.last_test or 
                (datetime.now() - proxy.last_test).seconds > 300):  # Test every 5 minutes
                task = self._test_proxy_health(proxy)
                health_check_tasks.append(task)
        
        if health_check_tasks:
            await asyncio.gather(*health_check_tasks, return_exceptions=True)
        
        # Move unhealthy proxies to failed list
        healthy_proxies = [p for p in self.active_proxies if p.is_healthy]
        failed_proxies = [p for p in self.active_proxies if not p.is_healthy]
        
        self.active_proxies = healthy_proxies
        self.failed_proxies.extend(failed_proxies)
        
        self.last_health_check = datetime.now()
        
        print(f"✅ Health check complete: {len(healthy_proxies)} healthy, {len(failed_proxies)} failed")
    
    async def _test_proxy_health(self, proxy: ProxyInfo):
        """Test individual proxy health"""
        try:
            timeout = aiohttp.ClientTimeout(total=10)
            proxy_url = proxy.url
            
            async with aiohttp.ClientSession(timeout=timeout) as session:
                start_time = time.time()
                
                # Test with httpbin.org to get IP info
                async with session.get(
                    'https://httpbin.org/ip',
                    proxy=proxy_url
                ) as response:
                    if response.status == 200:
                        response_time = time.time() - start_time
                        proxy.record_success(response_time)
                        proxy.last_test = datetime.now()
                        return True
                    else:
                        proxy.record_failure()
                        proxy.last_test = datetime.now()
                        return False
                        
        except Exception as e:
            proxy.record_failure()
            proxy.last_test = datetime.now()
            return False
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get comprehensive performance metrics"""
        healthy_count = len([p for p in self.active_proxies if p.is_healthy])
        
        metrics = {
            'total_proxies': len(self.active_proxies) + len(self.failed_proxies),
            'healthy_proxies': healthy_count,
            'failed_proxies': len(self.failed_proxies),
            'health_percentage': (healthy_count / max(len(self.active_proxies), 1)) * 100,
            'requests_per_proxy': self.performance_metrics['total_requests'] / max(healthy_count, 1),
            'geographic_coverage': list(self.performance_metrics['geographic_coverage']),
            'provider_distribution': self._get_provider_distribution(),
            **self.performance_metrics
        }
        
        return metrics
    
    def _get_provider_distribution(self) -> Dict[str, int]:
        """Get distribution of proxies by provider"""
        distribution = defaultdict(int)
        for proxy in self.active_proxies:
            distribution[proxy.provider] += 1
        return dict(distribution)
    
    async def rotate_failed_proxies(self):
        """Attempt to rotate failed proxies back into active pool"""
        if not self.failed_proxies:
            return
        
        # Test failed proxies for recovery
        recovery_tasks = []
        for proxy in self.failed_proxies[:10]:  # Test only 10 at a time
            if proxy.cooldown_until and datetime.now() >= proxy.cooldown_until:
                task = self._test_proxy_health(proxy)
                recovery_tasks.append((proxy, task))
        
        if recovery_tasks:
            results = await asyncio.gather(*[task for _, task in recovery_tasks], return_exceptions=True)
            
            recovered = []
            for i, (proxy, _) in enumerate(recovery_tasks):
                if results[i] is True:
                    recovered.append(proxy)
                    print(f"✅ Proxy {proxy.host} recovered")
            
            # Move recovered proxies back to active pool
            for proxy in recovered:
                self.failed_proxies.remove(proxy)
                self.active_proxies.append(proxy)
    
    async def cleanup_sessions(self):
        """Cleanup expired sticky sessions"""
        current_time = datetime.now()
        expired_sessions = []
        
        for session_id, proxy in self.sticky_sessions.items():
            if (proxy.last_used and 
                (current_time - proxy.last_used).seconds > 600):  # 10 minute timeout
                expired_sessions.append(session_id)
        
        for session_id in expired_sessions:
            del self.sticky_sessions[session_id]
            if session_id in self.session_requests:
                del self.session_requests[session_id]


class ResidentialProxyManager:
    """Specialized manager for residential proxy pools"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.residential_pools: Dict[str, List[ProxyInfo]] = defaultdict(list)
        self.rotation_schedule = {}
        
    async def initialize_residential_pools(self):
        """Initialize residential proxy pools with geographic distribution"""
        # Implementation for managing residential proxy pools
        # with focus on geographic distribution and ISP diversity
        pass
    
    def get_residential_proxy(self, country: str, isp_preference: Optional[str] = None) -> Optional[ProxyInfo]:
        """Get residential proxy from specific country and ISP"""
        # Implementation for selecting residential proxies
        # based on geographic and ISP requirements
        pass


class GeographicProxyTargeting:
    """Advanced geographic proxy targeting system"""
    
    def __init__(self):
        self.country_codes = {
            'US': 'United States', 'GB': 'United Kingdom', 'DE': 'Germany',
            'FR': 'France', 'CA': 'Canada', 'AU': 'Australia', 'SE': 'Sweden',
            'NO': 'Norway', 'DK': 'Denmark', 'FI': 'Finland', 'NL': 'Netherlands'
        }
        
        self.timezone_mapping = {
            'US': ['America/New_York', 'America/Chicago', 'America/Denver', 'America/Los_Angeles'],
            'GB': ['Europe/London'],
            'DE': ['Europe/Berlin'],
            'SE': ['Europe/Stockholm']
        }
    
    def select_geographic_proxy(self, 
                              proxies: List[ProxyInfo], 
                              target_country: str,
                              target_timezone: Optional[str] = None) -> Optional[ProxyInfo]:
        """Select proxy based on geographic targeting requirements"""
        
        # Filter by country
        country_proxies = [p for p in proxies if p.country and p.country.upper() == target_country.upper()]
        
        if not country_proxies:
            return None
        
        # If timezone specified, prefer proxies that match
        if target_timezone:
            timezone_match = []
            country_timezones = self.timezone_mapping.get(target_country.upper(), [])
            if target_timezone in country_timezones:
                # In a real implementation, we'd have timezone data for each proxy
                timezone_match = country_proxies[:len(country_proxies)//2]  # Simulate timezone matching
            
            return random.choice(timezone_match) if timezone_match else random.choice(country_proxies)
        
        return random.choice(country_proxies)


# Export classes
__all__ = [
    'UltimateProxyRotator',
    'ResidentialProxyManager', 
    'GeographicProxyTargeting',
    'ProxyInfo',
    'ProxyProviderConfig'
]
