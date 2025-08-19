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