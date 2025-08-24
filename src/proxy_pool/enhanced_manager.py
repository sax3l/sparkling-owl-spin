"""
Enhanced Proxy Pool Manager
===========================

Moderniserad async version av jhao104/proxy_pool arkitekturen.
Baserat på analys av DbClient och ProxyHandler klasser.

Key improvements:
- Async/await support 
- Better error handling
- Metrics integration
- Modern Python patterns
"""

import asyncio
import random
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Set
from dataclasses import dataclass, asdict
from enum import Enum

# Try to import aioredis, fallback gracefully
try:
    # import aioredis  # Disabled due to Python 3.13 compatibility issues
    AIOREDIS_AVAILABLE = False
    aioredis = None
except ImportError:
    AIOREDIS_AVAILABLE = False
    aioredis = None

# Mock imports for standalone testing
try:
    from utils.logger import get_logger
    from observability.metrics import MetricsCollector
except ImportError:
    import logging
    def get_logger(name): return logging.getLogger(name)
    
    class MetricsCollector:
        def counter(self, name, value): pass
        def timer(self, name, value): pass

logger = get_logger(__name__)


class ProxyStatus(Enum):
    """Proxy status states."""
    UNKNOWN = "unknown"
    ACTIVE = "active"
    INACTIVE = "inactive"
    TESTING = "testing"
    BLOCKED = "blocked"


@dataclass
class ProxyInfo:
    """Enhanced proxy information."""
    host: str
    port: int
    protocol: str = "http"
    username: Optional[str] = None
    password: Optional[str] = None
    status: ProxyStatus = ProxyStatus.UNKNOWN
    last_checked: Optional[datetime] = None
    success_rate: float = 0.0
    response_time: float = 0.0
    source: str = "unknown"
    country: Optional[str] = None
    anonymity: Optional[str] = None
    
    @property
    def url(self) -> str:
        """Get proxy URL."""
        if self.username and self.password:
            return f"{self.protocol}://{self.username}:{self.password}@{self.host}:{self.port}"
        return f"{self.protocol}://{self.host}:{self.port}"
    
    @property
    def is_active(self) -> bool:
        """Check if proxy is active."""
        return self.status == ProxyStatus.ACTIVE
        
    @property
    def key(self) -> str:
        """Unique key for proxy."""
        return f"{self.host}:{self.port}"


