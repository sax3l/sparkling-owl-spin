"""
Health check router for monitoring application status.
"""
import asyncio
import time
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import psutil
import json

from ..deps import get_database, get_redis_client
from ..config import get_settings

router = APIRouter()

class HealthStatus(BaseModel):
    """Health status model."""
    status: str
    timestamp: datetime
    uptime: float
    version: str
    environment: str

class DetailedHealthStatus(BaseModel):
    """Detailed health status model."""
    status: str
    timestamp: datetime
    uptime: float
    version: str
    environment: str
    services: Dict[str, Dict[str, Any]]
    system: Dict[str, Any]
    metrics: Dict[str, Any]

class ServiceHealth(BaseModel):
    """Individual service health model."""
    status: str
    response_time: Optional[float] = None
    error: Optional[str] = None
    last_check: datetime
    metadata: Optional[Dict[str, Any]] = None

# Global variables for tracking
app_start_time = time.time()
health_cache = {}
cache_ttl = 30  # seconds

class HealthChecker:
    """Health checking service."""
    
    def __init__(self):
        self.settings = get_settings()
    
    async def check_database(self) -> ServiceHealth:
        """Check database connectivity."""
        start_time = time.time()
        try:
            db = next(get_database())
            # Simple query to test connection
            result = db.execute("SELECT 1").fetchone()
            response_time = (time.time() - start_time) * 1000
            
            return ServiceHealth(
                status="healthy",
                response_time=response_time,
                last_check=datetime.utcnow(),
                metadata={"query_result": result[0] if result else None}
            )
        except Exception as e:
            return ServiceHealth(
                status="unhealthy",
                error=str(e),
                response_time=(time.time() - start_time) * 1000,
                last_check=datetime.utcnow()
            )
    
    async def check_redis(self) -> ServiceHealth:
        """Check Redis connectivity."""
        start_time = time.time()
        try:
            redis_client = await get_redis_client()
            await redis_client.ping()
            response_time = (time.time() - start_time) * 1000
            
            # Get Redis info
            info = await redis_client.info()
            
            return ServiceHealth(
                status="healthy",
                response_time=response_time,
                last_check=datetime.utcnow(),
                metadata={
                    "connected_clients": info.get("connected_clients", 0),
                    "used_memory": info.get("used_memory_human", "N/A"),
                    "uptime_in_seconds": info.get("uptime_in_seconds", 0)
                }
            )
        except Exception as e:
            return ServiceHealth(
                status="unhealthy",
                error=str(e),
                response_time=(time.time() - start_time) * 1000,
                last_check=datetime.utcnow()
            )
    
    async def check_external_services(self) -> Dict[str, ServiceHealth]:
        """Check external services health."""
        services = {}
        
        # Check scheduler if enabled
        if self.settings.scheduler.enabled:
            try:
                # This would check if scheduler is responsive
                services["scheduler"] = ServiceHealth(
                    status="healthy",
                    last_check=datetime.utcnow(),
                    metadata={"enabled": True}
                )
            except Exception as e:
                services["scheduler"] = ServiceHealth(
                    status="unhealthy",
                    error=str(e),
                    last_check=datetime.utcnow()
                )
        
        # Check proxy pool if enabled
        if self.settings.proxy_pool.enabled:
            try:
                services["proxy_pool"] = ServiceHealth(
                    status="healthy",
                    last_check=datetime.utcnow(),
                    metadata={"enabled": True}
                )
            except Exception as e:
                services["proxy_pool"] = ServiceHealth(
                    status="unhealthy",
                    error=str(e),
                    last_check=datetime.utcnow()
                )
        
        return services
    
    def get_system_metrics(self) -> Dict[str, Any]:
        """Get system metrics."""
        try:
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)
            
            # Memory usage
            memory = psutil.virtual_memory()
            
            # Disk usage
            disk = psutil.disk_usage('/')
            
            # Network stats
            network = psutil.net_io_counters()
            
            return {
                "cpu": {
                    "percent": cpu_percent,
                    "count": psutil.cpu_count()
                },
                "memory": {
                    "total": memory.total,
                    "available": memory.available,
                    "percent": memory.percent,
                    "used": memory.used
                },
                "disk": {
                    "total": disk.total,
                    "used": disk.used,
                    "free": disk.free,
                    "percent": (disk.used / disk.total) * 100
                },
                "network": {
                    "bytes_sent": network.bytes_sent,
                    "bytes_recv": network.bytes_recv,
                    "packets_sent": network.packets_sent,
                    "packets_recv": network.packets_recv
                }
            }
        except Exception as e:
            return {"error": str(e)}
    
    def get_application_metrics(self) -> Dict[str, Any]:
        """Get application-specific metrics."""
        uptime = time.time() - app_start_time
        
        return {
            "uptime_seconds": uptime,
            "uptime_human": str(timedelta(seconds=int(uptime))),
            "start_time": datetime.fromtimestamp(app_start_time).isoformat(),
            "current_time": datetime.utcnow().isoformat(),
            "environment": self.settings.environment,
            "debug_mode": self.settings.debug
        }

