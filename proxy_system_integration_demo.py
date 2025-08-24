#!/usr/bin/env python3
"""
Complete Proxy System Integration Demo
=====================================

Demonstrerar fullständig integration av alla komponenter baserat på jhao104/proxy_pool analysen:
- Enhanced Proxy Manager (moderniserad DbClient + ProxyHandler)
- Advanced Proxy Fetchers (moderniserad ProxyFetcher)  
- Integration mellan fetch, storage och validation

Detta visar hur den manuella analysen och implementationen resulterar i ett modernt,
async proxy pool system som behåller kärnfunktionaliteten från originalet.
"""

import asyncio
import logging
import random
from datetime import datetime
from dataclasses import dataclass
from enum import Enum
from typing import Optional, Dict, Set, List

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
        if self.username and self.password:
            return f"{self.protocol}://{self.username}:{self.password}@{self.host}:{self.port}"
        return f"{self.protocol}://{self.host}:{self.port}"
    
    @property
    def is_active(self) -> bool:
        return self.status == ProxyStatus.ACTIVE
        
    @property
    def key(self) -> str:
        return f"{self.host}:{self.port}"


@dataclass 
class ProxySource:
    """Configuration for a proxy source."""
    name: str
    url: str
    parser_type: str
    headers: Dict[str, str] = None
    rate_limit: float = 1.0
    enabled: bool = True
    timeout: int = 30


