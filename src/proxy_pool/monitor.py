"""
Proxy Pool Monitor - Real-time monitoring and health checking of proxy pools.
Provides comprehensive monitoring capabilities for proxy pools including health checks,
performance metrics, and automated recovery mechanisms.
"""

import asyncio
import logging
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Set, Any
from dataclasses import dataclass
from collections import defaultdict

try:
    import aioredis
    REDIS_AVAILABLE = True
except ImportError:
    aioredis = None
    REDIS_AVAILABLE = False

from ..observability.metrics import MetricsCollector
from ..utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class ProxyHealth:
    """Health status of a proxy with detailed metrics."""
    proxy_id: str
    is_healthy: bool
    last_check: datetime
    response_time: float
    success_rate: float
    consecutive_failures: int
    total_requests: int
    total_successes: int
    last_error: Optional[str] = None
    blocked_domains: Set[str] = None
    
    def __post_init__(self):
        if self.blocked_domains is None:
            self.blocked_domains = set()


@dataclass
class PoolMetrics:
    """Aggregated metrics for a proxy pool."""
    total_proxies: int
    healthy_proxies: int
    unhealthy_proxies: int
    average_response_time: float
    overall_success_rate: float
    last_updated: datetime


class ProxyMonitor:
    """
    Advanced proxy pool monitoring system.
    
    Features:
    - Real-time health checking
    - Performance metrics collection
    - Automatic proxy rotation
    - Dead proxy detection and removal
    - Domain-specific blacklisting
    - Recovery mechanisms
    """
    
    def __init__(
        self,
        redis_client: Optional[Any],
        metrics_collector: MetricsCollector,
        check_interval: int = 60,
        health_threshold: float = 0.8,
        max_consecutive_failures: int = 5,
        timeout: float = 30.0
    ):
        self.redis = redis_client
        self.metrics = metrics_collector
        self.check_interval = check_interval
        self.health_threshold = health_threshold
        self.max_consecutive_failures = max_consecutive_failures
        self.timeout = timeout
        
        self.proxy_health: Dict[str, ProxyHealth] = {}
        self.monitoring_active = False
        self._monitor_task: Optional[asyncio.Task] = None
        
    async def start_monitoring(self):
        """Start the proxy monitoring loop."""
        if self.monitoring_active:
            logger.warning("Monitoring already active")
            return
            
        self.monitoring_active = True
        self._monitor_task = asyncio.create_task(self._monitoring_loop())
        logger.info("Proxy monitoring started")
        
    async def stop_monitoring(self):
        """Stop the proxy monitoring loop."""
        self.monitoring_active = False
        if self._monitor_task:
            self._monitor_task.cancel()
            try:
                await self._monitor_task
            except asyncio.CancelledError:
                pass
        logger.info("Proxy monitoring stopped")
        
    async def _monitoring_loop(self):
        """Main monitoring loop."""
        while self.monitoring_active:
            try:
                await self._check_all_proxies()
                await self._update_metrics()
                await self._cleanup_dead_proxies()
                await asyncio.sleep(self.check_interval)
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                await asyncio.sleep(5)  # Brief pause on error
                
    async def _check_all_proxies(self):
        """Check health of all proxies in the pool."""
        # Get all proxies from Redis
        proxy_keys = await self.redis.keys("proxy:*")
        
        if not proxy_keys:
            logger.debug("No proxies found in pool")
            return
            
        # Create semaphore to limit concurrent checks
        semaphore = asyncio.Semaphore(10)
        tasks = []
        
        for key in proxy_keys:
            proxy_data = await self.redis.hgetall(key)
            if proxy_data:
                proxy_id = key.decode().split(":")[-1]
                task = asyncio.create_task(
                    self._check_proxy_health(semaphore, proxy_id, proxy_data)
                )
                tasks.append(task)
                
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)
            
    async def _check_proxy_health(self, semaphore: asyncio.Semaphore, proxy_id: str, proxy_data: Dict):
        """Check health of a single proxy."""
        async with semaphore:
            try:
                # Get or create health record
                if proxy_id not in self.proxy_health:
                    self.proxy_health[proxy_id] = ProxyHealth(
                        proxy_id=proxy_id,
                        is_healthy=True,
                        last_check=datetime.now(),
                        response_time=0.0,
                        success_rate=1.0,
                        consecutive_failures=0,
                        total_requests=0,
                        total_successes=0
                    )
                    
                health = self.proxy_health[proxy_id]
                
                # Perform health check
                start_time = time.time()
                is_healthy, error = await self._perform_health_check(proxy_data)
                response_time = time.time() - start_time
                
                # Update health record
                health.last_check = datetime.now()
                health.response_time = response_time
                health.total_requests += 1
                
                if is_healthy:
                    health.total_successes += 1
                    health.consecutive_failures = 0
                    health.last_error = None
                else:
                    health.consecutive_failures += 1
                    health.last_error = error
                    
                # Calculate success rate
                health.success_rate = health.total_successes / health.total_requests
                
                # Determine if proxy is healthy
                health.is_healthy = (
                    health.success_rate >= self.health_threshold and
                    health.consecutive_failures < self.max_consecutive_failures
                )
                
                # Update Redis with health status
                await self.redis.hset(
                    f"proxy:{proxy_id}",
                    mapping={
                        "is_healthy": str(health.is_healthy),
                        "last_check": health.last_check.isoformat(),
                        "response_time": str(health.response_time),
                        "success_rate": str(health.success_rate),
                        "consecutive_failures": str(health.consecutive_failures)
                    }
                )
                
                logger.debug(
                    f"Proxy {proxy_id} health check: "
                    f"healthy={health.is_healthy}, "
                    f"response_time={response_time:.2f}s, "
                    f"success_rate={health.success_rate:.2f}"
                )
                
            except Exception as e:
                logger.error(f"Error checking proxy {proxy_id}: {e}")
                
    async def _perform_health_check(self, proxy_data: Dict) -> tuple[bool, Optional[str]]:
        """Perform actual health check on a proxy."""
        try:
            # Extract proxy details
            host = proxy_data.get(b"host", b"").decode()
            port = proxy_data.get(b"port", b"").decode()
            
            if not host or not port:
                return False, "Missing host or port"
                
            # Simple connectivity test (can be enhanced with actual HTTP test)
            try:
                # Test basic connectivity
                reader, writer = await asyncio.wait_for(
                    asyncio.open_connection(host, int(port)),
                    timeout=self.timeout
                )
                writer.close()
                await writer.wait_closed()
                return True, None
            except asyncio.TimeoutError:
                return False, "Connection timeout"
            except Exception as e:
                return False, f"Connection failed: {str(e)}"
                
        except Exception as e:
            return False, f"Health check error: {str(e)}"
            
    async def _update_metrics(self):
        """Update monitoring metrics."""
        if not self.proxy_health:
            return
            
        healthy_count = sum(1 for h in self.proxy_health.values() if h.is_healthy)
        total_count = len(self.proxy_health)
        
        if total_count > 0:
            avg_response_time = sum(h.response_time for h in self.proxy_health.values()) / total_count
            overall_success_rate = sum(h.success_rate for h in self.proxy_health.values()) / total_count
        else:
            avg_response_time = 0.0
            overall_success_rate = 0.0
            
        # Update metrics
        self.metrics.gauge("proxy_pool_total", total_count)
        self.metrics.gauge("proxy_pool_healthy", healthy_count)
        self.metrics.gauge("proxy_pool_unhealthy", total_count - healthy_count)
        self.metrics.gauge("proxy_pool_avg_response_time", avg_response_time)
        self.metrics.gauge("proxy_pool_success_rate", overall_success_rate)
        
        logger.debug(
            f"Pool metrics: {healthy_count}/{total_count} healthy, "
            f"avg_response_time={avg_response_time:.2f}s, "
            f"success_rate={overall_success_rate:.2f}"
        )
        
    async def _cleanup_dead_proxies(self):
        """Remove proxies that are consistently failing."""
        dead_proxies = []
        
        for proxy_id, health in self.proxy_health.items():
            if (
                not health.is_healthy and
                health.consecutive_failures >= self.max_consecutive_failures and
                health.success_rate < 0.1  # Less than 10% success rate
            ):
                dead_proxies.append(proxy_id)
                
        for proxy_id in dead_proxies:
            await self._remove_dead_proxy(proxy_id)
            
    async def _remove_dead_proxy(self, proxy_id: str):
        """Remove a dead proxy from the pool."""
        try:
            # Remove from Redis
            await self.redis.delete(f"proxy:{proxy_id}")
            
            # Remove from health tracking
            if proxy_id in self.proxy_health:
                del self.proxy_health[proxy_id]
                
            # Log removal
            logger.warning(f"Removed dead proxy {proxy_id} from pool")
            
            # Update metrics
            self.metrics.counter("proxy_pool_removed_dead", 1)
            
        except Exception as e:
            logger.error(f"Error removing dead proxy {proxy_id}: {e}")
            
    async def get_pool_metrics(self) -> PoolMetrics:
        """Get current pool metrics."""
        if not self.proxy_health:
            return PoolMetrics(
                total_proxies=0,
                healthy_proxies=0,
                unhealthy_proxies=0,
                average_response_time=0.0,
                overall_success_rate=0.0,
                last_updated=datetime.now()
            )
            
        healthy_count = sum(1 for h in self.proxy_health.values() if h.is_healthy)
        total_count = len(self.proxy_health)
        avg_response_time = sum(h.response_time for h in self.proxy_health.values()) / total_count
        overall_success_rate = sum(h.success_rate for h in self.proxy_health.values()) / total_count
        
        return PoolMetrics(
            total_proxies=total_count,
            healthy_proxies=healthy_count,
            unhealthy_proxies=total_count - healthy_count,
            average_response_time=avg_response_time,
            overall_success_rate=overall_success_rate,
            last_updated=datetime.now()
        )
        
    async def get_proxy_health(self, proxy_id: str) -> Optional[ProxyHealth]:
        """Get health information for a specific proxy."""
        return self.proxy_health.get(proxy_id)
        
    async def mark_proxy_blocked(self, proxy_id: str, domain: str):
        """Mark a proxy as blocked for a specific domain."""
        if proxy_id in self.proxy_health:
            self.proxy_health[proxy_id].blocked_domains.add(domain)
            logger.warning(f"Proxy {proxy_id} marked as blocked for domain {domain}")
            
    async def is_proxy_blocked_for_domain(self, proxy_id: str, domain: str) -> bool:
        """Check if a proxy is blocked for a specific domain."""
        if proxy_id in self.proxy_health:
            return domain in self.proxy_health[proxy_id].blocked_domains
        return False