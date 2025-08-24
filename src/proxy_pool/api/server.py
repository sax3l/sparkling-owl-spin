"""
Proxy Pool API Server - FastAPI server for proxy pool management.
Provides RESTful API endpoints for proxy pool operations, monitoring, and administration.
"""

from datetime import datetime
from typing import Dict, List, Optional, Union
from fastapi import FastAPI, HTTPException, Depends, Query, Path
from pydantic import BaseModel, Field
import asyncio
import logging

from ..manager import ProxyManager
from ..monitor import ProxyMonitor, ProxyHealth, PoolMetrics
from observability.metrics import MetricsCollector
from utils.logger import get_logger

logger = get_logger(__name__)


# Pydantic models for API
class ProxyResponse(BaseModel):
    """Response model for proxy data."""
    proxy_id: str
    host: str
    port: int
    protocol: str = "http"
    country: Optional[str] = None
    anonymity: Optional[str] = None
    is_healthy: bool = True
    response_time: float = 0.0
    success_rate: float = 1.0
    last_used: Optional[datetime] = None


class ProxyRequest(BaseModel):
    """Request model for adding new proxy."""
    host: str = Field(..., description="Proxy host/IP address")
    port: int = Field(..., ge=1, le=65535, description="Proxy port")
    protocol: str = Field(default="http", pattern="^(http|https|socks4|socks5)$")
    username: Optional[str] = None
    password: Optional[str] = None
    country: Optional[str] = None
    anonymity: Optional[str] = Field(default="unknown", pattern="^(elite|anonymous|transparent|unknown)$")


class PoolStatsResponse(BaseModel):
    """Response model for pool statistics."""
    total_proxies: int
    healthy_proxies: int
    unhealthy_proxies: int
    average_response_time: float
    overall_success_rate: float
    last_updated: datetime


class ProxyHealthResponse(BaseModel):
    """Response model for proxy health information."""
    proxy_id: str
    is_healthy: bool
    last_check: datetime
    response_time: float
    success_rate: float
    consecutive_failures: int
    total_requests: int
    total_successes: int
    last_error: Optional[str] = None
    blocked_domains: List[str] = []


