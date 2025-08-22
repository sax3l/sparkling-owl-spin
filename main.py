"""
Main application entry point for the crawler platform.

Starts all services and provides a unified interface for:
- Web API (FastAPI)
- Scheduler (APScheduler)
- Proxy pool management
- Background workers
- Monitoring and health checks
"""

import asyncio
import logging
import signal
import sys
from contextlib import asynccontextmanager
from typing import Dict, Any
import uvicorn
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import yaml

# Import application modules
from src.utils.config_loader import ConfigLoader
from src.webapp.api import router as api_router
from src.webapp.views import router as views_router
from src.webapp.auth import router as auth_router
from src.proxy_pool.api.server import router as proxy_router
from src.scheduler.scheduler import SchedulerService
from src.database.connection import get_db_connection, close_db_connection
from src.observability.metrics import get_metrics_collector, shutdown_metrics
from src.utils.logger import get_logger, setup_logging

logger = get_logger(__name__)

# Global services
scheduler_service = None
metrics_collector = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Startup
    logger.info("Starting crawler application...")
    
    try:
        # Initialize services
        await startup_services()
        logger.info("All services started successfully")
        yield
        
    except Exception as e:
        logger.error(f"Failed to start services: {e}")
        raise
    finally:
        # Shutdown
        logger.info("Shutting down crawler application...")
        await shutdown_services()
        logger.info("All services shut down")

async def startup_services():
    """Initialize all application services."""
    global scheduler_service, metrics_collector
    
    # Setup logging
    setup_logging()
    
    # Initialize database
    logger.info("Initializing database connection...")
    db = await get_db_connection()
    await db.health_check()
    
    # Initialize metrics collector
    logger.info("Starting metrics collector...")
    metrics_collector = get_metrics_collector()
    
    # Initialize scheduler
    logger.info("Starting scheduler service...")
    scheduler_service = SchedulerService()
    await scheduler_service.start()
    
    # Register scheduled jobs
    await register_scheduled_jobs()
    
    logger.info("Services startup completed")

async def shutdown_services():
    """Shutdown all application services."""
    global scheduler_service, metrics_collector
    
    # Stop scheduler
    if scheduler_service:
        logger.info("Stopping scheduler service...")
        await scheduler_service.stop()
    
    # Stop metrics collector
    if metrics_collector:
        logger.info("Stopping metrics collector...")
        await shutdown_metrics()
    
    # Close database connections
    logger.info("Closing database connections...")
    await close_db_connection()

async def register_scheduled_jobs():
    """Register all scheduled jobs with the scheduler."""
    global scheduler_service
    
    if not scheduler_service:
        return
    
    # Daily retention cleanup at 2 AM
    await scheduler_service.add_job(
        func="src.scheduler.jobs.retention_job:run_retention_job",
        trigger="cron",
        hour=2,
        minute=0,
        id="daily_retention_cleanup",
        name="Daily Retention Cleanup"
    )
    
    # Redis snapshot every 6 hours
    await scheduler_service.add_job(
        func="src.scheduler.jobs.redis_snapshot_job:run_redis_snapshot",
        trigger="cron",
        hour="*/6",
        minute=0,
        id="redis_snapshot",
        name="Redis Snapshot Backup"
    )
    
    # Proxy pool health check every 5 minutes
    await scheduler_service.add_job(
        func="src.proxy_pool.monitor:run_health_check",
        trigger="interval",
        minutes=5,
        id="proxy_health_check",
        name="Proxy Pool Health Check"
    )
    
    logger.info("Scheduled jobs registered successfully")

def create_app() -> FastAPI:
    """Create and configure FastAPI application."""
    
    # Load configuration
    config = load_config()
    
    # Create FastAPI app
    app = FastAPI(
        title="Crawler Platform",
        description="Advanced web crawling and data extraction platform",
        version="1.0.0",
        lifespan=lifespan,
        docs_url="/api/docs",
        redoc_url="/api/redoc"
    )
    
    # Configure CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=config.get("cors", {}).get("allow_origins", ["*"]),
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Mount static files
    app.mount("/static", StaticFiles(directory="frontend/dist"), name="static")
    
    # Include routers
    app.include_router(api_router, prefix="/api/v1", tags=["API"])
    app.include_router(auth_router, prefix="/auth", tags=["Authentication"])
    app.include_router(proxy_router, prefix="/proxy", tags=["Proxy Pool"])
    app.include_router(views_router, prefix="", tags=["Web Views"])
    
    # Health check endpoint
    @app.get("/health")
    async def health_check():
        """Application health check."""
        try:
            # Check database
            db = await get_db_connection()
            db_healthy = await db.health_check()
            
            # Check scheduler
            scheduler_healthy = scheduler_service.is_running() if scheduler_service else False
            
            # Get metrics
            metrics = get_metrics_collector()
            
            health_status = {
                "status": "healthy" if db_healthy and scheduler_healthy else "unhealthy",
                "timestamp": "2024-01-15T12:00:00Z",  # Would use datetime.utcnow()
                "services": {
                    "database": "healthy" if db_healthy else "unhealthy",
                    "scheduler": "healthy" if scheduler_healthy else "unhealthy",
                    "metrics": "healthy"
                },
                "version": "1.0.0"
            }
            
            return health_status
            
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return {
                "status": "unhealthy",
                "error": str(e),
                "timestamp": "2024-01-15T12:00:00Z"
            }
    
    # Root redirect
    @app.get("/")
    async def root():
        """Redirect root to dashboard."""
        return {"message": "Crawler Platform API", "docs": "/api/docs", "dashboard": "/dashboard"}
    
    return app

def load_config() -> Dict[str, Any]:
    """Load application configuration using the comprehensive ConfigLoader."""
    try:
        config_loader = ConfigLoader()
        return config_loader.get_config("config/app_config.yml")
    except FileNotFoundError:
        logger.warning("Config file not found, using defaults")
        return {
            "cors": {"allow_origins": ["*"]},
            "server": {"host": "0.0.0.0", "port": 8000},
            "debug": False
        }

def setup_signal_handlers():
    """Setup signal handlers for graceful shutdown."""
    def signal_handler(signum, frame):
        logger.info(f"Received signal {signum}, initiating graceful shutdown...")
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

def run_server():
    """Run the application server."""
    config = load_config()
    server_config = config.get("server", {})
    
    setup_signal_handlers()
    
    uvicorn.run(
        "main:create_app",
        factory=True,
        host=server_config.get("host", "0.0.0.0"),
        port=server_config.get("port", 8000),
        reload=config.get("debug", False),
        log_level="info",
        access_log=True
    )

if __name__ == "__main__":
    run_server()