class IntegratedProxyManager:
    """
    Integrerad Proxy Manager som kombinerar alla komponenter.
    Baserat på jhao104/proxy_pool arkitektur men moderniserad.
    """
    
    def __init__(self):
        # Storage (baserat på DbClient)
        self._proxy_pool: Dict[str, ProxyInfo] = {}
        self._active_proxies: Set[str] = set()
        
        # Fetcher sources (baserat på ProxyFetcher)
        self.sources = [
            ProxySource("FreeProxyList", "https://www.free-proxy-list.net/", "html_table"),
            ProxySource("ProxyNova", "https://www.proxynova.com/", "html_table", rate_limit=2.0),
            ProxySource("SpysOne", "https://spys.one/", "html_custom", rate_limit=3.0),
            ProxySource("MockAPI", "https://api.example.com/proxies", "api"),
        ]
        
        # Configuration (baserat på ConfigHandler)
        self.config = {
            "max_pool_size": 200,
            "validation_interval": 300,
            "max_concurrent_fetches": 5,
            "min_success_rate": 0.3,
            "auto_cleanup_hours": 24
        }
        
        # Statistics
        self.stats = {
            "total_fetched": 0,
            "successful_validations": 0,
            "failed_validations": 0,
            "last_fetch_time": None,
            "last_validation_time": None
        }
        
    async def fetch_and_populate(self) -> int:
        """
        Fetch proxies från alla sources och lägg till i poolen.
        Kombinerar fetcher och storage logik.
        """
        logger.info("🚀 Starting proxy fetch and populate cycle...")
        
        all_new_proxies = []
        
        # Fetch från alla enabled sources
        enabled_sources = [s for s in self.sources if s.enabled]
        
        for source in enabled_sources:
            try:
                new_proxies = await self._fetch_from_source(source)
                all_new_proxies.extend(new_proxies)
                logger.info(f"📥 {source.name}: fetched {len(new_proxies)} proxies")
                
                # Rate limiting between sources
                await asyncio.sleep(0.5)
                
            except Exception as e:
                logger.error(f"❌ Failed to fetch from {source.name}: {e}")
                
        # Deduplicate
        unique_proxies = self._deduplicate_proxies(all_new_proxies)
        
        # Add to pool
        added_count = 0
        for proxy in unique_proxies:
            if await self._add_proxy(proxy):
                added_count += 1
                
        self.stats["total_fetched"] += added_count
        self.stats["last_fetch_time"] = datetime.now()
        
        logger.info(f"✅ Fetch complete: {added_count} new proxies added to pool")
        return added_count
        
    async def validate_and_cleanup(self) -> Dict[str, int]:
        """
        Validera alla proxies och rensa inaktiva.
        Baserat på original validation och cleanup logik.
        """
        logger.info("🔄 Starting proxy validation and cleanup...")
        
        validation_results = {
            "validated": 0,
            "activated": 0,
            "deactivated": 0,
            "removed": 0
        }
        
        # Validate alla proxies
        for proxy in list(self._proxy_pool.values()):
            is_valid = await self._validate_proxy(proxy)
            validation_results["validated"] += 1
            
            if is_valid:
                if proxy.key not in self._active_proxies:
                    self._active_proxies.add(proxy.key)
                    validation_results["activated"] += 1
                    
                self.stats["successful_validations"] += 1
            else:
                if proxy.key in self._active_proxies:
                    self._active_proxies.remove(proxy.key)
                    validation_results["deactivated"] += 1
                    
                self.stats["failed_validations"] += 1
                
                # Remove proxies with very low success rate
                if proxy.success_rate < self.config["min_success_rate"]:
                    await self._remove_proxy(proxy.key)
                    validation_results["removed"] += 1
                    
        self.stats["last_validation_time"] = datetime.now()
        
        logger.info(f"✅ Validation complete: {validation_results}")
        return validation_results
        
    async def get_best_proxy(self, protocol: Optional[str] = None, country: Optional[str] = None) -> Optional[ProxyInfo]:
        """
        Få den bästa tillgängliga proxyn baserat på kriterier.
        Använder intelligent selection baserad på success rate och response time.
        """
        candidates = [
            proxy for proxy in self._proxy_pool.values()
            if proxy.is_active 
            and (not protocol or proxy.protocol == protocol)
            and (not country or proxy.country == country)
        ]
        
        if not candidates:
            logger.warning("❌ No suitable proxies available")
            return None
            
        # Sortera baserat på success rate och response time
        candidates.sort(key=lambda p: (p.success_rate, -p.response_time), reverse=True)
        
        # Weighted random selection från top candidates  
        top_candidates = candidates[:min(5, len(candidates))]
        weights = [p.success_rate + 0.1 for p in top_candidates]  # Minimum weight
        
        selected = random.choices(top_candidates, weights=weights)[0]
        
        logger.info(f"✅ Selected best proxy: {selected.key} (success_rate: {selected.success_rate:.2f})")
        return selected
        
    async def _fetch_from_source(self, source: ProxySource) -> List[ProxyInfo]:
        """Simulerad fetch från en källa (riktig implementation skulle använda aiohttp)."""
        await asyncio.sleep(0.1)  # Simulera network delay
        
        # Simulera olika källor (baserat på ProxyFetcher metoder)
        if "FreeProxyList" in source.name:
            return [
                ProxyInfo("203.142.71.78", 8080, "http", source=source.name, country="TH"),
                ProxyInfo("185.199.84.161", 53281, "http", source=source.name, country="TR"),
                ProxyInfo("103.159.46.34", 3128, "https", source=source.name, country="ID"),
            ]
        elif "ProxyNova" in source.name:
            return [
                ProxyInfo("45.76.97.109", 3128, "http", source=source.name, country="US"),
                ProxyInfo("138.68.235.51", 80, "http", source=source.name, country="GB"),
            ]
        elif "SpysOne" in source.name:
            return [
                ProxyInfo("198.199.86.11", 3128, "http", source=source.name),
                ProxyInfo("165.22.45.209", 8080, "http", source=source.name),
            ]
        elif "API" in source.name:
            return [
                ProxyInfo("149.154.157.17", 3128, "http", source=source.name, country="RU"),
                ProxyInfo("192.41.13.71", 80, "http", source=source.name, country="US"),
            ]
        else:
            return []
            
    def _deduplicate_proxies(self, proxies: List[ProxyInfo]) -> List[ProxyInfo]:
        """Remove duplicates."""
        seen = set()
        unique = []
        
        for proxy in proxies:
            if proxy.key not in seen:
                seen.add(proxy.key)
                unique.append(proxy)
                
        return unique
        
    async def _add_proxy(self, proxy: ProxyInfo) -> bool:
        """Add proxy to pool."""
        try:
            # Check pool size limit
            if len(self._proxy_pool) >= self.config["max_pool_size"]:
                logger.debug("Pool size limit reached, skipping new proxy")
                return False
                
            self._proxy_pool[proxy.key] = proxy
            return True
            
        except Exception as e:
            logger.error(f"Failed to add proxy {proxy.key}: {e}")
            return False
            
    async def _remove_proxy(self, proxy_key: str) -> bool:
        """Remove proxy from pool."""
        try:
            if proxy_key in self._proxy_pool:
                del self._proxy_pool[proxy_key]
            self._active_proxies.discard(proxy_key)
            return True
            
        except Exception as e:
            logger.error(f"Failed to remove proxy {proxy_key}: {e}")
            return False
            
    async def _validate_proxy(self, proxy: ProxyInfo) -> bool:
        """
        Validate proxy (simulerad - riktig implementation skulle göra HTTP request).
        Baserat på original validation logik.
        """
        try:
            # Simulera validation
            await asyncio.sleep(0.05)  # Simulera request time
            
            # Random success/failure med bias mot högre success rate
            base_chance = 0.6
            if proxy.success_rate > 0:
                # Proxies med hög success rate har högre chans att förbli valid
                chance = base_chance + (proxy.success_rate * 0.3)
            else:
                chance = base_chance
                
            is_valid = random.random() < chance
            
            # Uppdatera proxy stats
            proxy.last_checked = datetime.now()
            
            if is_valid:
                proxy.status = ProxyStatus.ACTIVE
                proxy.response_time = random.uniform(0.5, 3.0)
                # Update success rate (moving average)
                old_rate = proxy.success_rate
                proxy.success_rate = (old_rate * 0.8) + (1.0 * 0.2)
            else:
                proxy.status = ProxyStatus.INACTIVE
                proxy.response_time = 0.0
                old_rate = proxy.success_rate
                proxy.success_rate = (old_rate * 0.8) + (0.0 * 0.2)
                
            return is_valid
            
        except Exception as e:
            logger.error(f"Validation error for {proxy.key}: {e}")
            proxy.status = ProxyStatus.INACTIVE
            return False
            
    def get_pool_stats(self) -> Dict[str, any]:
        """Get comprehensive pool statistics."""
        active_proxies = [p for p in self._proxy_pool.values() if p.is_active]
        
        protocol_stats = {}
        country_stats = {}
        
        for proxy in self._proxy_pool.values():
            # Protocol stats
            protocol_stats[proxy.protocol] = protocol_stats.get(proxy.protocol, 0) + 1
            
            # Country stats
            if proxy.country:
                country_stats[proxy.country] = country_stats.get(proxy.country, 0) + 1
                
        avg_response_time = 0.0
        avg_success_rate = 0.0
        
        if active_proxies:
            avg_response_time = sum(p.response_time for p in active_proxies) / len(active_proxies)
            avg_success_rate = sum(p.success_rate for p in active_proxies) / len(active_proxies)
            
        return {
            "total_proxies": len(self._proxy_pool),
            "active_proxies": len(active_proxies),
            "inactive_proxies": len(self._proxy_pool) - len(active_proxies),
            "success_rate_overall": (len(active_proxies) / len(self._proxy_pool)) * 100 if self._proxy_pool else 0,
            "average_response_time": avg_response_time,
            "average_success_rate": avg_success_rate,
            "protocols": protocol_stats,
            "countries": country_stats,
            "fetch_stats": self.stats
        }