health_checker = HealthChecker()

async def get_cached_health() -> Dict[str, Any]:
    """Get cached health status or perform new check."""
    current_time = time.time()
    
    # Check if cache is still valid
    if ("last_check" in health_cache and 
        current_time - health_cache["last_check"] < cache_ttl):
        return health_cache["data"]
    
    # Perform health checks
    health_data = await perform_health_checks()
    
    # Update cache
    health_cache["data"] = health_data
    health_cache["last_check"] = current_time
    
    return health_data

async def perform_health_checks() -> Dict[str, Any]:
    """Perform comprehensive health checks."""
    # Check core services
    database_health = await health_checker.check_database()
    redis_health = await health_checker.check_redis()
    
    # Check external services
    external_services = await health_checker.check_external_services()
    
    # Get system metrics
    system_metrics = health_checker.get_system_metrics()
    app_metrics = health_checker.get_application_metrics()
    
    # Determine overall status
    services = {
        "database": database_health.dict(),
        "redis": redis_health.dict(),
        **{k: v.dict() for k, v in external_services.items()}
    }
    
    # Overall status determination
    all_healthy = all(
        service["status"] == "healthy" 
        for service in services.values()
    )
    
    overall_status = "healthy" if all_healthy else "degraded"
    
    # Check for critical failures
    critical_services = ["database", "redis"]
    critical_unhealthy = any(
        services.get(service, {}).get("status") == "unhealthy"
        for service in critical_services
    )
    
    if critical_unhealthy:
        overall_status = "unhealthy"
    
    return {
        "status": overall_status,
        "timestamp": datetime.utcnow().isoformat(),
        "services": services,
        "system": system_metrics,
        "metrics": app_metrics
    }

# Routes
@router.get("/", response_model=HealthStatus)
async def basic_health_check():
    """Basic health check endpoint."""
    settings = get_settings()
    uptime = time.time() - app_start_time
    
    return HealthStatus(
        status="healthy",
        timestamp=datetime.utcnow(),
        uptime=uptime,
        version=settings.app_version,
        environment=settings.environment
    )

@router.get("/detailed", response_model=DetailedHealthStatus)
async def detailed_health_check():
    """Detailed health check with all service statuses."""
    health_data = await get_cached_health()
    settings = get_settings()
    
    return DetailedHealthStatus(
        status=health_data["status"],
        timestamp=datetime.fromisoformat(health_data["timestamp"]),
        uptime=health_data["metrics"]["uptime_seconds"],
        version=settings.app_version,
        environment=settings.environment,
        services=health_data["services"],
        system=health_data["system"],
        metrics=health_data["metrics"]
    )

@router.get("/live")
async def liveness_probe():
    """Kubernetes liveness probe endpoint."""
    # Simple check that the application is running
    try:
        uptime = time.time() - app_start_time
        if uptime < 5:  # Allow 5 seconds for startup
            return JSONResponse(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                content={"status": "starting", "uptime": uptime}
            )
        
        return {"status": "alive", "uptime": uptime}
    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={"status": "error", "error": str(e)}
        )

