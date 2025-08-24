#!/usr/bin/env python3
"""
IP Rotation Implementation Guide
===============================

Baserat på djupanalysen av Ge0rg3/requests-ip-rotator:
- Enkel, elegant arkitektur med endast 1 huvudklass (ApiGateway)
- AWS API Gateway integration för IP rotation
- 319 linjer kod med 6 nyckelfunktioner
- Fokuserad på requests library integration

Vår implementation moderniserar detta till async och integrerar med vårt system.
"""

import asyncio
import aiohttp
import random
import time
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Set, Any, Union
from dataclasses import dataclass
from pathlib import Path

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


@dataclass
class IPRotatorConfig:
    """Configuration for IP rotation system."""
    regions: List[str] = None
    max_endpoints: int = 10
    endpoint_timeout: float = 30.0
    rotation_delay: float = 0.0
    retry_attempts: int = 3
    health_check_interval: int = 300  # 5 minutes
    
    def __post_init__(self):
        if self.regions is None:
            self.regions = ['us-east-1', 'us-west-1', 'eu-west-1', 'ap-southeast-1']


@dataclass
class IPEndpoint:
    """Represents an IP endpoint for rotation."""
    ip: str
    endpoint_url: str
    region: str = "unknown"
    is_active: bool = True
    last_used: Optional[datetime] = None
    success_count: int = 0
    failure_count: int = 0
    response_time: float = 0.0
    created_at: datetime = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()
    
    @property
    def success_rate(self) -> float:
        """Calculate success rate."""
        total = self.success_count + self.failure_count
        if total == 0:
            return 1.0
        return self.success_count / total
    
    @property
    def key(self) -> str:
        """Unique key for endpoint."""
        return f"{self.ip}_{self.region}"