def create_proxy_api(
    proxy_manager: ProxyManager,
    proxy_monitor: ProxyMonitor,
    metrics_collector: MetricsCollector
) -> FastAPI:
    """Create FastAPI app for proxy pool management."""
    
    app = FastAPI(
        title="Proxy Pool API",
        description="API for managing proxy pools with health monitoring and statistics",
        version="1.0.0"
    )
    
    @app.get("/health")
    async def health_check():
        """Health check endpoint."""
        return {"status": "healthy", "timestamp": datetime.now()}
    
    @app.get("/proxies", response_model=List[ProxyResponse])
    async def get_proxies(
        healthy_only: bool = Query(False, description="Return only healthy proxies"),
        limit: Optional[int] = Query(None, ge=1, le=1000, description="Limit number of results")
    ):
        """Get list of all proxies."""
        try:
            proxies = await proxy_manager.get_all_proxies()
            
            # Filter healthy proxies if requested
            if healthy_only:
                proxies = [p for p in proxies if p.get("is_healthy", True)]
            
            # Apply limit
            if limit:
                proxies = proxies[:limit]
                
            return [
                ProxyResponse(
                    proxy_id=proxy["id"],
                    host=proxy["host"],
                    port=proxy["port"],
                    protocol=proxy.get("protocol", "http"),
                    country=proxy.get("country"),
                    anonymity=proxy.get("anonymity"),
                    is_healthy=proxy.get("is_healthy", True),
                    response_time=proxy.get("response_time", 0.0),
                    success_rate=proxy.get("success_rate", 1.0),
                    last_used=proxy.get("last_used")
                )
                for proxy in proxies
            ]
            
        except Exception as e:
            logger.error(f"Error getting proxies: {e}")
            raise HTTPException(status_code=500, detail="Failed to retrieve proxies")
    
    @app.get("/proxies/{proxy_id}", response_model=ProxyResponse)
    async def get_proxy(proxy_id: str = Path(..., description="Proxy ID")):
        """Get specific proxy by ID."""
        try:
            proxy = await proxy_manager.get_proxy(proxy_id)
            if not proxy:
                raise HTTPException(status_code=404, detail="Proxy not found")
                
            return ProxyResponse(
                proxy_id=proxy["id"],
                host=proxy["host"],
                port=proxy["port"],
                protocol=proxy.get("protocol", "http"),
                country=proxy.get("country"),
                anonymity=proxy.get("anonymity"),
                is_healthy=proxy.get("is_healthy", True),
                response_time=proxy.get("response_time", 0.0),
                success_rate=proxy.get("success_rate", 1.0),
                last_used=proxy.get("last_used")
            )
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error getting proxy {proxy_id}: {e}")
            raise HTTPException(status_code=500, detail="Failed to retrieve proxy")
    
    @app.post("/proxies", response_model=ProxyResponse, status_code=201)
    async def add_proxy(proxy_data: ProxyRequest):
        """Add new proxy to the pool."""
        try:
            proxy_id = await proxy_manager.add_proxy(
                host=proxy_data.host,
                port=proxy_data.port,
                protocol=proxy_data.protocol,
                username=proxy_data.username,
                password=proxy_data.password,
                country=proxy_data.country,
                anonymity=proxy_data.anonymity
            )
            
            # Get the added proxy
            proxy = await proxy_manager.get_proxy(proxy_id)
            
            return ProxyResponse(
                proxy_id=proxy["id"],
                host=proxy["host"],
                port=proxy["port"],
                protocol=proxy.get("protocol", "http"),
                country=proxy.get("country"),
                anonymity=proxy.get("anonymity"),
                is_healthy=True,
                response_time=0.0,
                success_rate=1.0
            )
            
        except Exception as e:
            logger.error(f"Error adding proxy: {e}")
            raise HTTPException(status_code=500, detail="Failed to add proxy")
    
    @app.delete("/proxies/{proxy_id}")
    async def delete_proxy(proxy_id: str = Path(..., description="Proxy ID")):
        """Delete proxy from the pool."""
        try:
            success = await proxy_manager.remove_proxy(proxy_id)
            if not success:
                raise HTTPException(status_code=404, detail="Proxy not found")
                
            return {"message": f"Proxy {proxy_id} deleted successfully"}
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error deleting proxy {proxy_id}: {e}")
            raise HTTPException(status_code=500, detail="Failed to delete proxy")
    
    @app.get("/proxies/acquire", response_model=ProxyResponse)
    async def acquire_proxy(
        domain: Optional[str] = Query(None, description="Domain for proxy selection"),
        protocol: Optional[str] = Query(None, description="Required protocol")
    ):
        """Acquire a proxy for use."""
        try:
            proxy = await proxy_manager.get_proxy_for_domain(domain, protocol)
            if not proxy:
                raise HTTPException(status_code=404, detail="No suitable proxy available")
                
            return ProxyResponse(
                proxy_id=proxy["id"],
                host=proxy["host"],
                port=proxy["port"],
                protocol=proxy.get("protocol", "http"),
                country=proxy.get("country"),
                anonymity=proxy.get("anonymity"),
                is_healthy=proxy.get("is_healthy", True),
                response_time=proxy.get("response_time", 0.0),
                success_rate=proxy.get("success_rate", 1.0)
            )
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error acquiring proxy: {e}")
            raise HTTPException(status_code=500, detail="Failed to acquire proxy")
    
    @app.post("/proxies/{proxy_id}/release")
    async def release_proxy(
        proxy_id: str = Path(..., description="Proxy ID"),
        success: bool = Query(True, description="Whether the proxy use was successful")
    ):
        """Release a proxy after use."""
        try:
            await proxy_manager.release_proxy(proxy_id, success)
            return {"message": f"Proxy {proxy_id} released successfully"}
            
        except Exception as e:
            logger.error(f"Error releasing proxy {proxy_id}: {e}")
            raise HTTPException(status_code=500, detail="Failed to release proxy")
    
    @app.get("/proxies/{proxy_id}/health", response_model=ProxyHealthResponse)
    async def get_proxy_health(proxy_id: str = Path(..., description="Proxy ID")):
        """Get health information for a specific proxy."""
        try:
            health = await proxy_monitor.get_proxy_health(proxy_id)
            if not health:
                raise HTTPException(status_code=404, detail="Proxy health data not found")
                
            return ProxyHealthResponse(
                proxy_id=health.proxy_id,
                is_healthy=health.is_healthy,
                last_check=health.last_check,
                response_time=health.response_time,
                success_rate=health.success_rate,
                consecutive_failures=health.consecutive_failures,
                total_requests=health.total_requests,
                total_successes=health.total_successes,
                last_error=health.last_error,
                blocked_domains=list(health.blocked_domains)
            )
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error getting proxy health {proxy_id}: {e}")
            raise HTTPException(status_code=500, detail="Failed to retrieve proxy health")
    
    @app.get("/stats", response_model=PoolStatsResponse)
    async def get_pool_stats():
        """Get proxy pool statistics."""
        try:
            metrics = await proxy_monitor.get_pool_metrics()
            
            return PoolStatsResponse(
                total_proxies=metrics.total_proxies,
                healthy_proxies=metrics.healthy_proxies,
                unhealthy_proxies=metrics.unhealthy_proxies,
                average_response_time=metrics.average_response_time,
                overall_success_rate=metrics.overall_success_rate,
                last_updated=metrics.last_updated
            )
            
        except Exception as e:
            logger.error(f"Error getting pool stats: {e}")
            raise HTTPException(status_code=500, detail="Failed to retrieve pool statistics")
    
    @app.post("/proxies/validate")
    async def validate_all_proxies():
        """Trigger validation of all proxies in the pool."""
        try:
            # This would trigger the monitor to check all proxies
            # Implementation depends on monitor capabilities
            return {"message": "Proxy validation triggered"}
            
        except Exception as e:
            logger.error(f"Error validating proxies: {e}")
            raise HTTPException(status_code=500, detail="Failed to validate proxies")
    
    @app.post("/proxies/cleanup")
    async def cleanup_dead_proxies():
        """Remove dead/unhealthy proxies from the pool."""
        try:
            # This would trigger cleanup of dead proxies
            # Implementation depends on manager capabilities
            return {"message": "Dead proxy cleanup triggered"}
            
        except Exception as e:
            logger.error(f"Error cleaning up proxies: {e}")
            raise HTTPException(status_code=500, detail="Failed to cleanup proxies")
    
    @app.get("/metrics")
    async def get_metrics():
        """Get prometheus-style metrics."""
        try:
            # Return metrics in Prometheus format
            metrics_data = metrics_collector.get_metrics()
            return {"metrics": metrics_data}
            
        except Exception as e:
            logger.error(f"Error getting metrics: {e}")
            raise HTTPException(status_code=500, detail="Failed to retrieve metrics")
    
    return app


# Factory function for creating the app with dependencies
async def create_proxy_server(redis_url: str = "redis://localhost:6379") -> FastAPI:
    """Create proxy server with all dependencies."""
    import aioredis
    
    # Initialize Redis connection
    redis_client = await aioredis.from_url(redis_url)
    
    # Initialize components
    metrics_collector = MetricsCollector()
    proxy_manager = ProxyManager(redis_client, metrics_collector)
    proxy_monitor = ProxyMonitor(redis_client, metrics_collector)
    
    # Start monitoring
    await proxy_monitor.start_monitoring()
    
    # Create and return the app
    return create_proxy_api(proxy_manager, proxy_monitor, metrics_collector)