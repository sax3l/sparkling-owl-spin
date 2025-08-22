"""
Lovable Backend App Factory

Creates and configures the FastAPI application instance.
"""

from fastapi import FastAPI
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware

from .api import api_router
from .auth import auth_router
from .settings import get_settings


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    settings = get_settings()
    
    app = FastAPI(
        title="Lovable Backend API",
        description="Backend API for the Lovable platform",
        version="1.0.0",
        docs_url="/docs" if settings.debug else None,
        redoc_url="/redoc" if settings.debug else None,
        openapi_url="/openapi.json" if settings.debug else None,
    )
    
    # Add middleware
    app.add_middleware(GZipMiddleware, minimum_size=1000)
    
    if not settings.debug:
        app.add_middleware(
            TrustedHostMiddleware,
            allowed_hosts=["localhost", "127.0.0.1", "*.lovable.dev"]
        )
    
    # Include routers
    app.include_router(auth_router, prefix="/auth", tags=["authentication"])
    app.include_router(api_router, prefix=settings.api_prefix, tags=["api"])
    
    # Health check endpoint
    @app.get("/health")
    async def health_check():
        """Health check endpoint."""
        return {"status": "healthy", "service": "lovable-backend"}
    
    # Root endpoint
    @app.get("/")
    async def root():
        """Root endpoint."""
        return {
            "message": "Welcome to Lovable Backend API",
            "version": "1.0.0",
            "docs_url": "/docs" if settings.debug else None
        }
    
    return app
