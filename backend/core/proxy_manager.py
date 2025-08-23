"""
Proxy management service for rotating proxies and anti-bot protection
Matches ScraperAPI's anti-bot capabilities with intelligent rotation
"""
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from enum import Enum
import asyncio
import aiohttp
import random
import logging
from dataclasses import dataclass
import json

class ProxyType(Enum):
    HTTP = "http"
    HTTPS = "https"
    SOCKS5 = "socks5"

class ProxyStatus(Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    BANNED = "banned"
    TESTING = "testing"

@dataclass
class Proxy:
    id: str
    host: str
    port: int
    username: Optional[str] = None
    password: Optional[str] = None
    proxy_type: ProxyType = ProxyType.HTTP
    status: ProxyStatus = ProxyStatus.INACTIVE
    location: Optional[str] = None
    provider: Optional[str] = None
    success_rate: float = 0.0
    response_time: float = 0.0
    last_used: Optional[datetime] = None
    last_tested: Optional[datetime] = None
    usage_count: int = 0
    ban_count: int = 0
    metadata: Dict[str, Any] = None

class ProxyPool:
    """Advanced proxy pool with intelligent rotation"""
    
    def __init__(self, test_url: str = "https://httpbin.org/ip"):
        self.proxies: Dict[str, Proxy] = {}
        self.test_url = test_url
        self.logger = logging.getLogger(__name__)
        self.rotation_strategy = "round_robin"  # round_robin, random, performance_based
        self.current_index = 0
    
    async def add_proxy(self, proxy: Proxy) -> bool:
        """Add proxy to pool and test it"""
        self.proxies[proxy.id] = proxy
        is_working = await self.test_proxy(proxy)
        if is_working:
            proxy.status = ProxyStatus.ACTIVE
            self.logger.info(f"Proxy {proxy.id} added successfully")
        else:
            proxy.status = ProxyStatus.INACTIVE
            self.logger.warning(f"Proxy {proxy.id} failed initial test")
        return is_working
    
    async def get_proxy(self, exclude_ids: List[str] = None) -> Optional[Proxy]:
        """Get next proxy based on rotation strategy"""
        active_proxies = [
            p for p in self.proxies.values() 
            if p.status == ProxyStatus.ACTIVE and (not exclude_ids or p.id not in exclude_ids)
        ]
        
        if not active_proxies:
            return None
        
        if self.rotation_strategy == "round_robin":
            proxy = active_proxies[self.current_index % len(active_proxies)]
            self.current_index += 1
        elif self.rotation_strategy == "random":
            proxy = random.choice(active_proxies)
        elif self.rotation_strategy == "performance_based":
            # Sort by success rate and response time
            active_proxies.sort(key=lambda p: (p.success_rate, -p.response_time), reverse=True)
            proxy = active_proxies[0]
        else:
            proxy = active_proxies[0]
        
        proxy.last_used = datetime.now()
        proxy.usage_count += 1
        return proxy
    
    async def mark_proxy_failed(self, proxy_id: str, reason: str = "request_failed"):
        """Mark proxy as failed and potentially ban it"""
        proxy = self.proxies.get(proxy_id)
        if not proxy:
            return
        
        proxy.ban_count += 1
        
        # Ban proxy if too many failures
        if proxy.ban_count >= 5:
            proxy.status = ProxyStatus.BANNED
            self.logger.warning(f"Proxy {proxy_id} banned after {proxy.ban_count} failures")
        else:
            # Temporarily deactivate
            proxy.status = ProxyStatus.INACTIVE
            self.logger.info(f"Proxy {proxy_id} deactivated ({reason})")
    
    async def test_proxy(self, proxy: Proxy) -> bool:
        """Test if proxy is working"""
        proxy_url = self._get_proxy_url(proxy)
        
        try:
            timeout = aiohttp.ClientTimeout(total=10)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                start_time = datetime.now()
                async with session.get(self.test_url, proxy=proxy_url) as response:
                    end_time = datetime.now()
                    
                    if response.status == 200:
                        proxy.response_time = (end_time - start_time).total_seconds()
                        proxy.last_tested = datetime.now()
                        proxy.success_rate = min(proxy.success_rate + 0.1, 1.0)
                        return True
                    else:
                        proxy.success_rate = max(proxy.success_rate - 0.1, 0.0)
                        return False
        except Exception as e:
            self.logger.error(f"Proxy test failed for {proxy.id}: {e}")
            proxy.success_rate = max(proxy.success_rate - 0.2, 0.0)
            return False
    
    async def health_check(self):
        """Perform health check on all proxies"""
        tasks = []
        for proxy in self.proxies.values():
            if proxy.status in [ProxyStatus.ACTIVE, ProxyStatus.INACTIVE]:
                tasks.append(self.test_proxy(proxy))
        
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)
    
    def _get_proxy_url(self, proxy: Proxy) -> str:
        """Generate proxy URL"""
        if proxy.username and proxy.password:
            return f"{proxy.proxy_type.value}://{proxy.username}:{proxy.password}@{proxy.host}:{proxy.port}"
        else:
            return f"{proxy.proxy_type.value}://{proxy.host}:{proxy.port}"
    
    def get_stats(self) -> Dict[str, Any]:
        """Get proxy pool statistics"""
        total = len(self.proxies)
        by_status = {}
        by_location = {}
        
        for proxy in self.proxies.values():
            by_status[proxy.status.value] = by_status.get(proxy.status.value, 0) + 1
            if proxy.location:
                by_location[proxy.location] = by_location.get(proxy.location, 0) + 1
        
        avg_success_rate = sum(p.success_rate for p in self.proxies.values()) / total if total > 0 else 0
        avg_response_time = sum(p.response_time for p in self.proxies.values()) / total if total > 0 else 0
        
        return {
            'total_proxies': total,
            'by_status': by_status,
            'by_location': by_location,
            'avg_success_rate': avg_success_rate,
            'avg_response_time': avg_response_time,
            'rotation_strategy': self.rotation_strategy
        }

