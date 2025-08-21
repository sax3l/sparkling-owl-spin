"""
Integrationstester för proxy_manager - Proxypool-hantering och kvalitetskontroll

För nybörjare: Integrationstester testar hur flera komponenter fungerar tillsammans.
Här testar vi hur proxy-managern samverkar med Redis och kvalitetsmätningar.

GitHub Copilot tips: Använd async fixtures för asynkrona komponenter.
"""

import pytest

# Placeholder for ProxyManager (kommer implementeras)
class ProxyManager:
    def __init__(self, redis_client=None):
        self.redis = redis_client
        self.proxies = []
    
    async def add_proxy(self, addr: str, quality: float = 0.5, **kwargs):
        proxy = {'addr': addr, 'quality': quality, 'successes': 0, 'failures': 0}
        self.proxies.append(proxy)
        if self.redis:
            await self.redis.set(f"proxy:{addr}", str(quality))
    
    async def get_proxy(self):
        if not self.proxies:
            return None
        return max(self.proxies, key=lambda p: p['quality'])
    
    async def report_success(self, proxy):
        if proxy:
            proxy['successes'] += 1
            proxy['quality'] = min(1.0, proxy['quality'] + 0.01)
            if self.redis:
                await self.redis.set(f"proxy:{proxy['addr']}", str(proxy['quality']))
    
    async def report_failure(self, proxy):
        if proxy:
            proxy['failures'] += 1
            proxy['quality'] = max(0.0, proxy['quality'] - 0.1)
            if self.redis:
                await self.redis.set(f"proxy:{proxy['addr']}", str(proxy['quality']))
    
    async def get_stats(self):
        if not self.proxies:
            return {"total_proxies": 0, "avg_quality": 0, "best_quality": 0}
        
        qualities = [p['quality'] for p in self.proxies]
        return {
            "total_proxies": len(self.proxies),
            "avg_quality": sum(qualities) / len(qualities),
            "best_quality": max(qualities)
        }

@pytest.mark.integration
@pytest.mark.asyncio
async def test_proxy_rotation(redis_client):
    """Test grundläggande proxy-rotation"""
    pm = ProxyManager(redis_client=redis_client)
    await pm.add_proxy("1.1.1.1:8080", quality=0.9)
    await pm.add_proxy("2.2.2.2:8080", quality=0.5)
    p = await pm.get_proxy()
    assert p['addr'] == "1.1.1.1:8080"  # Högsta kvalitet
    await pm.report_success(p)

@pytest.mark.integration
@pytest.mark.asyncio
async def test_proxy_quality_updates(redis_client):
    """Test kvalitetsuppdateringar"""
    pm = ProxyManager(redis_client=redis_client)
    await pm.add_proxy("1.1.1.1:8080", quality=0.5)
    
    proxy = await pm.get_proxy()
    original_quality = proxy['quality']
    
    # Test framgång
    await pm.report_success(proxy)
    assert proxy['quality'] > original_quality
    
    # Test misslyckande
    await pm.report_failure(proxy)
    assert proxy['quality'] < original_quality

@pytest.mark.integration
@pytest.mark.asyncio
async def test_proxy_stats(redis_client):
    """Test statistik-generering"""
    pm = ProxyManager(redis_client=redis_client)
    
    await pm.add_proxy("1.1.1.1:8080", quality=0.9)
    await pm.add_proxy("2.2.2.2:8080", quality=0.5)
    await pm.add_proxy("3.3.3.3:8080", quality=0.7)
    
    stats = await pm.get_stats()
    assert stats["total_proxies"] == 3
    assert 0.5 < stats["avg_quality"] < 0.9
    assert stats["best_quality"] == 0.9

@pytest.mark.integration
@pytest.mark.asyncio
async def test_redis_integration(redis_client):
    """Test Redis-integration"""
    pm = ProxyManager(redis_client=redis_client)
    
    await pm.add_proxy("1.1.1.1:8080", quality=0.8)
    redis_value = await redis_client.get("proxy:1.1.1.1:8080")
    assert redis_value == "0.8"
    
    proxy = await pm.get_proxy()
    await pm.report_success(proxy)
    
    updated_value = await redis_client.get("proxy:1.1.1.1:8080")
    assert float(updated_value) > 0.8

@pytest.mark.integration
@pytest.mark.asyncio
async def test_empty_proxy_pool(redis_client):
    """Test tom proxy-pool"""
    pm = ProxyManager(redis_client=redis_client)
    
    proxy = await pm.get_proxy()
    assert proxy is None
    
    stats = await pm.get_stats()
    assert stats["total_proxies"] == 0