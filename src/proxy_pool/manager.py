from src.proxy_pool.adapters import PoolAdapter
from src.utils.contracts import ProxyDescriptor

class TransportService:
    """
    The public interface for acquiring and managing proxies.
    It delegates all logic to the configured adapter.
    """
    def __init__(self, adapter: PoolAdapter):
        self.adapter = adapter

    def get_proxy(self, purpose: str = "crawl") -> ProxyDescriptor:
        """
        Gets the best available proxy for a given purpose (e.g., 'crawl', 'scrape_sensitive').
        """
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
            from .adapters import DefaultPoolAdapter  # TODO: Implement DefaultPoolAdapter
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