@router.get("/ready")
async def readiness_probe():
    """Kubernetes readiness probe endpoint."""
    # Check if application is ready to serve traffic
    try:
        # Quick health check of critical services
        db_task = health_checker.check_database()
        redis_task = health_checker.check_redis()
        
        database_health, redis_health = await asyncio.gather(
            db_task, redis_task, return_exceptions=True
        )
        
        # Check if critical services are healthy
        db_healthy = (
            not isinstance(database_health, Exception) and 
            database_health.status == "healthy"
        )
        redis_healthy = (
            not isinstance(redis_health, Exception) and 
            redis_health.status == "healthy"
        )
        
        if not (db_healthy and redis_healthy):
            return JSONResponse(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                content={
                    "status": "not_ready",
                    "database": "healthy" if db_healthy else "unhealthy",
                    "redis": "healthy" if redis_healthy else "unhealthy"
                }
            )
        
        return {
            "status": "ready",
            "database": "healthy",
            "redis": "healthy"
        }
        
    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={"status": "error", "error": str(e)}
        )

@router.get("/metrics")
async def metrics_endpoint():
    """Prometheus-style metrics endpoint."""
    try:
        health_data = await get_cached_health()
        
        # Convert to Prometheus format
        metrics_lines = []
        
        # Application metrics
        metrics_lines.append(f"# HELP app_uptime_seconds Application uptime in seconds")
        metrics_lines.append(f"# TYPE app_uptime_seconds gauge")
        metrics_lines.append(f"app_uptime_seconds {health_data['metrics']['uptime_seconds']}")
        
        # Service health metrics
        for service_name, service_data in health_data["services"].items():
            status_value = 1 if service_data["status"] == "healthy" else 0
            metrics_lines.append(f"# HELP service_health_{service_name} Service health status")
            metrics_lines.append(f"# TYPE service_health_{service_name} gauge") 
            metrics_lines.append(f"service_health_{service_name} {status_value}")
            
            # Response time metrics
            if "response_time" in service_data and service_data["response_time"]:
                metrics_lines.append(f"# HELP service_response_time_{service_name}_ms Service response time in milliseconds")
                metrics_lines.append(f"# TYPE service_response_time_{service_name}_ms gauge")
                metrics_lines.append(f"service_response_time_{service_name}_ms {service_data['response_time']}")
        
        # System metrics
        if "system" in health_data and "error" not in health_data["system"]:
            sys_metrics = health_data["system"]
            
            # CPU metrics
            if "cpu" in sys_metrics:
                metrics_lines.append(f"# HELP system_cpu_percent CPU usage percentage")
                metrics_lines.append(f"# TYPE system_cpu_percent gauge")
                metrics_lines.append(f"system_cpu_percent {sys_metrics['cpu']['percent']}")
            
            # Memory metrics
            if "memory" in sys_metrics:
                mem = sys_metrics["memory"]
                metrics_lines.append(f"# HELP system_memory_percent Memory usage percentage")
                metrics_lines.append(f"# TYPE system_memory_percent gauge")
                metrics_lines.append(f"system_memory_percent {mem['percent']}")
        
        return "\n".join(metrics_lines)
        
    except Exception as e:
        return f"# Error generating metrics: {str(e)}"

@router.get("/ping")
async def ping():
    """Simple ping endpoint."""
    return {"message": "pong", "timestamp": datetime.utcnow().isoformat()}

@router.get("/version")
async def version_info():
    """Get application version information."""
    settings = get_settings()
    
    return {
        "version": settings.app_version,
        "name": settings.app_name,
        "environment": settings.environment,
        "debug": settings.debug,
        "python_version": f"{psutil.sys.version_info.major}.{psutil.sys.version_info.minor}.{psutil.sys.version_info.micro}",
        "build_time": datetime.utcnow().isoformat()  # In real app, this would be build timestamp
    }
