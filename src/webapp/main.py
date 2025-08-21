"""
Main FastAPI application configuration and setup.
"""
import logging
from contextlib import asynccontextmanager
from typing import Dict, Any

from fastapi import FastAPI, Request, Response, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
import uvicorn

from src.webapp.api.v1.router import api_router
from src.webapp.middleware.auth import AuthMiddleware
from src.webapp.middleware.rate_limit import RateLimitMiddleware
from src.webapp.middleware.request_id import RequestIDMiddleware
from src.utils.logger import setup_logging
from src.utils.config_loader import ConfigLoader

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Startup
    logger.info("Starting scraping platform API...")
    
    # Initialize database connections, load configs, etc.
    await startup_tasks()
    
    yield
    
    # Shutdown
    logger.info("Shutting down scraping platform API...")
    await shutdown_tasks()


async def startup_tasks():
    """Perform startup tasks."""
    # Load configuration
    config_loader = ConfigLoader()
    app.state.config = config_loader.load_config_with_env("config/app_config.yml")
    
    # Initialize database
    from src.database.connection import DatabaseManager
    app.state.db = DatabaseManager()
    await app.state.db.connect()
    
    # Initialize other services
    logger.info("Application startup completed")


async def shutdown_tasks():
    """Perform shutdown tasks."""
    # Close database connections
    if hasattr(app.state, 'db'):
        await app.state.db.disconnect()
    
    logger.info("Application shutdown completed")


def create_app() -> FastAPI:
    """Create and configure FastAPI application."""
    
    # Setup logging
    setup_logging()
    
    # Create FastAPI app
    app = FastAPI(
        title="Scraping Platform API",
        description="Advanced web scraping and data extraction platform",
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc",
        lifespan=lifespan
    )
    
    # Add middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Configure appropriately for production
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    app.add_middleware(GZipMiddleware, minimum_size=1000)
    app.add_middleware(RequestIDMiddleware)
    app.add_middleware(RateLimitMiddleware)
    app.add_middleware(AuthMiddleware)
    
    # Include routers
    app.include_router(api_router, prefix="/api")
    
    # Global exception handlers
    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException):
        """Handle HTTP exceptions."""
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": {
                    "type": "http_error",
                    "message": exc.detail,
                    "status_code": exc.status_code
                }
            }
        )
    
    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        """Handle general exceptions."""
        logger.error(f"Unhandled exception: {exc}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={
                "error": {
                    "type": "internal_error",
                    "message": "An internal server error occurred",
                    "status_code": 500
                }
            }
        )
    
    # Health check endpoint
    @app.get("/health")
    async def health_check():
        """Health check endpoint."""
        return {
            "status": "healthy",
            "service": "scraping-platform-api",
            "version": "1.0.0"
        }
    
    # Metrics endpoint
    @app.get("/metrics")
    async def metrics():
        """Metrics endpoint for monitoring."""
        # Return basic metrics
        return {
            "total_requests": getattr(app.state, 'total_requests', 0),
            "active_sessions": getattr(app.state, 'active_sessions', 0),
            "uptime": getattr(app.state, 'uptime', 0)
        }
    
    return app


# Create app instance
app = create_app()


if __name__ == "__main__":
    uvicorn.run(
        "src.webapp.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
