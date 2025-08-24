import asyncio, time
from collections import defaultdict
from urllib.parse import urlparse

class HostPoliteness:
    def __init__(self, default_delay_ms: int = 1000):
        self._last: dict[str, float] = defaultdict(lambda: 0.0)
        self._lock = asyncio.Lock()
        self.delay = default_delay_ms / 1000.0

    async def wait_for_host(self, url: str):
        host = urlparse(url).netloc
        async with self._lock:
            now = time.monotonic()
            delta = now - self._last[host]
            if delta < self.delay:
                await asyncio.sleep(self.delay - delta)
            self._last[host] = time.monotonic()

# Alias for compatibility
PolitenessManager = HostPoliteness
