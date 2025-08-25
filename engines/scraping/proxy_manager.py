#!/usr/bin/env python3
"""
Enhanced Proxy Manager för Sparkling-Owl-Spin
Extraherat från: proxy_pool + requests-ip-rotator
Integrerat från: vendors/proxy_pool
"""

import logging
import asyncio
import aiohttp
import json
import time
import random
from typing import Dict, List, Any, Optional, Union, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
import ipaddress
from pathlib import Path

logger = logging.getLogger(__name__)

class ProxyType(Enum):
    """Proxy types"""
    HTTP = "http"
    HTTPS = "https"
    SOCKS4 = "socks4"
    SOCKS5 = "socks5"

class ProxyAnonymity(Enum):
    """Proxy anonymity levels"""
    TRANSPARENT = "transparent"
    ANONYMOUS = "anonymous"
    ELITE = "elite"

class ProxySource(Enum):
    """Proxy sources"""
    FREE_PROXY_LIST = "free_proxy_list"
    PROXY_NOVA = "proxy_nova"
    SPYS_ONE = "spys_one"
    PROXY_DB = "proxy_db"
    PREMIUM_PROVIDERS = "premium_providers"
    CUSTOM_LIST = "custom_list"

@dataclass
class ProxyInfo:
    """Proxy information"""
    host: str
    port: int
    proxy_type: ProxyType
    anonymity: ProxyAnonymity
    country: Optional[str] = None
    response_time: Optional[float] = None
    last_checked: Optional[datetime] = None
    success_rate: float = 0.0
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    is_working: bool = False
    error_message: Optional[str] = None
    source: Optional[ProxySource] = None

@dataclass
class ProxyTestResult:
    """Proxy test result"""
    proxy: ProxyInfo
    success: bool
    response_time: float
    status_code: Optional[int] = None
    error_message: Optional[str] = None
    test_url: str = ""
    timestamp: datetime = None

