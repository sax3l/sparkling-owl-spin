#!/usr/bin/env python3
"""
Test för Enhanced Proxy Manager
===============================

Standalone test av den moderna proxy pool managern baserad på jhao104/proxy_pool analysen.
"""

import asyncio
import logging
from datetime import datetime
from dataclasses import dataclass
from enum import Enum
from typing import Optional, Dict, Set

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


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


class SimpleProxyManager:
    """
    Simplified test version of Enhanced Proxy Manager.
    Fokuserar på kärnfunktionalitet från jhao104/proxy_pool.
    """
    
    def __init__(self):
        # In-memory storage (enkel implementation)
        self._proxy_pool: Dict[str, ProxyInfo] = {}
        self._active_proxies: Set[str] = set()
        
        # Configuration
        self.max_pool_size = 100
        
    async def add_proxy(self, proxy_info: ProxyInfo) -> bool:
        """Add proxy to pool (baserat på DbClient.put)."""
        try:
            key = proxy_info.key
            
            if key in self._proxy_pool:
                logger.debug(f"Updating existing proxy: {key}")
            else:
                logger.info(f"➕ Adding new proxy: {key}")
                
            self._proxy_pool[key] = proxy_info
            
            if proxy_info.is_active:
                self._active_proxies.add(key)
                
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to add proxy {proxy_info.key}: {e}")
            return False
            
    async def get_proxy(self, protocol: Optional[str] = None) -> Optional[ProxyInfo]:
        """Get random active proxy (baserat på DbClient.get)."""
        try:
            candidates = [
                proxy for proxy in self._proxy_pool.values()
                if proxy.is_active and (not protocol or proxy.protocol == protocol)
            ]
            
            if not candidates:
                logger.warning("❌ No active proxies available")
                return None
                
            # Välj första för enkelhet (i riktig implementation: random.choice)
            selected = candidates[0]
            logger.info(f"✅ Selected proxy: {selected.key}")
            return selected
            
        except Exception as e:
            logger.error(f"❌ Failed to get proxy: {e}")
            return None
            
    async def validate_proxy(self, proxy_info: ProxyInfo, test_url: str = "http://httpbin.org/ip") -> bool:
        """Validate proxy (förenklad från original)."""
        try:
            # Simulera validation (i riktig implementation: HTTP request)
            logger.info(f"🔄 Validating proxy: {proxy_info.key}")
            
            # Simulera success/failure
            import random
            is_valid = random.choice([True, False])
            
            if is_valid:
                proxy_info.status = ProxyStatus.ACTIVE
                proxy_info.last_checked = datetime.now()
                proxy_info.success_rate = 0.8
                proxy_info.response_time = 1.5
                
                self._active_proxies.add(proxy_info.key)
                logger.info(f"✅ Proxy {proxy_info.key} is valid")
                return True
            else:
                proxy_info.status = ProxyStatus.INACTIVE
                proxy_info.last_checked = datetime.now()
                proxy_info.success_rate = 0.1
                
                self._active_proxies.discard(proxy_info.key)
                logger.warning(f"❌ Proxy {proxy_info.key} is invalid")
                return False
                
        except Exception as e:
            logger.error(f"❌ Validation error for {proxy_info.key}: {e}")
            return False
            
    async def validate_all_proxies(self):
        """Validate all proxies (baserat på batch validation)."""
        logger.info(f"🔄 Starting validation of {len(self._proxy_pool)} proxies...")
        
        for proxy in self._proxy_pool.values():
            await self.validate_proxy(proxy)
            
        active_count = len(self._active_proxies)
        total_count = len(self._proxy_pool)
        success_rate = (active_count / total_count) * 100 if total_count > 0 else 0
        
        logger.info(f"✅ Validation complete: {active_count}/{total_count} active ({success_rate:.1f}%)")
        
    async def get_stats(self) -> Dict[str, any]:
        """Get pool statistics."""
        active_proxies = [p for p in self._proxy_pool.values() if p.is_active]
        
        return {
            "total_proxies": len(self._proxy_pool),
            "active_proxies": len(active_proxies),
            "inactive_proxies": len(self._proxy_pool) - len(active_proxies),
            "success_rate": sum(p.success_rate for p in active_proxies) / len(active_proxies) if active_proxies else 0.0,
            "protocols": list(set(p.protocol for p in self._proxy_pool.values())),
        }


async def test_proxy_manager():
    """Test av proxy manager funktionalitet."""
    print("🚀 TESTING ENHANCED PROXY MANAGER")
    print("=" * 50)
    
    # Skapa manager
    manager = SimpleProxyManager()
    
    # Skapa test proxies (baserat på proxy_pool patterns)
    test_proxies = [
        ProxyInfo("127.0.0.1", 8080, "http", source="manual"),
        ProxyInfo("127.0.0.1", 3128, "http", source="manual"),
        ProxyInfo("192.168.1.100", 8080, "https", source="fetcher"),
        ProxyInfo("10.0.0.1", 3128, "http", source="api"),
        ProxyInfo("172.16.0.1", 8888, "http", source="scraper"),
    ]
    
    print(f"➕ Adding {len(test_proxies)} test proxies...")
    
    # Lägg till proxies
    for proxy in test_proxies:
        success = await manager.add_proxy(proxy)
        if success:
            print(f"   ✅ Added: {proxy.key}")
        else:
            print(f"   ❌ Failed: {proxy.key}")
            
    print()
    
    # Validera alla proxies
    print("🔄 Validating all proxies...")
    await manager.validate_all_proxies()
    print()
    
    # Testa att hämta proxy
    print("🎯 Testing proxy retrieval...")
    proxy = await manager.get_proxy()
    if proxy:
        print(f"   ✅ Got proxy: {proxy.url} (status: {proxy.status.value})")
    else:
        print("   ❌ No proxy available")
    print()
    
    # Visa statistik
    print("📊 Pool Statistics:")
    stats = await manager.get_stats()
    for key, value in stats.items():
        print(f"   {key}: {value}")
    print()
    
    # Testa protokoll-specifik hämtning
    print("🔍 Testing protocol-specific retrieval...")
    http_proxy = await manager.get_proxy("http")
    if http_proxy:
        print(f"   ✅ HTTP proxy: {http_proxy.url}")
    
    https_proxy = await manager.get_proxy("https")
    if https_proxy:
        print(f"   ✅ HTTPS proxy: {https_proxy.url}")
    elif not https_proxy:
        print(f"   ⚠️  No HTTPS proxy available")
    print()
    
    print("✅ ENHANCED PROXY MANAGER TEST COMPLETED!")
    print()
    print("🎯 IMPLEMENTATION SUCCESS!")
    print("   • Kärnfunktionalitet från jhao104/proxy_pool implementerad")
    print("   • Async/await support tillagt")
    print("   • Memory-based storage fungerar")
    print("   • Proxy validation simulerad")
    print("   • Statistics och reporting")
    print()
    print("📋 NÄSTA STEG:")
    print("   1. Lägg till riktig HTTP validation")
    print("   2. Integrera med advanced_fetchers.py")
    print("   3. Anslut till Redis när kompatibilitet lösts")
    print("   4. Skapa API endpoints")
    print("   5. Fullständig integration med befintligt system")


if __name__ == "__main__":
    asyncio.run(test_proxy_manager())
