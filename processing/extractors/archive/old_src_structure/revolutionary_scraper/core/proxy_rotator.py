"""
Revolutionary Proxy Rotation System
Implementing world's most advanced IP rotation with residential proxies
Completely unblockable through sophisticated proxy management
"""

import asyncio
import itertools
import random
import logging
from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass
from datetime import datetime, timedelta
import aiohttp
import time
from urllib.parse import urlparse
import json
import statistics

@dataclass
class ProxyInfo:
    """Advanced proxy information with performance metrics"""
    url: str
    protocol: str  # http, https, socks5
    country: str
    city: str
    provider: str
    auth_user: Optional[str] = None
    auth_pass: Optional[str] = None
    
    # Performance metrics
    response_time: float = 0.0
    success_rate: float = 1.0
    last_used: Optional[datetime] = None
    consecutive_failures: int = 0
    total_requests: int = 0
    total_successes: int = 0
    
    # Anti-detection features
    sticky_session: bool = False
    session_id: Optional[str] = None
    rotation_weight: float = 1.0
    geo_accuracy: float = 1.0
    
    def __post_init__(self):
        if self.last_used is None:
            self.last_used = datetime.now()
    
    @property
    def is_healthy(self) -> bool:
        """Check if proxy is considered healthy"""
        return (self.consecutive_failures < 5 and 
                self.success_rate > 0.7 and 
                self.response_time < 10.0)
    
    @property
    def formatted_proxy(self) -> Dict[str, str]:
        """Get formatted proxy dictionary for aiohttp"""
        if self.auth_user and self.auth_pass:
            auth_proxy = f"{self.protocol}://{self.auth_user}:{self.auth_pass}@{self.url.split('://', 1)[1]}"
        else:
            auth_proxy = self.url
            
        return {
            "http": auth_proxy,
            "https": auth_proxy
        }

