"""
Main FastAPI application configuration and setup.
"""

import os
import logging
from contextlib import asynccontextmanager
from typing import Dict, Any

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from fastapi.exception_handlers import http_exception_handler
from fastapi.exceptions import HTTPException, RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.middleware.base import BaseHTTPMiddleware

from .database import engine, Base
from .routers import (
    auth_router,
    health_router,
    webhooks_router,
    crawler_router,
    scraper_router,
    exports_router,
    privacy_router,
    templates_router
)
from .utils.rate_limiting import RateLimitMiddleware
from .utils.security import SecurityConfig, get_client_ip

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Startup
    print("🚀 Starting Dyad Crawler API...")
    
    # Create database tables
    Base.metadata.create_all(bind=engine)
    print("✅ Database tables created")
    
    # Run startup tasks
    try:
        await startup_tasks(app)
    except Exception as e:
        logger.error(f"Startup tasks failed: {e}")
    
    yield
    
    # Shutdown
    print("🛑 Shutting down Dyad Crawler API...")
    await shutdown_tasks(app)
    print("✅ Shutdown complete")


async def startup_tasks(app: FastAPI):
    """Perform startup tasks."""
    try:
        # Initialize telemetry if available
        try:
            from ..observability.telemetry import setup_telemetry
            setup_telemetry(app)
            logger.info("Telemetry setup completed")
        except ImportError:
            logger.warning("Telemetry module not available")
        
        # Initialize scheduler if available
        try:
            from ..scheduler.manager import SchedulerManager
            scheduler = SchedulerManager()
            await scheduler.initialize()
            app.state.scheduler = scheduler
            logger.info("Scheduler initialized")
        except ImportError:
            logger.warning("Scheduler module not available")
        
        # Initialize webhook manager if available
        try:
            from ..webhooks.manager import WebhookManager
            webhook_manager = WebhookManager()
            app.state.webhook_manager = webhook_manager
            logger.info("Webhook manager initialized")
        except ImportError:
            logger.warning("Webhook manager not available")
        
        logger.info("Application startup completed successfully")
        
    except Exception as e:
        logger.error(f"Error during startup: {e}")


async def shutdown_tasks(app: FastAPI):
    """Perform shutdown tasks."""
    try:
        # Stop scheduler
        if hasattr(app.state, 'scheduler'):
            await app.state.scheduler.stop()
            logger.info("Scheduler stopped")
        
        # Stop proxy manager
        if hasattr(app.state, 'proxy_manager'):
            await app.state.proxy_manager.stop()
            logger.info("Proxy manager stopped")
        
        logger.info("Application shutdown completed")
        
    except Exception as e:
        logger.error(f"Error during shutdown: {e}")


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Middleware to add security headers."""
    
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        
        # Add security headers
        for header, value in SecurityConfig.SECURITY_HEADERS.items():
            response.headers[header] = value
        
        return response


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Middleware for request logging."""
    
    async def dispatch(self, request: Request, call_next):
        import time
        
        start_time = time.time()
        client_ip = get_client_ip(dict(request.headers))
        
        # Log request
        logger.info(
            f"Request: {request.method} {request.url.path} "
            f"from {client_ip} "
            f"User-Agent: {request.headers.get('user-agent', 'unknown')}"
        )
        
        response = await call_next(request)
        
        # Log response
        process_time = time.time() - start_time
        logger.info(
            f"Response: {response.status_code} "
            f"for {request.method} {request.url.path} "
            f"in {process_time:.4f}s"
        )
        
        response.headers["X-Process-Time"] = str(process_time)
        return response


def create_app(environment: str = "development") -> FastAPI:
    """Create and configure FastAPI application."""
    
    # Application metadata
    app = FastAPI(
        title="Dyad Crawler API",
        description="Advanced web crawling and scraping platform",
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
        lifespan=lifespan
    )
    
    # Store environment in app state
    app.state.environment = environment
    
    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Configure appropriately for production
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Trusted host middleware
    trusted_hosts = os.getenv("TRUSTED_HOSTS", "localhost,127.0.0.1").split(",")
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=trusted_hosts
    )
    
    # Security headers middleware
    app.add_middleware(SecurityHeadersMiddleware)
    
    # Request logging middleware
    app.add_middleware(RequestLoggingMiddleware)
    
    # Rate limiting middleware
    app.add_middleware(RateLimitMiddleware)
    
    # Include routers
    app.include_router(health_router, prefix="/api/health", tags=["Health"])
    app.include_router(auth_router, prefix="/api/auth", tags=["Authentication"])
    app.include_router(webhooks_router, prefix="/api/webhooks", tags=["Webhooks"])
    app.include_router(crawler_router, prefix="/api/crawler", tags=["Crawler"])
    app.include_router(scraper_router, prefix="/api/scraper", tags=["Scraper"])
    app.include_router(exports_router, prefix="/api/exports", tags=["Exports"])
    app.include_router(privacy_router, prefix="/api/privacy", tags=["Privacy"])
    app.include_router(templates_router, prefix="/api/templates", tags=["Templates"])
    
    # Custom exception handlers
    @app.exception_handler(HTTPException)
    async def custom_http_exception_handler(request: Request, exc: HTTPException):
        """Custom HTTP exception handler."""
        from datetime import datetime
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": {
                    "message": exc.detail,
                    "status_code": exc.status_code,
                    "timestamp": datetime.utcnow().isoformat(),
                    "path": str(request.url.path)
                }
            }
        )
    
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        """Validation error handler."""
        from datetime import datetime
        return JSONResponse(
            status_code=422,
            content={
                "error": {
                    "message": "Validation error",
                    "details": exc.errors(),
                    "status_code": 422,
                    "timestamp": datetime.utcnow().isoformat(),
                    "path": str(request.url.path)
                }
            }
        )
    
    @app.exception_handler(500)
    async def internal_server_error_handler(request: Request, exc: Exception):
        """Internal server error handler."""
        from datetime import datetime
        
        logger.error(f"Internal server error: {str(exc)}", exc_info=True)
        
        return JSONResponse(
            status_code=500,
            content={
                "error": {
                    "message": "Internal server error",
                    "status_code": 500,
                    "timestamp": datetime.utcnow().isoformat(),
                    "path": str(request.url.path)
                }
            }
        )
    
    # Root endpoint
    @app.get("/", tags=["Root"])
    async def root():
        """Root endpoint with API information."""
        return {
            "name": "Dyad Crawler API",
            "version": "1.0.0",
            "description": "Advanced web crawling and scraping platform",
            "docs_url": "/docs",
            "health_check": "/api/health",
            "status": "operational"
        }
    
    # API info endpoint
    @app.get("/api", tags=["Root"])
    async def api_info():
        """API information endpoint."""
        return {
            "api_version": "v1",
            "endpoints": {
                "authentication": "/api/auth",
                "health": "/api/health",
                "webhooks": "/api/webhooks",
                "crawler": "/api/crawler",
                "scraper": "/api/scraper",
                "exports": "/api/exports",
                "privacy": "/api/privacy",
                "templates": "/api/templates"
            },
            "documentation": {
                "swagger": "/docs",
                "redoc": "/redoc",
                "openapi": "/openapi.json"
            }
        }
    
    return app


# Create application instance
app = create_app()


if __name__ == "__main__":
    import uvicorn
    
    # Development server configuration
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        reload_dirs=["src"],
        log_level="info"
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
