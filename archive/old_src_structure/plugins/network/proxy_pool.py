#!/usr/bin/env python3
"""
Proxy Pool Adapter för Sparkling-Owl-Spin
Proxy management and rotation för distributed crawling
"""

import logging
import asyncio
import aiohttp
import random
import time
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
import json
from urllib.parse import urlparse

logger = logging.getLogger(__name__)

class ProxyType(Enum):
    """Proxy types"""
    HTTP = "http"
    HTTPS = "https"
    SOCKS4 = "socks4"
    SOCKS5 = "socks5"

class ProxyStatus(Enum):
    """Proxy status"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    BLOCKED = "blocked"
    TESTING = "testing"
    FAILED = "failed"

@dataclass
class ProxyInfo:
    """Proxy information"""
    host: str
    port: int
    proxy_type: ProxyType
    username: Optional[str] = None
    password: Optional[str] = None
    country: Optional[str] = None
    region: Optional[str] = None
    provider: Optional[str] = None
    anonymity: Optional[str] = None  # transparent, anonymous, elite
    status: ProxyStatus = ProxyStatus.INACTIVE
    last_checked: Optional[datetime] = None
    response_time: Optional[float] = None
    success_rate: float = 0.0
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    consecutive_failures: int = 0
    created_at: datetime = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()
            
    @property
    def proxy_url(self) -> str:
        """Get proxy URL"""
        scheme = self.proxy_type.value
        if self.username and self.password:
            return f"{scheme}://{self.username}:{self.password}@{self.host}:{self.port}"
        return f"{scheme}://{self.host}:{self.port}"
        
    @property
    def is_authenticated(self) -> bool:
        """Check if proxy requires authentication"""
        return bool(self.username and self.password)
        
    def update_stats(self, success: bool, response_time: Optional[float] = None):
        """Update proxy statistics"""
        self.total_requests += 1
        self.last_checked = datetime.now()
        
        if response_time:
            # Moving average för response time
            if self.response_time is None:
                self.response_time = response_time
            else:
                self.response_time = (self.response_time * 0.8) + (response_time * 0.2)
        
        if success:
            self.successful_requests += 1
            self.consecutive_failures = 0
            self.status = ProxyStatus.ACTIVE
        else:
            self.failed_requests += 1
            self.consecutive_failures += 1
            
            # Mark as failed after too many consecutive failures
            if self.consecutive_failures >= 3:
                self.status = ProxyStatus.FAILED
                
        # Update success rate
        if self.total_requests > 0:
            self.success_rate = self.successful_requests / self.total_requests

class ProxyPoolAdapter:
    """Proxy Pool management för distributed crawling"""
    
    def __init__(self, plugin_info):
        self.plugin_info = plugin_info
        self.initialized = False
        self.proxies: List[ProxyInfo] = []
        self.active_proxies: List[ProxyInfo] = []
        self.proxy_index = 0
        self.test_urls = [
            "http://httpbin.org/ip",
            "https://api.ipify.org?format=json",
            "http://icanhazip.com/"
        ]
        self.session: Optional[aiohttp.ClientSession] = None
        self.stats = {
            "total_proxies": 0,
            "active_proxies": 0,
            "failed_proxies": 0,
            "blocked_proxies": 0,
            "total_requests": 0,
            "successful_requests": 0,
            "average_response_time": 0.0
        }
        
    async def initialize(self):
        """Initialize Proxy Pool adapter"""
        try:
            logger.info("🌐 Initializing Proxy Pool Adapter")
            
            # Create aiohttp session
            timeout = aiohttp.ClientTimeout(total=30, connect=10)
            self.session = aiohttp.ClientSession(timeout=timeout)
            
            # Load proxy lists från different sources
            await self._load_free_proxy_sources()
            await self._load_premium_proxy_sources()
            await self._load_custom_proxies()
            
            # Initial proxy testing
            if self.proxies:
                await self._test_all_proxies()
            else:
                logger.warning("⚠️ No proxies loaded - using mock proxies för testing")
                await self._create_mock_proxies()
                
            self._update_stats()
            self.initialized = True
            logger.info(f"✅ Proxy Pool initialized with {len(self.active_proxies)} active proxies")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize Proxy Pool: {str(e)}")
            await self._create_mock_proxies()  # Fallback to mock
            self.initialized = True
            
    async def _load_free_proxy_sources(self):
        """Load proxies från free proxy sources"""
        
        # Mock free proxy sources
        free_proxies = [
            {"host": "proxy1.free.com", "port": 8080, "type": "http", "country": "US"},
            {"host": "proxy2.free.com", "port": 3128, "type": "http", "country": "UK"}, 
            {"host": "proxy3.free.com", "port": 8000, "type": "https", "country": "DE"},
            {"host": "proxy4.free.com", "port": 1080, "type": "socks5", "country": "FR"},
            {"host": "proxy5.free.com", "port": 8080, "type": "http", "country": "SE"},
        ]
        
        for proxy_data in free_proxies:
            proxy = ProxyInfo(
                host=proxy_data["host"],
                port=proxy_data["port"],
                proxy_type=ProxyType(proxy_data["type"]),
                country=proxy_data.get("country"),
                provider="free_source",
                anonymity="anonymous"
            )
            self.proxies.append(proxy)
            
        logger.info(f"📥 Loaded {len(free_proxies)} free proxies")
        
    async def _load_premium_proxy_sources(self):
        """Load proxies från premium sources"""
        
        # Mock premium proxy sources
        premium_proxies = [
            {
                "host": "premium1.proxy.com", "port": 8080, "type": "http",
                "username": "user1", "password": "pass1", "country": "US", "anonymity": "elite"
            },
            {
                "host": "premium2.proxy.com", "port": 3128, "type": "https",
                "username": "user2", "password": "pass2", "country": "UK", "anonymity": "elite"
            },
            {
                "host": "premium3.proxy.com", "port": 1080, "type": "socks5",
                "username": "user3", "password": "pass3", "country": "DE", "anonymity": "elite"
            }
        ]
        
        for proxy_data in premium_proxies:
            proxy = ProxyInfo(
                host=proxy_data["host"],
                port=proxy_data["port"],
                proxy_type=ProxyType(proxy_data["type"]),
                username=proxy_data.get("username"),
                password=proxy_data.get("password"),
                country=proxy_data.get("country"),
                provider="premium_source",
                anonymity=proxy_data.get("anonymity", "anonymous")
            )
            self.proxies.append(proxy)
            
        logger.info(f"💎 Loaded {len(premium_proxies)} premium proxies")
        
    async def _load_custom_proxies(self):
        """Load custom proxy configurations"""
        
        # Load från config files, environment variables, etc.
        custom_proxies = [
            {
                "host": "custom1.internal.com", "port": 8080, "type": "http",
                "country": "SE", "provider": "internal", "anonymity": "transparent"
            },
            {
                "host": "custom2.internal.com", "port": 3128, "type": "https", 
                "country": "SE", "provider": "internal", "anonymity": "anonymous"
            }
        ]
        
        for proxy_data in custom_proxies:
            proxy = ProxyInfo(
                host=proxy_data["host"],
                port=proxy_data["port"],
                proxy_type=ProxyType(proxy_data["type"]),
                country=proxy_data.get("country"),
                provider=proxy_data.get("provider", "custom"),
                anonymity=proxy_data.get("anonymity", "anonymous")
            )
            self.proxies.append(proxy)
            
        logger.info(f"⚙️ Loaded {len(custom_proxies)} custom proxies")
        
    async def _create_mock_proxies(self):
        """Create mock proxies för testing"""
        mock_proxies = [
            ProxyInfo("127.0.0.1", 8080, ProxyType.HTTP, country="SE", provider="mock"),
            ProxyInfo("127.0.0.1", 3128, ProxyType.HTTPS, country="SE", provider="mock"),
            ProxyInfo("127.0.0.1", 1080, ProxyType.SOCKS5, country="SE", provider="mock"),
        ]
        
        for proxy in mock_proxies:
            proxy.status = ProxyStatus.ACTIVE
            proxy.success_rate = 0.95
            proxy.response_time = random.uniform(0.1, 0.5)
            self.proxies.append(proxy)
            self.active_proxies.append(proxy)
            
        logger.info("🎭 Created mock proxies för testing")
        
    async def _test_all_proxies(self):
        """Test all loaded proxies"""
        logger.info(f"🧪 Testing {len(self.proxies)} proxies...")
        
        # Test proxies in batches to avoid overwhelming
        batch_size = 10
        for i in range(0, len(self.proxies), batch_size):
            batch = self.proxies[i:i + batch_size]
            tasks = [self._test_proxy(proxy) for proxy in batch]
            await asyncio.gather(*tasks, return_exceptions=True)
            
            # Brief pause between batches
            await asyncio.sleep(1)
            
        # Update active proxy list
        self.active_proxies = [
            proxy for proxy in self.proxies 
            if proxy.status == ProxyStatus.ACTIVE
        ]
        
        logger.info(f"✅ Testing completed - {len(self.active_proxies)} active proxies")
        
    async def _test_proxy(self, proxy: ProxyInfo) -> bool:
        """Test individual proxy"""
        try:
            proxy.status = ProxyStatus.TESTING
            start_time = time.time()
            
            # Use a simple test URL
            test_url = random.choice(self.test_urls)
            
            # Configure proxy för aiohttp
            if proxy.proxy_type in [ProxyType.HTTP, ProxyType.HTTPS]:
                proxy_url = proxy.proxy_url
                
                # Mock proxy test - simulate success/failure
                await asyncio.sleep(random.uniform(0.1, 0.3))  # Simulate network delay
                
                # 80% success rate för mock testing
                success = random.random() < 0.8
                response_time = time.time() - start_time
                
                proxy.update_stats(success, response_time)
                
                if success:
                    logger.debug(f"✅ Proxy {proxy.host}:{proxy.port} - OK ({response_time:.3f}s)")
                    return True
                else:
                    logger.debug(f"❌ Proxy {proxy.host}:{proxy.port} - Failed")
                    return False
                    
            else:
                # SOCKS proxies need special handling
                proxy.status = ProxyStatus.INACTIVE
                logger.debug(f"⚠️ SOCKS proxy {proxy.host}:{proxy.port} - Not tested (needs pysocks)")
                return False
                
        except Exception as e:
            logger.debug(f"❌ Proxy {proxy.host}:{proxy.port} - Error: {str(e)}")
            proxy.update_stats(False)
            return False
            
    def get_next_proxy(self, exclude_failed: bool = True) -> Optional[ProxyInfo]:
        """Get next proxy using round-robin"""
        if not self.active_proxies:
            return None
            
        available_proxies = self.active_proxies
        if exclude_failed:
            available_proxies = [
                proxy for proxy in self.active_proxies 
                if proxy.status != ProxyStatus.FAILED
            ]
            
        if not available_proxies:
            return None
            
        # Round-robin selection
        proxy = available_proxies[self.proxy_index % len(available_proxies)]
        self.proxy_index += 1
        
        return proxy
        
    def get_random_proxy(self, country: Optional[str] = None, 
                        proxy_type: Optional[ProxyType] = None,
                        min_success_rate: float = 0.5) -> Optional[ProxyInfo]:
        """Get random proxy with filtering"""
        available_proxies = [
            proxy for proxy in self.active_proxies
            if (proxy.status == ProxyStatus.ACTIVE and
                proxy.success_rate >= min_success_rate and
                (country is None or proxy.country == country) and
                (proxy_type is None or proxy.proxy_type == proxy_type))
        ]
        
        if not available_proxies:
            return None
            
        return random.choice(available_proxies)
        
    def get_best_proxy(self, country: Optional[str] = None,
                      proxy_type: Optional[ProxyType] = None) -> Optional[ProxyInfo]:
        """Get best performing proxy"""
        available_proxies = [
            proxy for proxy in self.active_proxies
            if (proxy.status == ProxyStatus.ACTIVE and
                (country is None or proxy.country == country) and
                (proxy_type is None or proxy.proxy_type == proxy_type))
        ]
        
        if not available_proxies:
            return None
            
        # Sort by success rate and response time
        available_proxies.sort(
            key=lambda p: (p.success_rate, -p.response_time if p.response_time else 0),
            reverse=True
        )
        
        return available_proxies[0]
        
    async def create_proxy_session(self, proxy: Optional[ProxyInfo] = None) -> aiohttp.ClientSession:
        """Create aiohttp session with proxy configuration"""
        if proxy is None:
            proxy = self.get_next_proxy()
            
        if proxy is None:
            # Return session without proxy
            return aiohttp.ClientSession()
            
        # Configure proxy
        proxy_url = proxy.proxy_url
        
        # Create session with proxy
        connector = aiohttp.TCPConnector()
        session = aiohttp.ClientSession(
            connector=connector,
            timeout=aiohttp.ClientTimeout(total=30)
        )
        
        # Note: Real proxy support would be configured here
        logger.debug(f"🌐 Created session with proxy: {proxy.host}:{proxy.port}")
        
        return session
        
    async def test_proxy_health(self):
        """Test health of all active proxies"""
        logger.info("💓 Testing proxy health...")
        
        tasks = [self._test_proxy(proxy) for proxy in self.active_proxies[:10]]  # Test first 10
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Update active proxy list
        self.active_proxies = [
            proxy for proxy in self.proxies 
            if proxy.status == ProxyStatus.ACTIVE
        ]
        
        self._update_stats()
        logger.info(f"💓 Health check completed - {len(self.active_proxies)} proxies healthy")
        
    def mark_proxy_failed(self, proxy: ProxyInfo, reason: str = ""):
        """Mark proxy as failed"""
        proxy.status = ProxyStatus.FAILED
        proxy.consecutive_failures += 1
        
        if proxy in self.active_proxies:
            self.active_proxies.remove(proxy)
            
        logger.debug(f"💀 Marked proxy {proxy.host}:{proxy.port} as failed: {reason}")
        self._update_stats()
        
    def mark_proxy_blocked(self, proxy: ProxyInfo, reason: str = ""):
        """Mark proxy as blocked"""
        proxy.status = ProxyStatus.BLOCKED
        
        if proxy in self.active_proxies:
            self.active_proxies.remove(proxy)
            
        logger.debug(f"🚫 Marked proxy {proxy.host}:{proxy.port} as blocked: {reason}")
        self._update_stats()
        
    def get_proxy_stats(self) -> Dict[str, Any]:
        """Get proxy pool statistics"""
        return {
            "total_proxies": len(self.proxies),
            "active_proxies": len(self.active_proxies),
            "failed_proxies": len([p for p in self.proxies if p.status == ProxyStatus.FAILED]),
            "blocked_proxies": len([p for p in self.proxies if p.status == ProxyStatus.BLOCKED]),
            "countries": list(set(p.country for p in self.proxies if p.country)),
            "proxy_types": {
                ptype.value: len([p for p in self.proxies if p.proxy_type == ptype])
                for ptype in ProxyType
            },
            "providers": {
                provider: len([p for p in self.proxies if p.provider == provider])
                for provider in set(p.provider for p in self.proxies if p.provider)
            },
            "average_success_rate": sum(p.success_rate for p in self.active_proxies) / max(1, len(self.active_proxies)),
            "average_response_time": sum(p.response_time for p in self.active_proxies if p.response_time) / max(1, len([p for p in self.active_proxies if p.response_time]))
        }
        
    def get_proxies_by_country(self, country: str) -> List[ProxyInfo]:
        """Get proxies by country"""
        return [proxy for proxy in self.active_proxies if proxy.country == country]
        
    def get_proxies_by_type(self, proxy_type: ProxyType) -> List[ProxyInfo]:
        """Get proxies by type"""
        return [proxy for proxy in self.active_proxies if proxy.proxy_type == proxy_type]
        
    def get_premium_proxies(self) -> List[ProxyInfo]:
        """Get premium (authenticated) proxies"""
        return [proxy for proxy in self.active_proxies if proxy.is_authenticated]
        
    def get_proxy_by_host(self, host: str, port: int) -> Optional[ProxyInfo]:
        """Get specific proxy by host and port"""
        for proxy in self.proxies:
            if proxy.host == host and proxy.port == port:
                return proxy
        return None
        
    async def rotate_failed_proxies(self):
        """Re-test failed proxies to see if they're back online"""
        failed_proxies = [p for p in self.proxies if p.status == ProxyStatus.FAILED]
        
        if failed_proxies:
            logger.info(f"🔄 Re-testing {len(failed_proxies)} failed proxies...")
            
            for proxy in failed_proxies:
                # Reset failure count för re-testing
                proxy.consecutive_failures = max(0, proxy.consecutive_failures - 1)
                if proxy.consecutive_failures == 0:
                    proxy.status = ProxyStatus.INACTIVE
                    
            # Re-test some failed proxies
            test_batch = failed_proxies[:5]  # Test up to 5 at a time
            tasks = [self._test_proxy(proxy) for proxy in test_batch]
            await asyncio.gather(*tasks, return_exceptions=True)
            
            # Update active list
            newly_active = [p for p in test_batch if p.status == ProxyStatus.ACTIVE]
            self.active_proxies.extend(newly_active)
            
            if newly_active:
                logger.info(f"✅ {len(newly_active)} proxies recovered and re-activated")
                
    def _update_stats(self):
        """Update internal statistics"""
        self.stats.update({
            "total_proxies": len(self.proxies),
            "active_proxies": len(self.active_proxies),
            "failed_proxies": len([p for p in self.proxies if p.status == ProxyStatus.FAILED]),
            "blocked_proxies": len([p for p in self.proxies if p.status == ProxyStatus.BLOCKED]),
            "total_requests": sum(p.total_requests for p in self.proxies),
            "successful_requests": sum(p.successful_requests for p in self.proxies)
        })
        
        if self.active_proxies:
            avg_response_time = sum(
                p.response_time for p in self.active_proxies if p.response_time
            ) / max(1, len([p for p in self.active_proxies if p.response_time]))
            self.stats["average_response_time"] = avg_response_time
            
    async def export_proxy_list(self, format: str = "json") -> str:
        """Export proxy list in various formats"""
        if format.lower() == "json":
            proxy_data = []
            for proxy in self.proxies:
                proxy_data.append({
                    "host": proxy.host,
                    "port": proxy.port,
                    "type": proxy.proxy_type.value,
                    "status": proxy.status.value,
                    "country": proxy.country,
                    "provider": proxy.provider,
                    "success_rate": proxy.success_rate,
                    "response_time": proxy.response_time,
                    "total_requests": proxy.total_requests,
                    "is_authenticated": proxy.is_authenticated,
                    "last_checked": proxy.last_checked.isoformat() if proxy.last_checked else None
                })
            return json.dumps(proxy_data, indent=2)
            
        elif format.lower() == "txt":
            lines = []
            for proxy in self.active_proxies:
                if proxy.is_authenticated:
                    lines.append(f"{proxy.proxy_url}")
                else:
                    lines.append(f"{proxy.host}:{proxy.port}")
            return "\n".join(lines)
            
        else:
            return json.dumps({"error": f"Unsupported format: {format}"})
            
    async def cleanup(self):
        """Cleanup Proxy Pool adapter"""
        logger.info("🧹 Cleaning up Proxy Pool Adapter")
        
        if self.session:
            await self.session.close()
            
        self.proxies.clear()
        self.active_proxies.clear()
        self.stats.clear()
        self.initialized = False
        logger.info("✅ Proxy Pool Adapter cleanup completed")
