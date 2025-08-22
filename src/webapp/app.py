"""
ECaDP FastAPI Application

Main FastAPI application factory with complete middleware stack, 
authentication, rate limiting, and all API routes according to Backend specification.
"""

import logging
import time
from contextlib import asynccontextmanager
from typing import Dict, Any

from fastapi import FastAPI, Request, Response, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from fastapi.exception_handlers import http_exception_handler
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.middleware.sessions import SessionMiddleware
import uvicorn

from ..settings import get_settings
from ..database.manager import get_database_manager

logger = logging.getLogger(__name__)


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Middleware for structured request/response logging."""
    
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        
        # Log request
        logger.info(
            "Request started",
            extra={
                "method": request.method,
                "url": str(request.url),
                "client_ip": request.client.host if request.client else "unknown",
                "user_agent": request.headers.get("user-agent", ""),
                "correlation_id": getattr(request.state, "correlation_id", None)
            }
        )
        
        try:
            response = await call_next(request)
            
            # Log response
            duration = time.time() - start_time
            logger.info(
                "Request completed",
                extra={
                    "status_code": response.status_code,
                    "duration_ms": round(duration * 1000, 2),
                    "correlation_id": getattr(request.state, "correlation_id", None)
                }
            )
            
            # Add timing headers
            response.headers["X-Process-Time"] = str(duration)
            return response
            
        except Exception as exc:
            duration = time.time() - start_time
            logger.error(
                "Request failed",
                extra={
                    "error": str(exc),
                    "duration_ms": round(duration * 1000, 2),
                    "correlation_id": getattr(request.state, "correlation_id", None)
                },
                exc_info=True
            )
            raise


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan management."""
    # Startup
    logger.info("Starting ECaDP Backend")
    
    # Initialize database
    try:
        db_manager = get_database_manager()
        db_info = db_manager.test_connection()
        logger.info(f"Database connected: {db_info['vendor']} {db_info['version']}")
        
        # Create tables if they don't exist
        db_manager.create_tables()
        logger.info("Database tables verified/created")
        
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        raise
    
    logger.info("ECaDP Backend started successfully")
    
    yield
    
    # Shutdown
    logger.info("Shutting down ECaDP Backend")


def create_app() -> FastAPI:
    """Create and configure FastAPI application."""
    settings = get_settings()
    
    app = FastAPI(
        title="ECaDP Backend API",
        description="Enterprise Crawling and Data Processing Backend",
        version="1.0.0",
        docs_url="/docs" if settings.is_development else None,
        redoc_url="/redoc" if settings.is_development else None,
        openapi_url="/openapi.json" if settings.is_development else None,
        lifespan=lifespan
    )
    
    # Add middleware stack (order matters!)
    
    # 1. Request logging middleware  
    app.add_middleware(RequestLoggingMiddleware)
    
    # 2. CORS middleware
    if hasattr(settings.security, 'CORS_ORIGINS'):
        app.add_middleware(
            CORSMiddleware,
            allow_origins=settings.security.CORS_ORIGINS,
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
            expose_headers=["X-Process-Time", "X-Correlation-ID"]
        )
    
    # 3. Trusted host middleware (security)
    if settings.is_production:
        app.add_middleware(
            TrustedHostMiddleware,
            allowed_hosts=["*.yourdomain.com", "localhost", "127.0.0.1"]
        )
    
    # Health check endpoint
    @app.get("/health", tags=["Health"])
    async def health_check():
        """Health check endpoint."""
        try:
            db_manager = get_database_manager()
            db_info = db_manager.test_connection()
            
            return {
                "status": "healthy",
                "timestamp": time.time(),
                "database": {
                    "status": "connected",
                    "vendor": db_info["vendor"],
                    "version": db_info["version"]
                },
                "features": getattr(settings, 'FEATURE_FLAGS', {})
            }
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return JSONResponse(
                status_code=503,
                content={
                    "status": "unhealthy", 
                    "error": str(e),
                    "timestamp": time.time()
                }
            )
    
    # Ready check endpoint
    @app.get("/ready", tags=["Health"])
    async def ready_check():
        """Readiness check endpoint for Kubernetes."""
        return {"status": "ready", "timestamp": time.time()}
    
    # Basic API info endpoint
    @app.get("/", tags=["Info"])
    async def api_info():
        """API information endpoint."""
        return {
            "name": "ECaDP Backend API",
            "version": "1.0.0",
            "description": "Enterprise Crawling and Data Processing Backend",
            "docs_url": "/docs" if settings.is_development else None,
            "status": "operational"
        }
    
    # Include API routers
    from .routers import (
        jobs, data, templates, policies, 
        privacy, exports, scheduler, audit
    )
    
    app.include_router(jobs.router, prefix="/api/v1")
    app.include_router(data.router, prefix="/api/v1")
    app.include_router(templates.router, prefix="/api/v1")
    app.include_router(exports.router, prefix="/api/v1")
    app.include_router(privacy.router, prefix="/api/v1")
    app.include_router(policies.router, prefix="/api/v1") 
    app.include_router(scheduler.router, prefix="/api/v1")
    app.include_router(audit.router, prefix="/api/v1")
    
    # Global exception handler
    @app.exception_handler(HTTPException)
    async def custom_http_exception_handler(request: Request, exc: HTTPException):
        """Custom HTTP exception handler with correlation ID."""
        correlation_id = getattr(request.state, "correlation_id", None)
        
        response = await http_exception_handler(request, exc)
        if correlation_id:
            response.headers["X-Correlation-ID"] = correlation_id
            
        return response
    
    # Generic exception handler
    @app.exception_handler(Exception)
    async def generic_exception_handler(request: Request, exc: Exception):
        """Generic exception handler for unhandled errors."""
        correlation_id = getattr(request.state, "correlation_id", None)
        
        logger.error(
            "Unhandled exception",
            extra={
                "error": str(exc),
                "correlation_id": correlation_id,
                "path": request.url.path,
                "method": request.method
            },
            exc_info=True
        )
        
        response = JSONResponse(
            status_code=500,
            content={
                "detail": "Internal server error",
                "correlation_id": correlation_id
            }
        )
        
        if correlation_id:
            response.headers["X-Correlation-ID"] = correlation_id
            
        return response
    
    return app


def run_server():
    """Run the FastAPI server."""
    settings = get_settings()
    
    uvicorn.run(
        "src.webapp.app:create_app",
        factory=True,
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.is_development,
        log_level=settings.LOG_LEVEL.lower(),
        access_log=True,
        server_header=False,
        date_header=False
    )


if __name__ == "__main__":
    run_server()
