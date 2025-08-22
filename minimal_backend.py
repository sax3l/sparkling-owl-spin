"""
Minimal Backend Entry Point

En minimal FastAPI backend-app som är oberoende av det befintliga systemet.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime
from typing import Dict, Any
import uvicorn


class HealthResponse(BaseModel):
    status: str
    timestamp: str
    service: str
    version: str


def create_minimal_app() -> FastAPI:
    """Skapa en minimal FastAPI-app för backend."""
    
    app = FastAPI(
        title="Lovable Backend API",
        description="Backend API för Lovable-projektet",
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc"
    )
    
    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # I produktion, specificera exakta origins
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    @app.get("/")
    async def root():
        """Root endpoint."""
        return {"message": "Lovable Backend API is running", "status": "ok"}
    
    @app.get("/health", response_model=HealthResponse)
    async def health_check():
        """Health check endpoint."""
        return HealthResponse(
            status="healthy",
            timestamp=datetime.now().isoformat(),
            service="lovable-backend", 
            version="1.0.0"
        )
    
    @app.get("/api/v1/info")
    async def api_info():
        """API information endpoint."""
        return {
            "api_version": "v1",
            "service": "lovable-backend",
            "endpoints": {
                "root": "/",
                "health": "/health", 
                "docs": "/docs",
                "redoc": "/redoc"
            }
        }
    
    return app


def main():
    """Starta backend-servern."""
    app = create_minimal_app()
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info",
        reload=True,
        access_log=True
    )


if __name__ == "__main__":
    main()
