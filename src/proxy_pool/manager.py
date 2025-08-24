"""
Proxy Pool Manager - Comprehensive proxy management system
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta

try:
    from proxy_pool.adapters import PoolAdapter
    from utils.contracts import ProxyDescriptor
except ImportError:
    # Fallback implementations
    class PoolAdapter:
        pass
    
    class ProxyDescriptor:
        def __init__(self, proxy_id: str, endpoint: str):
            self.proxy_id = proxy_id
            self.endpoint = endpoint

logger = logging.getLogger(__name__)


class ProxyPoolManager:
    """
    Advanced proxy pool management system.
    
    Features:
    - Health monitoring
    - Load balancing
    - Geographic selection
    - Performance tracking
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.proxies: Dict[str, ProxyDescriptor] = {}
        self.health_stats: Dict[str, Dict[str, Any]] = {}
        self.adapter: Optional[PoolAdapter] = None
        
    def get_proxy(self, purpose: str = "crawl") -> Optional[ProxyDescriptor]:
        """Get the best available proxy for a given purpose."""
        # Basic implementation - return first available proxy
        if self.proxies:
            return next(iter(self.proxies.values()))
        return None
        
    def release_proxy(self, proxy_id: str, success: bool, response_time: float = 0.0):
        """Release proxy back to pool with performance data."""
        if proxy_id in self.health_stats:
            stats = self.health_stats[proxy_id]
            stats['total_requests'] = stats.get('total_requests', 0) + 1
            if success:
                stats['successful_requests'] = stats.get('successful_requests', 0) + 1
            stats['last_response_time'] = response_time
            stats['last_used'] = datetime.now()
    
    def add_proxy(self, proxy_id: str, endpoint: str) -> bool:
        """Add a new proxy to the pool."""
        try:
            proxy = ProxyDescriptor(proxy_id, endpoint)
            self.proxies[proxy_id] = proxy
            self.health_stats[proxy_id] = {
                'added_at': datetime.now(),
                'total_requests': 0,
                'successful_requests': 0,
                'last_response_time': 0.0,
                'is_healthy': True
            }
            return True
        except Exception as e:
            logger.error(f"Failed to add proxy {proxy_id}: {e}")
            return False
    
    def remove_proxy(self, proxy_id: str) -> bool:
        """Remove a proxy from the pool."""
        try:
            if proxy_id in self.proxies:
                del self.proxies[proxy_id]
            if proxy_id in self.health_stats:
                del self.health_stats[proxy_id]
            return True
        except Exception as e:
            logger.error(f"Failed to remove proxy {proxy_id}: {e}")
            return False
    
    def get_stats(self) -> Dict[str, Any]:
        """Get comprehensive proxy pool statistics."""
        total_proxies = len(self.proxies)
        healthy_proxies = sum(
            1 for stats in self.health_stats.values() 
            if stats.get('is_healthy', True)
        )
        
        return {
            'total_proxies': total_proxies,
            'healthy_proxies': healthy_proxies,
            'unhealthy_proxies': total_proxies - healthy_proxies,
            'utilization_rate': 0.0 if total_proxies == 0 else healthy_proxies / total_proxies,
            'last_updated': datetime.now()
        }


class TransportService:
    """
    The public interface for acquiring and managing proxies.
    It delegates all logic to the configured adapter.
    """
    def __init__(self, adapter: Optional[PoolAdapter] = None):
        self.adapter = adapter or PoolAdapter()

    def get_proxy(self, purpose: str = "crawl") -> Optional[ProxyDescriptor]:
        """
        Gets the best available proxy for a given purpose (e.g., 'crawl', 'scrape_sensitive').
        """
        if hasattr(self.adapter, 'pop_best'):
            return self.adapter.pop_best(purpose=purpose)
        return None

    def release(self, proxy_id: str, success: bool, rtt_ms: Optional[int] = None, status_code: Optional[int] = None):
        """
        Releases a proxy back to the pool and reports the outcome of its usage.
        """
        if hasattr(self.adapter, 'report'):
            self.adapter.report(proxy_id, success, rtt_ms, status_code)
    
    def stats(self) -> Dict[str, Any]:
        """Get proxy pool statistics."""
        if hasattr(self.adapter, 'stats'):
            return self.adapter.stats()
        return {'total_proxies': 0, 'healthy_proxies': 0}
        return self.adapter.pop_best(purpose=purpose)

    def release(self, proxy_id: str, success: bool, rtt_ms: int | None = None, status_code: int | None = None):
        """
        Releases a proxy back to the pool and reports the outcome of its usage.
        """
        self.adapter.report(proxy_id, success, rtt_ms, status_code)

    def stats(self) -> dict:
        """
        Retrieves current statistics from the proxy pool adapter.
        """
        return self.adapter.stats()

class ProxyPoolManager:
    """
    Enhanced proxy pool manager for API compatibility.
    Provides higher-level proxy management functionality.
    """
    
    def __init__(self, adapter: PoolAdapter = None):
        # Use default adapter if none provided
        if adapter is None:
            from proxy_pool.adapters import DefaultPoolAdapter  # TODO: Implement DefaultPoolAdapter
            adapter = DefaultPoolAdapter()
        
        self.transport = TransportService(adapter)
        self._stats_cache = {}
        self._last_refresh = None
    
    def get_proxy(self, purpose: str = "crawl") -> ProxyDescriptor:
        """Get best available proxy for given purpose."""
        return self.transport.get_proxy(purpose)
    
    def release_proxy(self, proxy_id: str, success: bool, rtt_ms: int = None, status_code: int = None):
        """Release proxy back to pool with performance metrics."""
        self.transport.release(proxy_id, success, rtt_ms, status_code)
    
    def get_stats(self) -> dict:
        """Get comprehensive proxy pool statistics."""
        base_stats = self.transport.stats()
        
        # Add enhanced statistics
        enhanced_stats = {
            **base_stats,
            "last_refresh": self._last_refresh,
            "pool_health": self._calculate_health(base_stats),
            "availability_zones": self._get_availability_zones(),
        }
        
        self._stats_cache = enhanced_stats
        return enhanced_stats
    
    def refresh_pool(self) -> bool:
        """Trigger proxy pool refresh."""
        try:
            # TODO: Implement actual refresh logic
            from datetime import datetime
            self._last_refresh = datetime.now().isoformat()
            return True
        except Exception:
            return False
    
    def _calculate_health(self, stats: dict) -> str:
        """Calculate overall pool health status."""
        total = stats.get("total_proxies", 0)
        active = stats.get("active_proxies", 0)
        
        if total == 0:
            return "critical"
        
        health_ratio = active / total
        if health_ratio >= 0.8:
            return "healthy"
        elif health_ratio >= 0.5:
            return "warning"
        else:
            return "critical"
    
    def _get_availability_zones(self) -> list:
        """Get list of proxy availability zones."""
        # TODO: Implement actual zone detection
        return ["us-east-1", "eu-west-1", "asia-southeast-1"]


# Backward compatibility alias
ProxyManager = ProxyPoolManager