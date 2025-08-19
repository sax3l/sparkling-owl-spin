from abc import ABC, abstractmethod
from src.utils.contracts import ProxyDescriptor

class PoolAdapter(ABC):
    """Abstract base class for all proxy pool adapters."""

    @abstractmethod
    def pop_best(self, purpose: str = "crawl") -> ProxyDescriptor:
        """Gets the best available proxy for a given purpose."""
        pass

    @abstractmethod
    def report(self, proxy_id: str, success: bool, rtt_ms: int | None = None, status_code: int | None = None):
        """Reports the outcome of a request to update proxy quality."""
        pass

    @abstractmethod
    def stats(self) -> dict:
        """Returns statistics about the proxy pool."""
        pass