class EnhancedProxyManager:
    """Enhanced Proxy Manager med smart rotation och health checking"""
    
    def __init__(self, plugin_info=None):
        self.plugin_info = plugin_info
        self.initialized = False
        self.session: Optional[aiohttp.ClientSession] = None
        
        # Proxy storage
        self.proxies: List[ProxyInfo] = []
        self.working_proxies: List[ProxyInfo] = []
        self.failed_proxies: List[ProxyInfo] = []
        
        # Rotation state
        self.current_proxy_index = 0
        self.proxy_usage_stats: Dict[str, Dict[str, Any]] = {}
        
        # Test URLs för proxy validation
        self.test_urls = [
            "http://httpbin.org/ip",
            "https://httpbin.org/ip",
            "http://ip-api.com/json",
            "https://api.ipify.org?format=json",
            "http://checkip.amazonaws.com"
        ]
        
        # Free proxy sources
        self.free_proxy_sources = {
            ProxySource.FREE_PROXY_LIST: {
                "url": "https://free-proxy-list.net/",
                "parser": self._parse_free_proxy_list
            },
            ProxySource.PROXY_NOVA: {
                "url": "https://www.proxynova.com/proxy-server-list/",
                "parser": self._parse_proxy_nova
            },
            ProxySource.SPYS_ONE: {
                "url": "https://spys.one/en/",
                "parser": self._parse_spys_one
            }
        }
        
        # Premium proxy providers
        self.premium_providers = {
            "luminati": {
                "endpoint": "http://zproxy.lum-superproxy.io:22225",
                "auth": True
            },
            "smartproxy": {
                "endpoint": "gate.smartproxy.com:7000", 
                "auth": True
            },
            "oxylabs": {
                "endpoint": "pr.oxylabs.io:7777",
                "auth": True
            }
        }
        
        # Configuration
        self.config = {
            "max_proxy_age": timedelta(hours=1),
            "test_timeout": 10,
            "min_success_rate": 0.7,
            "max_consecutive_failures": 5,
            "health_check_interval": 300,  # 5 minutes
            "rotation_strategy": "round_robin",  # round_robin, random, performance_based
            "enable_country_filtering": False,
            "preferred_countries": ["US", "UK", "DE", "FR"],
            "enable_geolocation": False,
            "auto_refresh_proxies": True,
            "concurrent_tests": 50
        }
        
        # Statistics
        self.stats = {
            "proxies_found": 0,
            "proxies_tested": 0,
            "working_proxies_count": 0,
            "failed_proxies_count": 0,
            "total_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "avg_response_time": 0.0,
            "last_refresh": None,
            "by_source": {},
            "by_country": {},
            "by_anonymity": {}
        }
        
        # Background tasks
        self.health_check_task: Optional[asyncio.Task] = None
        self.refresh_task: Optional[asyncio.Task] = None
        
    async def initialize(self):
        """Initialize Proxy Manager"""
        try:
            logger.info("🔄 Initializing Enhanced Proxy Manager")
            
            # Create aiohttp session för proxy testing
            connector = aiohttp.TCPConnector(
                limit=self.config["concurrent_tests"] * 2,
                limit_per_host=20,
                ttl_dns_cache=300,
                verify_ssl=False
            )
            
            timeout = aiohttp.ClientTimeout(total=self.config["test_timeout"])
            self.session = aiohttp.ClientSession(
                connector=connector,
                timeout=timeout
            )
            
            # Initialize statistics for sources
            for source in ProxySource:
                self.stats["by_source"][source.value] = {
                    "found": 0,
                    "tested": 0,
                    "working": 0,
                    "failed": 0
                }
                
            for anonymity in ProxyAnonymity:
                self.stats["by_anonymity"][anonymity.value] = {
                    "count": 0,
                    "working": 0
                }
                
            self.initialized = True
            
            # Start background tasks
            if self.config["auto_refresh_proxies"]:
                self.refresh_task = asyncio.create_task(self._auto_refresh_proxies())
                
            self.health_check_task = asyncio.create_task(self._health_check_loop())
            
            logger.info("✅ Enhanced Proxy Manager initialized")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize Proxy Manager: {str(e)}")
            self.initialized = True
            
    async def fetch_free_proxies(self, sources: Optional[List[ProxySource]] = None) -> List[ProxyInfo]:
        """Fetch proxies from free sources"""
        
        if not self.initialized:
            await self.initialize()
            
        if not sources:
            sources = list(ProxySource)
            
        all_proxies = []
        
        for source in sources:
            if source not in self.free_proxy_sources:
                continue
                
            try:
                logger.info(f"🔍 Fetching proxies from {source.value}")
                
                source_config = self.free_proxy_sources[source]
                
                async with self.session.get(source_config["url"]) as response:
                    if response.status == 200:
                        content = await response.text()
                        proxies = await source_config["parser"](content)
                        
                        for proxy in proxies:
                            proxy.source = source
                            
                        all_proxies.extend(proxies)
                        self.stats["by_source"][source.value]["found"] = len(proxies)
                        
                        logger.info(f"✅ Found {len(proxies)} proxies from {source.value}")
                    else:
                        logger.warning(f"⚠️ Failed to fetch from {source.value}: HTTP {response.status}")
                        
            except Exception as e:
                logger.error(f"❌ Error fetching from {source.value}: {str(e)}")
                continue
                
        # Remove duplicates
        unique_proxies = []
        seen = set()
        
        for proxy in all_proxies:
            proxy_key = f"{proxy.host}:{proxy.port}"
            if proxy_key not in seen:
                seen.add(proxy_key)
                unique_proxies.append(proxy)
                
        self.stats["proxies_found"] = len(unique_proxies)
        logger.info(f"📊 Found {len(unique_proxies)} unique proxies total")
        
        return unique_proxies
        
    async def _parse_free_proxy_list(self, content: str) -> List[ProxyInfo]:
        """Parse free-proxy-list.net"""
        
        proxies = []
        
        try:
            from bs4 import BeautifulSoup
            
            soup = BeautifulSoup(content, 'html.parser')
            table = soup.find('table', {'class': 'table'})
            
            if table:
                rows = table.find_all('tr')[1:]  # Skip header
                
                for row in rows:
                    cols = row.find_all('td')
                    if len(cols) >= 7:
                        host = cols[0].text.strip()
                        port = int(cols[1].text.strip())
                        country = cols[2].text.strip()
                        anonymity_text = cols[4].text.strip().lower()
                        https_support = cols[6].text.strip().lower() == 'yes'
                        
                        # Determine anonymity
                        if 'elite' in anonymity_text:
                            anonymity = ProxyAnonymity.ELITE
                        elif 'anonymous' in anonymity_text:
                            anonymity = ProxyAnonymity.ANONYMOUS
                        else:
                            anonymity = ProxyAnonymity.TRANSPARENT
                            
                        # Determine proxy type
                        proxy_type = ProxyType.HTTPS if https_support else ProxyType.HTTP
                        
                        proxy = ProxyInfo(
                            host=host,
                            port=port,
                            proxy_type=proxy_type,
                            anonymity=anonymity,
                            country=country
                        )
                        
                        proxies.append(proxy)
                        
        except Exception as e:
            logger.error(f"❌ Error parsing free-proxy-list: {str(e)}")
            
        return proxies
        
    async def _parse_proxy_nova(self, content: str) -> List[ProxyInfo]:
        """Parse proxynova.com"""
        
        proxies = []
        
        try:
            # Simplified parsing - real implementation would be more complex
            import re
            
            # Find proxy entries using regex
            pattern = r'(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}):(\d{2,5})'
            matches = re.findall(pattern, content)
            
            for match in matches:
                host = match[0]
                port = int(match[1])
                
                # Validate IP
                try:
                    ipaddress.ip_address(host)
                    proxy = ProxyInfo(
                        host=host,
                        port=port,
                        proxy_type=ProxyType.HTTP,
                        anonymity=ProxyAnonymity.ANONYMOUS
                    )
                    proxies.append(proxy)
                except:
                    continue
                    
        except Exception as e:
            logger.error(f"❌ Error parsing proxy-nova: {str(e)}")
            
        return proxies
        
    async def _parse_spys_one(self, content: str) -> List[ProxyInfo]:
        """Parse spys.one"""
        
        proxies = []
        
        try:
            # Simplified parsing
            import re
            
            pattern = r'(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}):(\d{2,5})'
            matches = re.findall(pattern, content)
            
            for match in matches:
                host = match[0]
                port = int(match[1])
                
                try:
                    ipaddress.ip_address(host)
                    proxy = ProxyInfo(
                        host=host,
                        port=port,
                        proxy_type=ProxyType.HTTP,
                        anonymity=ProxyAnonymity.ANONYMOUS
                    )
                    proxies.append(proxy)
                except:
                    continue
                    
        except Exception as e:
            logger.error(f"❌ Error parsing spys.one: {str(e)}")
            
        return proxies
        
    async def test_proxy(self, proxy: ProxyInfo, test_url: Optional[str] = None) -> ProxyTestResult:
        """Test single proxy"""
        
        if not test_url:
            test_url = random.choice(self.test_urls)
            
        start_time = time.time()
        
        try:
            # Build proxy URL
            proxy_url = f"{proxy.proxy_type.value}://{proxy.host}:{proxy.port}"
            
            # Test request
            async with self.session.get(
                test_url,
                proxy=proxy_url,
                timeout=aiohttp.ClientTimeout(total=self.config["test_timeout"])
            ) as response:
                
                response_time = time.time() - start_time
                
                if response.status == 200:
                    # Update proxy stats
                    proxy.last_checked = datetime.now()
                    proxy.response_time = response_time
                    proxy.is_working = True
                    proxy.successful_requests += 1
                    proxy.total_requests += 1
                    proxy.success_rate = proxy.successful_requests / proxy.total_requests
                    
                    return ProxyTestResult(
                        proxy=proxy,
                        success=True,
                        response_time=response_time,
                        status_code=response.status,
                        test_url=test_url,
                        timestamp=datetime.now()
                    )
                else:
                    proxy.failed_requests += 1
                    proxy.total_requests += 1
                    proxy.is_working = False
                    proxy.success_rate = proxy.successful_requests / proxy.total_requests
                    
                    return ProxyTestResult(
                        proxy=proxy,
                        success=False,
                        response_time=response_time,
                        status_code=response.status,
                        error_message=f"HTTP {response.status}",
                        test_url=test_url,
                        timestamp=datetime.now()
                    )
                    
        except Exception as e:
            response_time = time.time() - start_time
            
            proxy.failed_requests += 1
            proxy.total_requests += 1
            proxy.is_working = False
            proxy.error_message = str(e)
            if proxy.total_requests > 0:
                proxy.success_rate = proxy.successful_requests / proxy.total_requests
                
            return ProxyTestResult(
                proxy=proxy,
                success=False,
                response_time=response_time,
                error_message=str(e),
                test_url=test_url,
                timestamp=datetime.now()
            )
            
    async def test_proxies(self, proxies: List[ProxyInfo]) -> Tuple[List[ProxyInfo], List[ProxyInfo]]:
        """Test multiple proxies concurrently"""
        
        logger.info(f"🧪 Testing {len(proxies)} proxies...")
        
        # Create test tasks
        semaphore = asyncio.Semaphore(self.config["concurrent_tests"])
        
        async def test_with_semaphore(proxy):
            async with semaphore:
                return await self.test_proxy(proxy)
                
        tasks = [test_with_semaphore(proxy) for proxy in proxies]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        working_proxies = []
        failed_proxies = []
        
        for result in results:
            if isinstance(result, ProxyTestResult):
                if result.success:
                    working_proxies.append(result.proxy)
                else:
                    failed_proxies.append(result.proxy)
                    
                # Update statistics
                source = result.proxy.source
                if source:
                    self.stats["by_source"][source.value]["tested"] += 1
                    if result.success:
                        self.stats["by_source"][source.value]["working"] += 1
                    else:
                        self.stats["by_source"][source.value]["failed"] += 1
                        
                self.stats["by_anonymity"][result.proxy.anonymity.value]["count"] += 1
                if result.success:
                    self.stats["by_anonymity"][result.proxy.anonymity.value]["working"] += 1
                    
        self.stats["proxies_tested"] = len(proxies)
        self.stats["working_proxies_count"] = len(working_proxies)
        self.stats["failed_proxies_count"] = len(failed_proxies)
        
        logger.info(f"✅ Proxy testing complete: {len(working_proxies)} working, {len(failed_proxies)} failed")
        
        return working_proxies, failed_proxies
        
    async def refresh_proxy_pool(self, sources: Optional[List[ProxySource]] = None) -> None:
        """Refresh entire proxy pool"""
        
        logger.info("🔄 Refreshing proxy pool...")
        
        # Fetch new proxies
        new_proxies = await self.fetch_free_proxies(sources)
        
        # Test new proxies
        working_proxies, failed_proxies = await self.test_proxies(new_proxies)
        
        # Update proxy pool
        self.proxies = new_proxies
        self.working_proxies = working_proxies
        self.failed_proxies = failed_proxies
        
        # Reset rotation index
        self.current_proxy_index = 0
        
        self.stats["last_refresh"] = datetime.now()
        
        logger.info(f"🔄 Proxy pool refreshed: {len(self.working_proxies)} working proxies available")
        
    async def get_next_proxy(self) -> Optional[ProxyInfo]:
        """Get next proxy using configured rotation strategy"""
        
        if not self.working_proxies:
            logger.warning("⚠️ No working proxies available")
            return None
            
        if self.config["rotation_strategy"] == "round_robin":
            proxy = self.working_proxies[self.current_proxy_index]
            self.current_proxy_index = (self.current_proxy_index + 1) % len(self.working_proxies)
            
        elif self.config["rotation_strategy"] == "random":
            proxy = random.choice(self.working_proxies)
            
        elif self.config["rotation_strategy"] == "performance_based":
            # Sort by success rate and response time
            sorted_proxies = sorted(
                self.working_proxies,
                key=lambda p: (p.success_rate, -p.response_time if p.response_time else 0),
                reverse=True
            )
            proxy = sorted_proxies[0]
            
        else:
            proxy = self.working_proxies[0]
            
        # Update usage stats
        proxy_key = f"{proxy.host}:{proxy.port}"
        if proxy_key not in self.proxy_usage_stats:
            self.proxy_usage_stats[proxy_key] = {
                "total_uses": 0,
                "successful_uses": 0,
                "failed_uses": 0,
                "last_used": None
            }
            
        self.proxy_usage_stats[proxy_key]["total_uses"] += 1
        self.proxy_usage_stats[proxy_key]["last_used"] = datetime.now()
        
        return proxy
        
    async def mark_proxy_failed(self, proxy: ProxyInfo, error: str) -> None:
        """Mark proxy as failed"""
        
        proxy.failed_requests += 1
        proxy.error_message = error
        proxy.is_working = False
        
        if proxy.total_requests > 0:
            proxy.success_rate = proxy.successful_requests / proxy.total_requests
            
        # Remove from working proxies if success rate too low
        if proxy.success_rate < self.config["min_success_rate"]:
            if proxy in self.working_proxies:
                self.working_proxies.remove(proxy)
                self.failed_proxies.append(proxy)
                
                logger.warning(f"⚠️ Proxy moved to failed list: {proxy.host}:{proxy.port} (success rate: {proxy.success_rate:.2f})")
                
        # Update usage stats
        proxy_key = f"{proxy.host}:{proxy.port}"
        if proxy_key in self.proxy_usage_stats:
            self.proxy_usage_stats[proxy_key]["failed_uses"] += 1
            
    async def mark_proxy_successful(self, proxy: ProxyInfo) -> None:
        """Mark proxy as successful"""
        
        proxy.successful_requests += 1
        proxy.last_checked = datetime.now()
        proxy.is_working = True
        
        if proxy.total_requests > 0:
            proxy.success_rate = proxy.successful_requests / proxy.total_requests
            
        # Update usage stats
        proxy_key = f"{proxy.host}:{proxy.port}"
        if proxy_key in self.proxy_usage_stats:
            self.proxy_usage_stats[proxy_key]["successful_uses"] += 1
            
    async def _health_check_loop(self):
        """Background health check loop"""
        
        while self.initialized:
            try:
                await asyncio.sleep(self.config["health_check_interval"])
                
                if self.working_proxies:
                    # Test random sample of working proxies
                    sample_size = min(10, len(self.working_proxies))
                    sample_proxies = random.sample(self.working_proxies, sample_size)
                    
                    logger.debug(f"🔍 Health checking {sample_size} proxies...")
                    
                    for proxy in sample_proxies:
                        result = await self.test_proxy(proxy)
                        if not result.success:
                            await self.mark_proxy_failed(proxy, result.error_message or "Health check failed")
                            
            except Exception as e:
                logger.error(f"❌ Health check error: {str(e)}")
                
    async def _auto_refresh_proxies(self):
        """Background proxy refresh loop"""
        
        while self.initialized:
            try:
                await asyncio.sleep(3600)  # Refresh every hour
                
                # Only refresh if we're running low on working proxies
                if len(self.working_proxies) < 10:
                    logger.info("🔄 Auto-refreshing proxies (low proxy count)")
                    await self.refresh_proxy_pool()
                    
            except Exception as e:
                logger.error(f"❌ Auto-refresh error: {str(e)}")
                
    def get_proxy_statistics(self) -> Dict[str, Any]:
        """Get comprehensive proxy statistics"""
        
        return {
            "proxies_found": self.stats["proxies_found"],
            "proxies_tested": self.stats["proxies_tested"],
            "working_proxies_count": self.stats["working_proxies_count"],
            "failed_proxies_count": self.stats["failed_proxies_count"],
            "success_rate": (
                self.stats["working_proxies_count"] / max(1, self.stats["proxies_tested"])
            ) * 100 if self.stats["proxies_tested"] > 0 else 0,
            "total_requests": self.stats["total_requests"],
            "successful_requests": self.stats["successful_requests"],
            "failed_requests": self.stats["failed_requests"],
            "avg_response_time": self.stats["avg_response_time"],
            "last_refresh": self.stats["last_refresh"].isoformat() if self.stats["last_refresh"] else None,
            "by_source": self.stats["by_source"],
            "by_country": self.stats["by_country"],
            "by_anonymity": self.stats["by_anonymity"],
            "current_rotation_index": self.current_proxy_index,
            "rotation_strategy": self.config["rotation_strategy"]
        }
        
    def export_proxies(self, filename: str, format: str = "json") -> None:
        """Export working proxies to file"""
        
        try:
            if format == "json":
                data = []
                for proxy in self.working_proxies:
                    data.append({
                        "host": proxy.host,
                        "port": proxy.port,
                        "type": proxy.proxy_type.value,
                        "anonymity": proxy.anonymity.value,
                        "country": proxy.country,
                        "response_time": proxy.response_time,
                        "success_rate": proxy.success_rate,
                        "last_checked": proxy.last_checked.isoformat() if proxy.last_checked else None
                    })
                    
                with open(filename, 'w') as f:
                    json.dump(data, f, indent=2)
                    
            elif format == "txt":
                with open(filename, 'w') as f:
                    for proxy in self.working_proxies:
                        f.write(f"{proxy.host}:{proxy.port}\n")
                        
            logger.info(f"💾 Exported {len(self.working_proxies)} proxies to {filename}")
            
        except Exception as e:
            logger.error(f"❌ Export failed: {str(e)}")
            
    async def cleanup(self):
        """Cleanup Proxy Manager"""
        logger.info("🧹 Cleaning up Enhanced Proxy Manager")
        
        # Cancel background tasks
        if self.health_check_task:
            self.health_check_task.cancel()
            try:
                await self.health_check_task
            except asyncio.CancelledError:
                pass
                
        if self.refresh_task:
            self.refresh_task.cancel()
            try:
                await self.refresh_task
            except asyncio.CancelledError:
                pass
                
        # Close session
        if self.session:
            await self.session.close()
            
        # Clear data
        self.proxies.clear()
        self.working_proxies.clear()
        self.failed_proxies.clear()
        self.proxy_usage_stats.clear()
        
        self.initialized = False
        logger.info("✅ Enhanced Proxy Manager cleanup completed")

# Alias för pyramid architecture compatibility
ProxyManager = EnhancedProxyManager