class AntiBotService:
    """Anti-bot protection service matching industry standards"""
    
    def __init__(self):
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:122.0) Gecko/20100101 Firefox/122.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2.1 Safari/605.1.15',
        ]
        
        self.headers_templates = [
            {
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
                'Accept-Language': 'en-US,en;q=0.9',
                'Accept-Encoding': 'gzip, deflate, br',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
                'Sec-Fetch-Dest': 'document',
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-Site': 'none',
                'Sec-Fetch-User': '?1',
                'Cache-Control': 'max-age=0'
            }
        ]
    
    def get_random_headers(self) -> Dict[str, str]:
        """Generate randomized headers to avoid detection"""
        headers = random.choice(self.headers_templates).copy()
        headers['User-Agent'] = random.choice(self.user_agents)
        return headers
    
    def get_delay_range(self, base_delay: float = 1.0) -> float:
        """Get randomized delay to mimic human behavior"""
        return random.uniform(base_delay * 0.5, base_delay * 2.0)
    
    async def smart_delay(self, request_count: int, base_delay: float = 1.0):
        """Implement smart delays based on request patterns"""
        if request_count > 100:
            delay = random.uniform(2.0, 5.0)  # Slower for high volume
        elif request_count > 50:
            delay = random.uniform(1.0, 3.0)
        else:
            delay = self.get_delay_range(base_delay)
        
        await asyncio.sleep(delay)
    
    def should_use_headless_browser(self, url: str, complexity_score: int) -> bool:
        """Determine if headless browser is needed based on site complexity"""
        # Check for SPA indicators, JavaScript rendering needs
        spa_indicators = ['react', 'vue', 'angular', 'spa']
        if any(indicator in url.lower() for indicator in spa_indicators):
            return True
        
        return complexity_score > 7  # High complexity sites need browser rendering