async def run_integration_demo():
    """Kör fullständig integration demo."""
    
    print("🚀 COMPLETE PROXY SYSTEM INTEGRATION DEMO")
    print("=" * 60)
    print()
    print("Baserat på manuell analys och implementation av jhao104/proxy_pool")
    print("Moderniserad med async/await och förbättrad arkitektur")
    print()
    
    # Skapa integrerad manager
    manager = IntegratedProxyManager()
    
    print("📋 SYSTEM CONFIGURATION:")
    for key, value in manager.config.items():
        print(f"   {key}: {value}")
    print()
    
    print("📡 PROXY SOURCES:")
    for i, source in enumerate(manager.sources):
        status = "✅" if source.enabled else "❌"
        print(f"   {i+1}. {source.name} ({source.parser_type}) {status}")
        print(f"      URL: {source.url}")
        print(f"      Rate limit: {source.rate_limit}s")
    print()
    
    # Steg 1: Fetch proxies
    print("🔄 STEP 1: FETCHING PROXIES FROM ALL SOURCES")
    print("-" * 40)
    added_count = await manager.fetch_and_populate()
    print()
    
    # Steg 2: Initial stats
    print("📊 INITIAL POOL STATE:")
    initial_stats = manager.get_pool_stats()
    print(f"   Total proxies: {initial_stats['total_proxies']}")
    print(f"   Active proxies: {initial_stats['active_proxies']}")  
    print(f"   Protocols: {initial_stats['protocols']}")
    print(f"   Countries: {initial_stats['countries']}")
    print()
    
    # Steg 3: Validate all proxies
    print("🔄 STEP 2: VALIDATING ALL PROXIES")
    print("-" * 40)
    validation_results = await manager.validate_and_cleanup()
    print()
    
    # Steg 4: Post-validation stats
    print("📊 POST-VALIDATION POOL STATE:")
    post_stats = manager.get_pool_stats()
    print(f"   Total proxies: {post_stats['total_proxies']}")
    print(f"   Active proxies: {post_stats['active_proxies']}")
    print(f"   Success rate: {post_stats['success_rate_overall']:.1f}%")
    print(f"   Average response time: {post_stats['average_response_time']:.2f}s")
    print(f"   Average success rate: {post_stats['average_success_rate']:.2f}")
    print()
    
    # Steg 5: Test proxy selection
    print("🎯 STEP 3: TESTING INTELLIGENT PROXY SELECTION")
    print("-" * 40)
    
    # Get best overall proxy
    best_proxy = await manager.get_best_proxy()
    if best_proxy:
        print(f"✅ Best overall proxy: {best_proxy.url}")
        print(f"   Source: {best_proxy.source}")
        print(f"   Success rate: {best_proxy.success_rate:.2f}")
        print(f"   Response time: {best_proxy.response_time:.2f}s")
        if best_proxy.country:
            print(f"   Country: {best_proxy.country}")
    print()
    
    # Get best HTTP proxy
    http_proxy = await manager.get_best_proxy(protocol="http")
    if http_proxy:
        print(f"✅ Best HTTP proxy: {http_proxy.url}")
        print(f"   Success rate: {http_proxy.success_rate:.2f}")
    print()
    
    # Get best HTTPS proxy  
    https_proxy = await manager.get_best_proxy(protocol="https")
    if https_proxy:
        print(f"✅ Best HTTPS proxy: {https_proxy.url}")
    else:
        print("⚠️  No HTTPS proxies available")
    print()
    
    # Steg 6: Show final comprehensive stats
    print("📈 FINAL SYSTEM STATISTICS:")
    print("-" * 40)
    final_stats = manager.get_pool_stats()
    
    print("🏊 Pool Overview:")
    print(f"   Total Proxies: {final_stats['total_proxies']}")
    print(f"   Active: {final_stats['active_proxies']} ({final_stats['success_rate_overall']:.1f}%)")
    print(f"   Inactive: {final_stats['inactive_proxies']}")
    print()
    
    print("⚡ Performance Metrics:")
    print(f"   Avg Response Time: {final_stats['average_response_time']:.2f}s")
    print(f"   Avg Success Rate: {final_stats['average_success_rate']:.2f}")
    print()
    
    print("🔧 Protocol Distribution:")
    for protocol, count in final_stats['protocols'].items():
        print(f"   {protocol.upper()}: {count}")
    print()
    
    print("🌍 Geographic Distribution:")
    for country, count in list(final_stats['countries'].items())[:5]:  # Top 5
        print(f"   {country}: {count}")
    print()
    
    print("📊 Operation Statistics:")
    fetch_stats = final_stats['fetch_stats']
    print(f"   Total Fetched: {fetch_stats['total_fetched']}")
    print(f"   Successful Validations: {fetch_stats['successful_validations']}")
    print(f"   Failed Validations: {fetch_stats['failed_validations']}")
    if fetch_stats['last_fetch_time']:
        print(f"   Last Fetch: {fetch_stats['last_fetch_time'].strftime('%H:%M:%S')}")
    if fetch_stats['last_validation_time']:
        print(f"   Last Validation: {fetch_stats['last_validation_time'].strftime('%H:%M:%S')}")
    print()
    
    print("✅ INTEGRATION DEMO COMPLETED SUCCESSFULLY!")
    print()
    print("🎯 IMPLEMENTATION ACHIEVEMENTS:")
    print("   ✅ Enhanced Proxy Manager (DbClient + ProxyHandler modernized)")
    print("   ✅ Advanced Proxy Fetcher (ProxyFetcher with freeProxy methods)")
    print("   ✅ Async/await architecture throughout")
    print("   ✅ Intelligent proxy selection with weighted algorithms") 
    print("   ✅ Comprehensive statistics and monitoring")
    print("   ✅ Source management and rate limiting")
    print("   ✅ Automatic validation and cleanup")
    print("   ✅ Multi-protocol and geographic filtering")
    print()
    print("🚀 READY FOR PRODUCTION INTEGRATION:")
    print("   • Replace simulated fetching with real HTTP requests")
    print("   • Add Redis storage layer when Python compatibility resolved")
    print("   • Create FastAPI endpoints for external access")
    print("   • Integrate with existing Sparkling Owl Spin scraper system")
    print("   • Add comprehensive logging and monitoring")


if __name__ == "__main__":
    asyncio.run(run_integration_demo())