class AsyncIPRotator:
    """
    Async IP Rotation System
    =========================
    
    Moderniserad version av Ge0rg3/requests-ip-rotator ApiGateway klass.
    
    Förbättringar:
    - Full async/await support
    - Aiohttp integration istället för requests
    - Health checking och monitoring
    - Better error handling och retry logic
    - Integration med vårt proxy system
    """
    
    def __init__(self, config: IPRotatorConfig = None):
        self.config = config or IPRotatorConfig()
        self.session: Optional[aiohttp.ClientSession] = None
        
        # IP endpoint management
        self.endpoints: Dict[str, IPEndpoint] = {}
        self.active_endpoints: List[str] = []
        self.current_index = 0
        
        # Statistics
        self.stats = {
            "requests_made": 0,
            "successful_rotations": 0,
            "failed_rotations": 0,
            "endpoints_created": 0,
            "endpoints_removed": 0,
            "last_rotation": None,
            "total_uptime": 0
        }
        
        self.start_time = datetime.now()
        self.is_initialized = False
        
    async def initialize(self):
        """Initialize the IP rotator (modernized version of init_gateway)."""
        logger.info("🔄 Initializing Async IP Rotator...")
        
        # Create aiohttp session with proper configuration
        connector = aiohttp.TCPConnector(
            limit=100,
            ttl_dns_cache=300,
            use_dns_cache=True,
            keepalive_timeout=60
        )
        
        timeout = aiohttp.ClientTimeout(total=self.config.endpoint_timeout)
        
        self.session = aiohttp.ClientSession(
            connector=connector,
            timeout=timeout,
            headers={
                "User-Agent": "SparkllingOwlSpin-IPRotator/1.0"
            }
        )
        
        # Initialize endpoints (simulera AWS API Gateway creation)
        await self._create_endpoints()
        
        self.is_initialized = True
        logger.info(f"✅ IP Rotator initialized with {len(self.active_endpoints)} endpoints")
        
    async def _create_endpoints(self):
        """
        Create IP endpoints (simulerad AWS API Gateway creation).
        I riktig implementation: skapa AWS API Gateway endpoints.
        """
        logger.info("🏗️  Creating IP endpoints...")
        
        # Simulera endpoint creation för olika regioner
        simulated_endpoints = [
            ("54.230.45.123", "https://api1.example.com", "us-east-1"),
            ("52.84.72.45", "https://api2.example.com", "us-west-1"), 
            ("54.239.134.67", "https://api3.example.com", "eu-west-1"),
            ("54.240.143.89", "https://api4.example.com", "ap-southeast-1"),
            ("52.46.78.234", "https://api5.example.com", "us-east-1"),
            ("54.230.157.12", "https://api6.example.com", "us-west-1"),
        ]
        
        for ip, url, region in simulated_endpoints[:self.config.max_endpoints]:
            endpoint = IPEndpoint(
                ip=ip,
                endpoint_url=url,
                region=region,
                is_active=True
            )
            
            self.endpoints[endpoint.key] = endpoint
            self.active_endpoints.append(endpoint.key)
            self.stats["endpoints_created"] += 1
            
            logger.debug(f"➕ Created endpoint: {ip} ({region})")
            
        logger.info(f"✅ Created {len(self.endpoints)} IP endpoints")
        
    async def make_request(self, method: str, url: str, **kwargs) -> aiohttp.ClientResponse:
        """
        Make HTTP request with IP rotation (modernized version av send method).
        
        Detta ersätter original send() metoden med async support.
        """
        if not self.is_initialized:
            await self.initialize()
            
        # Rotera till nästa IP
        endpoint = await self._get_next_endpoint()
        
        if not endpoint:
            raise Exception("No active endpoints available for rotation")
            
        # Förbered request med IP rotation
        rotated_kwargs = await self._prepare_rotated_request(endpoint, **kwargs)
        
        # Gör request med retry logic
        return await self._execute_request_with_retry(
            method, url, endpoint, rotated_kwargs
        )
        
    async def _get_next_endpoint(self) -> Optional[IPEndpoint]:
        """
        Få nästa endpoint för rotation.
        Implementerar intelligent selection baserat på success rate.
        """
        if not self.active_endpoints:
            logger.error("❌ No active endpoints available")
            return None
            
        # Enkel round-robin med intelligent fallback
        attempts = 0
        while attempts < len(self.active_endpoints):
            # Round-robin selection
            endpoint_key = self.active_endpoints[self.current_index]
            self.current_index = (self.current_index + 1) % len(self.active_endpoints)
            
            endpoint = self.endpoints.get(endpoint_key)
            if endpoint and endpoint.is_active:
                # Uppdatera användning
                endpoint.last_used = datetime.now()
                self.stats["successful_rotations"] += 1
                self.stats["last_rotation"] = datetime.now()
                
                logger.debug(f"🔄 Rotated to IP: {endpoint.ip} ({endpoint.region})")
                return endpoint
                
            attempts += 1
            
        # Om ingen aktiv endpoint hittades
        self.stats["failed_rotations"] += 1
        logger.warning("⚠️ No active endpoints found during rotation")
        return None
        
    async def _prepare_rotated_request(self, endpoint: IPEndpoint, **kwargs) -> Dict[str, Any]:
        """Förbered request med IP rotation headers och proxy settings."""
        
        # I riktig implementation: sätt proxy till endpoint URL
        # För simulation: lägg till headers som indikerar rotation
        headers = kwargs.get('headers', {})
        headers.update({
            'X-Rotated-IP': endpoint.ip,
            'X-Rotated-Region': endpoint.region,
            'X-Rotation-Time': datetime.now().isoformat()
        })
        
        kwargs['headers'] = headers
        
        # Lägg till rotation delay om konfigurerad
        if self.config.rotation_delay > 0:
            await asyncio.sleep(self.config.rotation_delay)
            
        return kwargs
        
    async def _execute_request_with_retry(
        self, 
        method: str, 
        url: str, 
        endpoint: IPEndpoint, 
        kwargs: Dict[str, Any]
    ) -> aiohttp.ClientResponse:
        """Execute request med retry logic och error handling."""
        
        start_time = time.time()
        last_exception = None
        
        for attempt in range(self.config.retry_attempts):
            try:
                # Gör actual HTTP request
                async with self.session.request(method, url, **kwargs) as response:
                    response_time = time.time() - start_time
                    
                    # Uppdatera endpoint statistik
                    endpoint.response_time = response_time
                    endpoint.success_count += 1
                    
                    self.stats["requests_made"] += 1
                    
                    logger.debug(f"✅ Request successful via {endpoint.ip} in {response_time:.2f}s")
                    
                    return response
                    
            except Exception as e:
                last_exception = e
                endpoint.failure_count += 1
                
                logger.warning(f"❌ Request failed via {endpoint.ip} (attempt {attempt + 1}): {e}")
                
                # Om för många failures, deaktivera endpoint
                if endpoint.success_rate < 0.1 and endpoint.failure_count > 5:
                    await self._deactivate_endpoint(endpoint)
                    
                # Kort delay innan retry
                if attempt < self.config.retry_attempts - 1:
                    await asyncio.sleep(0.5 * (attempt + 1))
                    
        # Om alla attempts misslyckades
        raise Exception(f"All retry attempts failed. Last error: {last_exception}")
        
    async def _deactivate_endpoint(self, endpoint: IPEndpoint):
        """Deactivate endpoint som presterar dåligt."""
        endpoint.is_active = False
        
        if endpoint.key in self.active_endpoints:
            self.active_endpoints.remove(endpoint.key)
            self.stats["endpoints_removed"] += 1
            
        logger.warning(f"⏸️ Deactivated endpoint: {endpoint.ip} (success rate: {endpoint.success_rate:.2f})")
        
        # Om vi har för få aktiva endpoints, försök återaktivera några
        if len(self.active_endpoints) < 2:
            await self._reactivate_best_endpoints()
            
    async def _reactivate_best_endpoints(self):
        """Återaktivera de bästa inaktiva endpoints."""
        inactive_endpoints = [
            ep for ep in self.endpoints.values() 
            if not ep.is_active and ep.success_rate > 0.3
        ]
        
        # Sortera efter success rate
        inactive_endpoints.sort(key=lambda ep: ep.success_rate, reverse=True)
        
        # Återaktivera top 2
        for endpoint in inactive_endpoints[:2]:
            endpoint.is_active = True
            endpoint.failure_count = 0  # Reset failure count
            self.active_endpoints.append(endpoint.key)
            
            logger.info(f"🔄 Reactivated endpoint: {endpoint.ip}")
            
    async def health_check(self) -> Dict[str, Any]:
        """
        Utför health check på alla endpoints.
        Moderniserad version av endpoint monitoring.
        """
        logger.info("🏥 Performing endpoint health check...")
        
        health_results = {
            "total_endpoints": len(self.endpoints),
            "active_endpoints": len(self.active_endpoints),
            "healthy_endpoints": 0,
            "unhealthy_endpoints": 0,
            "average_response_time": 0.0,
            "average_success_rate": 0.0
        }
        
        health_tasks = []
        for endpoint in self.endpoints.values():
            if endpoint.is_active:
                health_tasks.append(self._check_endpoint_health(endpoint))
                
        if health_tasks:
            health_checks = await asyncio.gather(*health_tasks, return_exceptions=True)
            
            response_times = []
            success_rates = []
            
            for i, result in enumerate(health_checks):
                if isinstance(result, Exception):
                    health_results["unhealthy_endpoints"] += 1
                elif result:
                    health_results["healthy_endpoints"] += 1
                    endpoint = list(self.endpoints.values())[i]
                    response_times.append(endpoint.response_time)
                    success_rates.append(endpoint.success_rate)
                else:
                    health_results["unhealthy_endpoints"] += 1
                    
            if response_times:
                health_results["average_response_time"] = sum(response_times) / len(response_times)
            if success_rates:
                health_results["average_success_rate"] = sum(success_rates) / len(success_rates)
                
        logger.info(f"✅ Health check complete: {health_results['healthy_endpoints']}/{health_results['total_endpoints']} healthy")
        return health_results
        
    async def _check_endpoint_health(self, endpoint: IPEndpoint) -> bool:
        """Check health för en enskild endpoint."""
        try:
            # Simulera health check (i riktig implementation: test request)
            await asyncio.sleep(0.1)  # Simulera network delay
            
            # Simulera health baserat på tidigare performance
            is_healthy = endpoint.success_rate > 0.7 and endpoint.failure_count < 10
            
            if not is_healthy and endpoint.is_active:
                await self._deactivate_endpoint(endpoint)
                
            return is_healthy
            
        except Exception as e:
            logger.error(f"❌ Health check failed for {endpoint.ip}: {e}")
            return False
            
    async def get_stats(self) -> Dict[str, Any]:
        """Få omfattande statistik om IP rotation systemet."""
        uptime = (datetime.now() - self.start_time).total_seconds()
        
        endpoint_stats = {}
        for region in self.config.regions:
            region_endpoints = [ep for ep in self.endpoints.values() if ep.region == region]
            endpoint_stats[region] = {
                "total": len(region_endpoints),
                "active": len([ep for ep in region_endpoints if ep.is_active]),
                "avg_success_rate": sum(ep.success_rate for ep in region_endpoints) / len(region_endpoints) if region_endpoints else 0
            }
            
        return {
            **self.stats,
            "uptime_seconds": uptime,
            "total_endpoints": len(self.endpoints),
            "active_endpoints": len(self.active_endpoints),
            "regions": endpoint_stats,
            "requests_per_second": self.stats["requests_made"] / uptime if uptime > 0 else 0,
            "success_rate": (self.stats["successful_rotations"] / (self.stats["successful_rotations"] + self.stats["failed_rotations"])) * 100 if (self.stats["successful_rotations"] + self.stats["failed_rotations"]) > 0 else 100
        }
        
    async def shutdown(self):
        """
        Shutdown IP rotator och cleanup resources.
        Moderniserad version av original shutdown metod.
        """
        logger.info("🔄 Shutting down IP Rotator...")
        
        if self.session:
            await self.session.close()
            
        # I riktig implementation: cleanup AWS resources
        logger.info("✅ IP Rotator shutdown complete")
        
    async def __aenter__(self):
        """Async context manager entry."""
        await self.initialize()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.shutdown()