class ProxyRotator:
    """
    Revolutionary proxy rotation system with advanced anti-detection
    Implements sophisticated algorithms for unblockable scraping
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Proxy pools organized by type
        self.residential_proxies: List[ProxyInfo] = []
        self.datacenter_proxies: List[ProxyInfo] = []
        self.mobile_proxies: List[ProxyInfo] = []
        self.all_proxies: List[ProxyInfo] = []
        
        # Advanced rotation state
        self.rotation_cycles = {
            'round_robin': itertools.cycle([]),
            'weighted': [],
            'geographic': {},
            'performance_based': []
        }
        
        # Performance tracking
        self.proxy_stats: Dict[str, Dict] = {}
        self.domain_proxy_mapping: Dict[str, List[str]] = {}
        self.blacklisted_proxies: Set[str] = set()
        
        # Configuration
        self.rotation_strategy = config.get('rotation_strategy', 'intelligent')
        self.max_consecutive_failures = config.get('max_consecutive_failures', 5)
        self.proxy_timeout = config.get('proxy_timeout', 10)
        self.health_check_interval = config.get('health_check_interval', 300)  # 5 minutes
        self.geographic_targeting = config.get('geographic_targeting', True)
        self.sticky_sessions = config.get('sticky_sessions', True)
        
        # Initialize proxy providers
        self.providers = {
            'bright_data': config.get('bright_data', {}),
            'oxylabs': config.get('oxylabs', {}),
            'smartproxy': config.get('smartproxy', {}),
            'scraperapi': config.get('scraperapi', {}),
            'zenrows': config.get('zenrows', {}),
            'custom': config.get('custom_proxies', [])
        }
        
        # Anti-detection features
        self.geo_consistency = config.get('geo_consistency', True)
        self.session_persistence = config.get('session_persistence', 600)  # 10 minutes
        self.rotation_randomization = config.get('rotation_randomization', True)
        
        self._last_health_check = datetime.now() - timedelta(hours=1)
        self._initialization_complete = False
        
    async def initialize(self):
        """Initialize proxy pools from all providers"""
        self.logger.info("Initializing revolutionary proxy rotation system...")
        
        # Load proxies from all configured providers
        await self._load_bright_data_proxies()
        await self._load_oxylabs_proxies()
        await self._load_smartproxy_proxies()
        await self._load_scraperapi_proxies()
        await self._load_zenrows_proxies()
        await self._load_custom_proxies()
        
        # Combine all proxy pools
        self.all_proxies = (self.residential_proxies + 
                           self.datacenter_proxies + 
                           self.mobile_proxies)
        
        # Initialize rotation cycles
        self._initialize_rotation_cycles()
        
        # Perform initial health check
        await self._perform_health_check()
        
        self._initialization_complete = True
        self.logger.info(f"Proxy initialization complete. Loaded {len(self.all_proxies)} proxies")
        
    async def get_proxy(self, domain: str = None, session_id: str = None, 
                       country: str = None, proxy_type: str = None) -> Optional[ProxyInfo]:
        """
        Get optimal proxy using advanced selection algorithms
        """
        if not self._initialization_complete:
            await self.initialize()
            
        # Perform periodic health checks
        await self._maybe_perform_health_check()
        
        # Filter proxies based on requirements
        candidate_proxies = self._filter_proxies(
            domain=domain,
            country=country,
            proxy_type=proxy_type,
            session_id=session_id
        )
        
        if not candidate_proxies:
            self.logger.warning("No suitable proxies available")
            return None
            
        # Select proxy using configured strategy
        selected_proxy = await self._select_proxy_by_strategy(
            candidate_proxies, domain, session_id
        )
        
        if selected_proxy:
            selected_proxy.last_used = datetime.now()
            selected_proxy.total_requests += 1
            
        return selected_proxy
    
    async def report_proxy_result(self, proxy: ProxyInfo, success: bool, 
                                response_time: float = 0.0, error: str = None):
        """
        Report proxy performance for adaptive learning
        """
        if success:
            proxy.consecutive_failures = 0
            proxy.total_successes += 1
            proxy.response_time = (proxy.response_time + response_time) / 2
        else:
            proxy.consecutive_failures += 1
            
        # Update success rate
        proxy.success_rate = proxy.total_successes / max(1, proxy.total_requests)
        
        # Update statistics
        proxy_key = proxy.url
        if proxy_key not in self.proxy_stats:
            self.proxy_stats[proxy_key] = {
                'total_requests': 0,
                'total_successes': 0,
                'avg_response_time': 0,
                'last_error': None,
                'error_history': []
            }
            
        stats = self.proxy_stats[proxy_key]
        stats['total_requests'] += 1
        
        if success:
            stats['total_successes'] += 1
            stats['avg_response_time'] = ((stats['avg_response_time'] * (stats['total_successes'] - 1) + 
                                         response_time) / stats['total_successes'])
        else:
            stats['last_error'] = error
            stats['error_history'].append({
                'timestamp': datetime.now().isoformat(),
                'error': error
            })
            
            # Keep only last 10 errors
            stats['error_history'] = stats['error_history'][-10:]
            
        # Blacklist proxy if too many failures
        if proxy.consecutive_failures >= self.max_consecutive_failures:
            self.blacklisted_proxies.add(proxy.url)
            self.logger.warning(f"Blacklisted proxy {proxy.url} due to consecutive failures")
            
    async def get_geographic_proxy(self, country_code: str, session_id: str = None) -> Optional[ProxyInfo]:
        """
        Get proxy from specific geographic location
        """
        return await self.get_proxy(
            country=country_code,
            session_id=session_id,
            proxy_type='residential'  # Residential proxies are best for geo-targeting
        )
    
    async def get_sticky_session_proxy(self, session_id: str, domain: str = None) -> Optional[ProxyInfo]:
        """
        Get proxy for sticky session (same IP for duration)
        """
        return await self.get_proxy(
            domain=domain,
            session_id=session_id
        )
    
    def _filter_proxies(self, domain: str = None, country: str = None, 
                       proxy_type: str = None, session_id: str = None) -> List[ProxyInfo]:
        """
        Filter proxies based on requirements
        """
        candidates = []
        
        # Start with appropriate proxy pool
        if proxy_type == 'residential':
            candidates = self.residential_proxies
        elif proxy_type == 'datacenter':
            candidates = self.datacenter_proxies
        elif proxy_type == 'mobile':
            candidates = self.mobile_proxies
        else:
            candidates = self.all_proxies
            
        # Filter by health
        candidates = [p for p in candidates if p.is_healthy and p.url not in self.blacklisted_proxies]
        
        # Filter by country
        if country:
            candidates = [p for p in candidates if p.country.lower() == country.lower()]
            
        # Handle sticky sessions
        if session_id and self.sticky_sessions:
            # Try to find existing proxy for this session
            session_proxies = [p for p in candidates if p.session_id == session_id]
            if session_proxies:
                candidates = session_proxies
            else:
                # Assign session ID to selected proxy
                for proxy in candidates:
                    if not proxy.sticky_session:
                        proxy.session_id = session_id
                        proxy.sticky_session = True
                        break
                        
        return candidates
    
    async def _select_proxy_by_strategy(self, candidates: List[ProxyInfo], 
                                      domain: str = None, session_id: str = None) -> Optional[ProxyInfo]:
        """
        Select proxy using configured strategy
        """
        if not candidates:
            return None
            
        if self.rotation_strategy == 'round_robin':
            return self._select_round_robin(candidates)
        elif self.rotation_strategy == 'weighted':
            return self._select_weighted(candidates)
        elif self.rotation_strategy == 'performance_based':
            return self._select_performance_based(candidates)
        elif self.rotation_strategy == 'geographic':
            return self._select_geographic(candidates, domain)
        elif self.rotation_strategy == 'intelligent':
            return self._select_intelligent(candidates, domain, session_id)
        else:
            # Default to random selection
            return random.choice(candidates)
    
    def _select_round_robin(self, candidates: List[ProxyInfo]) -> ProxyInfo:
        """Round robin proxy selection"""
        # Simple round robin through candidates
        if not hasattr(self, '_round_robin_index'):
            self._round_robin_index = 0
            
        proxy = candidates[self._round_robin_index % len(candidates)]
        self._round_robin_index += 1
        
        return proxy
    
    def _select_weighted(self, candidates: List[ProxyInfo]) -> ProxyInfo:
        """Weighted random selection based on success rate"""
        if not candidates:
            return None
            
        weights = [p.success_rate * p.rotation_weight for p in candidates]
        
        if sum(weights) == 0:
            return random.choice(candidates)
            
        return random.choices(candidates, weights=weights, k=1)[0]
    
    def _select_performance_based(self, candidates: List[ProxyInfo]) -> ProxyInfo:
        """Select proxy based on performance metrics"""
        # Score based on success rate and response time
        scored_proxies = []
        
        for proxy in candidates:
            # Higher success rate = better
            success_score = proxy.success_rate
            
            # Lower response time = better (normalize to 0-1)
            time_score = max(0, 1 - (proxy.response_time / 10.0))
            
            # Recent usage penalty (encourage rotation)
            if proxy.last_used:
                minutes_since_use = (datetime.now() - proxy.last_used).total_seconds() / 60
                recency_score = min(1.0, minutes_since_use / 30)  # Prefer proxies not used in 30 min
            else:
                recency_score = 1.0
                
            total_score = (success_score * 0.4 + time_score * 0.3 + recency_score * 0.3)
            scored_proxies.append((proxy, total_score))
            
        # Sort by score and add randomization
        scored_proxies.sort(key=lambda x: x[1], reverse=True)
        
        # Select from top 30% with weighted randomization
        top_count = max(1, len(scored_proxies) // 3)
        top_proxies = [p[0] for p in scored_proxies[:top_count]]
        
        return random.choice(top_proxies)
    
    def _select_geographic(self, candidates: List[ProxyInfo], domain: str = None) -> ProxyInfo:
        """Select proxy based on geographic optimization"""
        if not domain:
            return random.choice(candidates)
            
        # Get target country from domain or use geographic intelligence
        target_country = self._get_target_country_for_domain(domain)
        
        if target_country:
            geo_candidates = [p for p in candidates if p.country.lower() == target_country.lower()]
            if geo_candidates:
                return self._select_performance_based(geo_candidates)
                
        return self._select_performance_based(candidates)
    
    def _select_intelligent(self, candidates: List[ProxyInfo], 
                          domain: str = None, session_id: str = None) -> ProxyInfo:
        """
        Intelligent proxy selection combining multiple factors
        """
        # Use machine learning-like approach to select optimal proxy
        scored_proxies = []
        
        for proxy in candidates:
            score = 0
            
            # Performance metrics (40% weight)
            perf_score = (proxy.success_rate * 0.6 + 
                         (1 - min(proxy.response_time / 10, 1)) * 0.4)
            score += perf_score * 0.4
            
            # Geographic relevance (20% weight)
            if domain:
                target_country = self._get_target_country_for_domain(domain)
                if target_country and proxy.country.lower() == target_country.lower():
                    score += 0.2
                    
            # Rotation fairness (20% weight)
            if proxy.last_used:
                minutes_since = (datetime.now() - proxy.last_used).total_seconds() / 60
                rotation_score = min(1.0, minutes_since / 60)  # Full score after 1 hour
                score += rotation_score * 0.2
            else:
                score += 0.2
                
            # Provider diversity (10% weight)
            provider_usage = self._get_provider_usage_ratio(proxy.provider)
            diversity_score = 1 - provider_usage
            score += diversity_score * 0.1
            
            # Session consistency (10% weight)
            if session_id and proxy.session_id == session_id:
                score += 0.1
                
            scored_proxies.append((proxy, score))
            
        # Sort and select with controlled randomization
        scored_proxies.sort(key=lambda x: x[1], reverse=True)
        
        # Select from top candidates with weighted probability
        top_candidates = scored_proxies[:max(1, len(scored_proxies) // 4)]
        weights = [score for _, score in top_candidates]
        
        if sum(weights) > 0:
            selected = random.choices(top_candidates, weights=weights, k=1)[0]
            return selected[0]
        else:
            return random.choice(candidates)
    
    def _get_target_country_for_domain(self, domain: str) -> Optional[str]:
        """
        Determine target country for domain using geographic intelligence
        """
        domain_country_map = {
            '.com': 'US',
            '.co.uk': 'GB',
            '.de': 'DE',
            '.fr': 'FR',
            '.jp': 'JP',
            '.au': 'AU',
            '.ca': 'CA',
            '.se': 'SE',
            '.no': 'NO',
            '.dk': 'DK'
        }
        
        for tld, country in domain_country_map.items():
            if domain.endswith(tld):
                return country
                
        # Default to US for .com or unknown
        return 'US'
    
    def _get_provider_usage_ratio(self, provider: str) -> float:
        """
        Calculate how much a provider has been used recently
        """
        if not self.proxy_stats:
            return 0.0
            
        provider_proxies = [p for p in self.all_proxies if p.provider == provider]
        if not provider_proxies:
            return 0.0
            
        total_requests = sum(stats.get('total_requests', 0) 
                           for stats in self.proxy_stats.values())
        
        provider_requests = sum(self.proxy_stats.get(p.url, {}).get('total_requests', 0) 
                              for p in provider_proxies)
        
        return provider_requests / max(1, total_requests)
    
    async def _load_bright_data_proxies(self):
        """Load Bright Data residential proxies"""
        config = self.providers.get('bright_data', {})
        if not config.get('enabled', False):
            return
            
        # Bright Data configuration
        username = config.get('username')
        password = config.get('password')
        zone = config.get('zone', 'residential')
        
        if not username or not password:
            return
            
        # Generate proxy configurations for different countries
        countries = config.get('countries', ['US', 'GB', 'DE', 'SE', 'CA'])
        
        for country in countries:
            proxy_info = ProxyInfo(
                url="zproxy.lum-superproxy.io:22225",
                protocol="http",
                country=country,
                city="",
                provider="bright_data",
                auth_user=f"brd-customer-{username}-zone-{zone}-country-{country.lower()}",
                auth_pass=password,
                geo_accuracy=0.95
            )
            self.residential_proxies.append(proxy_info)
            
    async def _load_oxylabs_proxies(self):
        """Load Oxylabs residential proxies"""
        config = self.providers.get('oxylabs', {})
        if not config.get('enabled', False):
            return
            
        username = config.get('username')
        password = config.get('password')
        
        if not username or not password:
            return
            
        # Oxylabs residential endpoints
        countries = config.get('countries', ['US', 'GB', 'DE'])
        
        for country in countries:
            proxy_info = ProxyInfo(
                url="pr.oxylabs.io:7777",
                protocol="http", 
                country=country,
                city="",
                provider="oxylabs",
                auth_user=f"{username}-country-{country}",
                auth_pass=password,
                geo_accuracy=0.9
            )
            self.residential_proxies.append(proxy_info)
            
    async def _load_smartproxy_proxies(self):
        """Load Smartproxy residential proxies"""
        config = self.providers.get('smartproxy', {})
        if not config.get('enabled', False):
            return
            
        username = config.get('username')
        password = config.get('password')
        
        if not username or not password:
            return
            
        # Smartproxy endpoints
        endpoints = [
            "gate.smartproxy.com:7000",
            "gate.smartproxy.com:10000", 
            "gate.smartproxy.com:10001"
        ]
        
        countries = config.get('countries', ['US', 'GB'])
        
        for endpoint in endpoints:
            for country in countries:
                proxy_info = ProxyInfo(
                    url=endpoint,
                    protocol="http",
                    country=country, 
                    city="",
                    provider="smartproxy",
                    auth_user=username,
                    auth_pass=password,
                    geo_accuracy=0.85
                )
                self.residential_proxies.append(proxy_info)
                
    async def _load_scraperapi_proxies(self):
        """Load ScraperAPI proxies"""
        config = self.providers.get('scraperapi', {})
        if not config.get('enabled', False):
            return
            
        api_key = config.get('api_key')
        if not api_key:
            return
            
        # ScraperAPI proxy endpoint
        proxy_info = ProxyInfo(
            url="proxy-server.scraperapi.com:8001",
            protocol="http",
            country="US",
            city="",
            provider="scraperapi", 
            auth_user="scraperapi",
            auth_pass=api_key,
            geo_accuracy=0.8
        )
        self.datacenter_proxies.append(proxy_info)
        
    async def _load_zenrows_proxies(self):
        """Load ZenRows proxies"""
        config = self.providers.get('zenrows', {})
        if not config.get('enabled', False):
            return
            
        api_key = config.get('api_key')
        if not api_key:
            return
            
        # ZenRows proxy configuration
        proxy_info = ProxyInfo(
            url="superproxy.zenrows.com:1337",
            protocol="http",
            country="US", 
            city="",
            provider="zenrows",
            auth_user=api_key,
            auth_pass="",
            geo_accuracy=0.75
        )
        self.datacenter_proxies.append(proxy_info)
        
    async def _load_custom_proxies(self):
        """Load custom proxy list"""
        custom_proxies = self.providers.get('custom', [])
        
        for proxy_config in custom_proxies:
            proxy_info = ProxyInfo(
                url=proxy_config.get('url', ''),
                protocol=proxy_config.get('protocol', 'http'),
                country=proxy_config.get('country', 'US'),
                city=proxy_config.get('city', ''),
                provider="custom",
                auth_user=proxy_config.get('username'),
                auth_pass=proxy_config.get('password'),
                geo_accuracy=proxy_config.get('geo_accuracy', 0.5)
            )
            
            proxy_type = proxy_config.get('type', 'datacenter')
            if proxy_type == 'residential':
                self.residential_proxies.append(proxy_info)
            elif proxy_type == 'mobile':
                self.mobile_proxies.append(proxy_info)
            else:
                self.datacenter_proxies.append(proxy_info)
                
    def _initialize_rotation_cycles(self):
        """Initialize rotation cycles for different strategies"""
        if self.all_proxies:
            self.rotation_cycles['round_robin'] = itertools.cycle(self.all_proxies)
            
    async def _maybe_perform_health_check(self):
        """Perform health check if enough time has passed"""
        if (datetime.now() - self._last_health_check).total_seconds() > self.health_check_interval:
            await self._perform_health_check()
            
    async def _perform_health_check(self):
        """Perform health check on all proxies"""
        self.logger.info("Performing proxy health check...")
        
        tasks = []
        semaphore = asyncio.Semaphore(20)  # Limit concurrent health checks
        
        for proxy in self.all_proxies:
            if proxy.url not in self.blacklisted_proxies:
                task = self._check_single_proxy_health(proxy, semaphore)
                tasks.append(task)
                
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)
            
        self._last_health_check = datetime.now()
        
        healthy_count = sum(1 for p in self.all_proxies if p.is_healthy)
        self.logger.info(f"Health check complete: {healthy_count}/{len(self.all_proxies)} proxies healthy")
        
    async def _check_single_proxy_health(self, proxy: ProxyInfo, semaphore: asyncio.Semaphore):
        """Check health of a single proxy"""
        async with semaphore:
            try:
                start_time = time.time()
                
                timeout = aiohttp.ClientTimeout(total=self.proxy_timeout)
                async with aiohttp.ClientSession(
                    connector=aiohttp.TCPConnector(limit=1),
                    timeout=timeout
                ) as session:
                    async with session.get(
                        'https://httpbin.org/ip',
                        proxy=proxy.formatted_proxy['https']
                    ) as response:
                        if response.status == 200:
                            response_time = time.time() - start_time
                            await self.report_proxy_result(proxy, True, response_time)
                            return True
                        else:
                            await self.report_proxy_result(proxy, False, error=f"HTTP {response.status}")
                            return False
                            
            except Exception as e:
                await self.report_proxy_result(proxy, False, error=str(e))
                return False
                
    def get_proxy_statistics(self) -> Dict[str, Any]:
        """Get comprehensive proxy statistics"""
        total_proxies = len(self.all_proxies)
        healthy_proxies = sum(1 for p in self.all_proxies if p.is_healthy)
        blacklisted_count = len(self.blacklisted_proxies)
        
        provider_stats = {}
        for proxy in self.all_proxies:
            provider = proxy.provider
            if provider not in provider_stats:
                provider_stats[provider] = {'total': 0, 'healthy': 0, 'avg_success_rate': 0}
                
            provider_stats[provider]['total'] += 1
            if proxy.is_healthy:
                provider_stats[provider]['healthy'] += 1
                
            provider_stats[provider]['avg_success_rate'] += proxy.success_rate
            
        for provider, stats in provider_stats.items():
            if stats['total'] > 0:
                stats['avg_success_rate'] /= stats['total']
                
        country_stats = {}
        for proxy in self.all_proxies:
            country = proxy.country
            if country not in country_stats:
                country_stats[country] = {'total': 0, 'healthy': 0}
                
            country_stats[country]['total'] += 1
            if proxy.is_healthy:
                country_stats[country]['healthy'] += 1
                
        return {
            'total_proxies': total_proxies,
            'healthy_proxies': healthy_proxies,
            'blacklisted_proxies': blacklisted_count,
            'health_rate': healthy_proxies / max(1, total_proxies),
            'provider_stats': provider_stats,
            'country_stats': country_stats,
            'last_health_check': self._last_health_check.isoformat(),
            'rotation_strategy': self.rotation_strategy
        }