class EnhancedProxyManager:
    """
    Enhanced async proxy pool manager.
    
    Inspired by jhao104/proxy_pool but modernized with:
    - Async/await support
    - Better validation
    - Metrics integration 
    - Memory + Redis storage
    """
    
    def __init__(self, redis_url: Optional[str] = None, metrics: Optional[MetricsCollector] = None):
        self.redis_url = redis_url
        self.metrics = metrics or MetricsCollector()
        self.redis_client = None  # Will be typed properly after connection
        
        # In-memory storage as fallback
        self._proxy_pool: Dict[str, ProxyInfo] = {}
        self._active_proxies: Set[str] = set()
        self._testing_proxies: Set[str] = set()
        
        # Configuration
        self.max_pool_size = 1000
        self.validation_interval = 300  # 5 minutes
        self.max_test_concurrent = 10
        
        # Stats
        self._stats = {
            "total_proxies": 0,
            "active_proxies": 0,
            "tests_completed": 0,
            "success_rate": 0.0
        }
        
    async def initialize(self):
        """Initialize the proxy manager."""
        logger.info("🔄 Initializing Enhanced Proxy Manager...")
        
        # Setup Redis connection if URL provided
        if self.redis_url and AIOREDIS_AVAILABLE:
            try:
                self.redis_client = aioredis.from_url(self.redis_url)
                await self.redis_client.ping()
                logger.info("✅ Connected to Redis")
            except Exception as e:
                logger.warning(f"❌ Redis connection failed: {e}, using memory storage")
                self.redis_client = None
        else:
            if not AIOREDIS_AVAILABLE:
                logger.warning("⚠️  aioredis not available, using memory storage")
            self.redis_client = None
                
        # Load existing proxies
        await self._load_existing_proxies()
        
        logger.info(f"✅ Proxy Manager initialized with {len(self._proxy_pool)} proxies")
        
    async def add_proxy(self, proxy_info: ProxyInfo) -> bool:
        """
        Add proxy to pool.
        Equivalent to DbClient.put() from original.
        """
        try:
            key = proxy_info.key
            
            # Check if already exists
            if key in self._proxy_pool:
                logger.debug(f"Proxy {key} already exists, updating...")
                
            # Add to memory pool
            self._proxy_pool[key] = proxy_info
            
            # Add to Redis if available
            if self.redis_client:
                await self.redis_client.hset(
                    "proxy_pool", 
                    key, 
                    str(asdict(proxy_info))
                )
                
            # Update stats
            self._update_stats()
            
            logger.debug(f"➕ Added proxy: {key}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to add proxy {proxy_info.key}: {e}")
            return False
            
    async def get_proxy(self, protocol: Optional[str] = None, country: Optional[str] = None) -> Optional[ProxyInfo]:
        """
        Get random active proxy.
        Equivalent to DbClient.get() from original.
        """
        try:
            # Filter active proxies
            candidates = [
                proxy for proxy in self._proxy_pool.values()
                if proxy.is_active and (not protocol or proxy.protocol == protocol)
                and (not country or proxy.country == country)
            ]
            
            if not candidates:
                logger.warning("❌ No active proxies available")
                return None
                
            # Select based on success rate (weighted random)
            weights = [max(proxy.success_rate, 0.1) for proxy in candidates]
            selected = random.choices(candidates, weights=weights)[0]
            
            # Update metrics
            self.metrics.counter("proxy_requests", 1)
            
            logger.debug(f"✅ Selected proxy: {selected.key} (success_rate: {selected.success_rate:.2f})")
            return selected
            
        except Exception as e:
            logger.error(f"❌ Failed to get proxy: {e}")
            return None
            
    async def remove_proxy(self, proxy_key: str) -> bool:
        """Remove proxy from pool."""
        try:
            # Remove from memory
            if proxy_key in self._proxy_pool:
                del self._proxy_pool[proxy_key]
                
            # Remove from sets
            self._active_proxies.discard(proxy_key)
            self._testing_proxies.discard(proxy_key)
            
            # Remove from Redis
            if self.redis_client:
                await self.redis_client.hdel("proxy_pool", proxy_key)
                
            # Update stats  
            self._update_stats()
            
            logger.debug(f"➖ Removed proxy: {proxy_key}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to remove proxy {proxy_key}: {e}")
            return False
            
    async def validate_proxy(self, proxy_info: ProxyInfo, test_url: str = "http://httpbin.org/ip") -> bool:
        """
        Validate proxy by making test request.
        Enhanced version of original validation logic.
        """
        import aiohttp
        import time
        
        try:
            start_time = time.time()
            
            proxy_url = proxy_info.url
            timeout = aiohttp.ClientTimeout(total=10)
            
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.get(test_url, proxy=proxy_url) as response:
                    response_time = time.time() - start_time
                    
                    if response.status == 200:
                        # Update proxy stats
                        proxy_info.status = ProxyStatus.ACTIVE
                        proxy_info.last_checked = datetime.now()
                        proxy_info.response_time = response_time
                        
                        # Calculate success rate (simple moving average)
                        old_rate = proxy_info.success_rate
                        proxy_info.success_rate = (old_rate * 0.8) + (1.0 * 0.2)
                        
                        # Add to active set
                        self._active_proxies.add(proxy_info.key)
                        
                        logger.debug(f"✅ Proxy {proxy_info.key} validated in {response_time:.2f}s")
                        return True
                        
        except Exception as e:
            logger.debug(f"❌ Proxy {proxy_info.key} validation failed: {e}")
            
        # Mark as inactive on failure
        proxy_info.status = ProxyStatus.INACTIVE
        proxy_info.last_checked = datetime.now()
        
        # Update success rate
        old_rate = proxy_info.success_rate
        proxy_info.success_rate = (old_rate * 0.8) + (0.0 * 0.2)
        
        # Remove from active set
        self._active_proxies.discard(proxy_info.key)
        
        return False
        
    async def validate_all_proxies(self):
        """
        Validate all proxies in pool.
        Enhanced version of original batch validation.
        """
        logger.info(f"🔄 Starting validation of {len(self._proxy_pool)} proxies...")
        
        # Create semaphore to limit concurrent tests
        semaphore = asyncio.Semaphore(self.max_test_concurrent)
        
        async def validate_with_semaphore(proxy_info):
            async with semaphore:
                await self.validate_proxy(proxy_info)
                
        # Run validations concurrently
        tasks = [validate_with_semaphore(proxy) for proxy in self._proxy_pool.values()]
        await asyncio.gather(*tasks, return_exceptions=True)
        
        # Update stats
        self._update_stats()
        
        active_count = len(self._active_proxies)
        total_count = len(self._proxy_pool)
        success_rate = (active_count / total_count) * 100 if total_count > 0 else 0
        
        logger.info(f"✅ Validation complete: {active_count}/{total_count} active ({success_rate:.1f}%)")
        
    async def cleanup_inactive_proxies(self, max_inactive_hours: int = 24):
        """Remove old inactive proxies."""
        cutoff_time = datetime.now() - timedelta(hours=max_inactive_hours)
        
        to_remove = []
        for key, proxy in self._proxy_pool.items():
            if (proxy.status == ProxyStatus.INACTIVE and 
                proxy.last_checked and 
                proxy.last_checked < cutoff_time):
                to_remove.append(key)
                
        for key in to_remove:
            await self.remove_proxy(key)
            
        if to_remove:
            logger.info(f"🧹 Cleaned up {len(to_remove)} inactive proxies")
            
    async def get_stats(self) -> Dict[str, any]:
        """Get pool statistics."""
        active_proxies = [p for p in self._proxy_pool.values() if p.is_active]
        
        avg_response_time = 0.0
        if active_proxies:
            avg_response_time = sum(p.response_time for p in active_proxies) / len(active_proxies)
            
        return {
            "total_proxies": len(self._proxy_pool),
            "active_proxies": len(active_proxies),
            "inactive_proxies": len(self._proxy_pool) - len(active_proxies),
            "average_response_time": avg_response_time,
            "success_rate": sum(p.success_rate for p in active_proxies) / len(active_proxies) if active_proxies else 0.0,
            "protocols": list(set(p.protocol for p in self._proxy_pool.values())),
            "countries": list(set(p.country for p in self._proxy_pool.values() if p.country))
        }
        
    async def _load_existing_proxies(self):
        """Load existing proxies from Redis."""
        if not self.redis_client:
            return
            
        try:
            proxy_data = await self.redis_client.hgetall("proxy_pool")
            for key, data in proxy_data.items():
                # Parse stored proxy data (simplified)
                # In real implementation, properly deserialize JSON
                pass
                
        except Exception as e:
            logger.warning(f"❌ Failed to load existing proxies: {e}")
            
    def _update_stats(self):
        """Update internal statistics."""
        active_count = len([p for p in self._proxy_pool.values() if p.is_active])
        
        self._stats.update({
            "total_proxies": len(self._proxy_pool),
            "active_proxies": active_count,
            "success_rate": (active_count / len(self._proxy_pool)) * 100 if self._proxy_pool else 0.0
        })
        
        # Send metrics
        self.metrics.counter("proxy_pool_total", len(self._proxy_pool))
        self.metrics.counter("proxy_pool_active", active_count)
        

# Helper functions for easy integration
async def create_proxy_manager(redis_url: Optional[str] = None) -> EnhancedProxyManager:
    """Factory function to create and initialize proxy manager."""
    manager = EnhancedProxyManager(redis_url=redis_url)
    await manager.initialize()
    return manager


# Usage example
async def example_usage():
    """Example of how to use the Enhanced Proxy Manager."""
    
    # Create manager
    manager = await create_proxy_manager()
    
    # Add some test proxies
    test_proxies = [
        ProxyInfo("127.0.0.1", 8080, "http", source="manual"),
        ProxyInfo("127.0.0.1", 3128, "http", source="manual"),
    ]
    
    for proxy in test_proxies:
        await manager.add_proxy(proxy)
        
    # Validate all proxies
    await manager.validate_all_proxies()
    
    # Get a proxy for use
    proxy = await manager.get_proxy()
    if proxy:
        print(f"✅ Got proxy: {proxy.url}")
        
    # Get statistics
    stats = await manager.get_stats()
    print(f"📊 Pool stats: {stats}")


if __name__ == "__main__":
    asyncio.run(example_usage())