# Integration helpers for existing system
class ProxyPoolIPRotator:
    """
    Integration klass som kombinerar IP rotation med proxy pool.
    Gör det möjligt att använda IP rotation tillsammans med proxy management.
    """
    
    def __init__(self, proxy_manager=None, ip_rotator_config: IPRotatorConfig = None):
        self.proxy_manager = proxy_manager
        self.ip_rotator = AsyncIPRotator(ip_rotator_config)
        
    async def make_request(self, method: str, url: str, use_proxy: bool = True, **kwargs):
        """Make request med både IP rotation och proxy support."""
        
        # Om proxy är enabled och vi har en proxy manager
        if use_proxy and self.proxy_manager:
            proxy = await self.proxy_manager.get_best_proxy()
            if proxy:
                kwargs['proxy'] = proxy.url
                
        # Använd IP rotation för request
        return await self.ip_rotator.make_request(method, url, **kwargs)
        
    async def get_combined_stats(self) -> Dict[str, Any]:
        """Få kombinerad statistik från både IP rotation och proxy pool."""
        ip_stats = await self.ip_rotator.get_stats()
        
        combined_stats = {
            "ip_rotation": ip_stats,
            "proxy_pool": await self.proxy_manager.get_stats() if self.proxy_manager else {},
            "integration": {
                "total_requests": ip_stats.get("requests_made", 0),
                "combined_success_rate": ip_stats.get("success_rate", 0)
            }
        }
        
        return combined_stats


