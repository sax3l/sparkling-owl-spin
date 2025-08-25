import itertools, random, time, httpx, asyncio
from typing import Optional, List, Dict, Any

class ProxyPool:
    def __init__(self, proxies: List[str]):
        self._proxies = proxies
        self._iter = itertools.cycle(proxies) if proxies else None
        self._bad: Dict[str, float] = {}  # proxy -> until_ts
        self._healthy_proxies = set(proxies)
        self._stats = {
            'total_proxies': len(proxies),
            'healthy_proxies': len(proxies),
            'unhealthy_proxies': 0,
            'total_requests': 0,
            'failed_requests': 0
        }

    def next(self) -> Optional[str]:
        if not self._iter:
            return None
        for _ in range(len(self._proxies)):
            p = next(self._iter)
            until = self._bad.get(p, 0)
            if time.time() > until:
                self._stats['total_requests'] += 1
                return p
        return None

    def mark_bad(self, proxy: str, ban_seconds: int = 120):
        self._bad[proxy] = time.time() + ban_seconds
        self._healthy_proxies.discard(proxy)
        self._stats['failed_requests'] += 1
        self._stats['healthy_proxies'] = len(self._healthy_proxies)
        self._stats['unhealthy_proxies'] = self._stats['total_proxies'] - self._stats['healthy_proxies']

    def get_stats(self) -> Dict[str, Any]:
        """Get proxy pool statistics"""
        return self._stats.copy()

    async def initialize(self):
        """Initialize proxy pool (placeholder for async setup)"""
        pass

    async def close(self):
        """Close proxy pool (placeholder for cleanup)"""
        pass

    @staticmethod
    def from_env(csv: str) -> "ProxyPool":
        proxies = [p.strip() for p in csv.split(",") if p.strip()]
        return ProxyPool(proxies)
