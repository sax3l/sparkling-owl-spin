import pytest

# Placeholder for ProxyManager
class ProxyManager:
    def __init__(self, redis_client): self.proxies = []
    async def add_proxy(self, addr, quality): self.proxies.append({'addr': addr, 'quality': quality})
    async def get_proxy(self): return max(self.proxies, key=lambda p: p['quality']) if self.proxies else None
    async def report_success(self, proxy): pass

@pytest.mark.integration
@pytest.mark.asyncio
async def test_proxy_rotation(redis_client):
    pm = ProxyManager(redis_client=redis_client)
    await pm.add_proxy("1.1.1.1:8080", quality=0.9)
    await pm.add_proxy("2.2.2.2:8080", quality=0.5)
    p = await pm.get_proxy()
    assert p['addr'] == "1.1.1.1:8080"
    await pm.report_success(p)