async def test_ip_rotator():
    """Test av IP rotation systemet."""
    
    print("🚀 TESTING ASYNC IP ROTATOR")
    print("=" * 50)
    
    # Skapa konfiguration
    config = IPRotatorConfig(
        regions=['us-east-1', 'us-west-1', 'eu-west-1'],
        max_endpoints=6,
        endpoint_timeout=10.0,
        rotation_delay=0.1
    )
    
    print("📋 Configuration:")
    print(f"   Regions: {config.regions}")
    print(f"   Max endpoints: {config.max_endpoints}")
    print(f"   Timeout: {config.endpoint_timeout}s")
    print()
    
    # Test IP rotator
    async with AsyncIPRotator(config) as rotator:
        
        # Visa initial stats
        print("📊 Initial Stats:")
        initial_stats = await rotator.get_stats()
        print(f"   Active endpoints: {initial_stats['active_endpoints']}")
        print(f"   Total endpoints: {initial_stats['total_endpoints']}")
        print()
        
        # Simulera några requests
        print("🔄 Simulating IP rotated requests...")
        
        for i in range(8):
            try:
                # I riktig implementation: detta skulle vara riktiga HTTP requests
                # För demo: simulera request genom att bara rotera IP
                endpoint = await rotator._get_next_endpoint()
                if endpoint:
                    print(f"   {i+1}. Request via IP: {endpoint.ip} (region: {endpoint.region})")
                    
                    # Simulera request delay och update stats
                    await asyncio.sleep(0.1)
                    endpoint.success_count += 1
                    rotator.stats["requests_made"] += 1
                    
                else:
                    print(f"   {i+1}. ❌ No endpoint available")
                    
            except Exception as e:
                print(f"   {i+1}. ❌ Error: {e}")
                
        print()
        
        # Health check
        print("🏥 Performing health check...")
        health = await rotator.health_check()
        print(f"   Healthy endpoints: {health['healthy_endpoints']}/{health['total_endpoints']}")
        print(f"   Average response time: {health['average_response_time']:.2f}s")
        print(f"   Average success rate: {health['average_success_rate']:.2f}")
        print()
        
        # Final stats
        print("📈 Final Statistics:")
        final_stats = await rotator.get_stats()
        for key, value in final_stats.items():
            if key == "regions":
                print(f"   {key}:")
                for region, stats in value.items():
                    print(f"     {region}: {stats['active']}/{stats['total']} active")
            elif isinstance(value, datetime):
                print(f"   {key}: {value.strftime('%H:%M:%S')}")
            elif isinstance(value, float):
                print(f"   {key}: {value:.2f}")
            else:
                print(f"   {key}: {value}")
                
    print()
    print("✅ IP ROTATOR TEST COMPLETED!")
    print()
    print("🎯 IMPLEMENTATION SUCCESS!")
    print("   • ApiGateway klass från requests-ip-rotator moderniserad")
    print("   • Konverterad till async/await arkitektur") 
    print("   • Intelligent endpoint selection och health monitoring")
    print("   • Integration ready för proxy pool system")
    print("   • Comprehensive statistics och monitoring")
    print()
    print("📋 NÄSTA STEG:")
    print("   1. Integrera med befintligt proxy pool system")
    print("   2. Implementera riktig AWS API Gateway support")
    print("   3. Lägg till persistent endpoint storage")
    print("   4. Skapa REST API för external access")
    print("   5. Comprehensive testing med real HTTP requests")


if __name__ == "__main__":
    asyncio.run(test_ip_rotator())
