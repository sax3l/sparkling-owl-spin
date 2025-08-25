#!/usr/bin/env python3
"""
API Server Consolidation - Unified API server
Consolidates api/server.py + api/main.py + api/app.py → api/rest/server.py  
As specified in Swedish reorganization instructions
"""

import asyncio
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional
import uvicorn
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from shared.models.base import BaseService, ServiceStatus, ServiceHealthCheck
from shared.utils.helpers import get_logger, load_configuration
from core.orchestrator import PyramidOrchestrator


class APIServer(BaseService):
    """Unified FastAPI server with all API endpoints"""
    
    def __init__(self, config_path: Optional[str] = None):
        super().__init__("api_server", "FastAPI REST API Server")
        
        self.logger = get_logger(__name__)
        self.config = load_configuration(config_path)
        self.app: Optional[FastAPI] = None
        self.orchestrator: Optional[PyramidOrchestrator] = None
        self.server_task: Optional[asyncio.Task] = None
        
        # API configuration
        self.api_config = self.config.get("api", {}).get("rest", {})
        self.server_config = self.api_config.get("server", {})
        
        self.host = self.server_config.get("host", "0.0.0.0")
        self.port = self.server_config.get("port", 8000)
        self.workers = self.server_config.get("workers", 1)
        self.reload = self.server_config.get("reload", False)
        
    async def start(self) -> None:
        """Start the API server"""
        self.status = ServiceStatus.STARTING
        self.logger.info("Starting API Server...")
        
        try:
            # Initialize FastAPI app
            await self._create_app()
            
            # Start orchestrator
            if not self.orchestrator:
                self.orchestrator = PyramidOrchestrator()
                await self.orchestrator.start()
            
            # Start server in background task
            config = uvicorn.Config(
                app=self.app,
                host=self.host,
                port=self.port,
                workers=self.workers,
                reload=self.reload,
                log_level="info"
            )
            server = uvicorn.Server(config)
            
            # Run server in background
            self.server_task = asyncio.create_task(server.serve())
            
            self.status = ServiceStatus.RUNNING
            self.logger.info(f"✅ API Server started on http://{self.host}:{self.port}")
            
        except Exception as e:
            self.status = ServiceStatus.ERROR
            self.logger.error(f"❌ Failed to start API Server: {e}")
            raise
    
    async def stop(self) -> None:
        """Stop the API server"""
        self.status = ServiceStatus.STOPPING
        self.logger.info("Stopping API Server...")
        
        try:
            # Stop server task
            if self.server_task and not self.server_task.done():
                self.server_task.cancel()
                try:
                    await self.server_task
                except asyncio.CancelledError:
                    pass
            
            # Stop orchestrator
            if self.orchestrator:
                await self.orchestrator.stop()
            
            self.status = ServiceStatus.STOPPED
            self.logger.info("✅ API Server stopped")
            
        except Exception as e:
            self.status = ServiceStatus.ERROR
            self.logger.error(f"❌ Failed to stop API Server: {e}")
    
    async def _create_app(self) -> None:
        """Create and configure FastAPI application"""
        
        # Create lifespan context manager
        @asynccontextmanager
        async def lifespan(app: FastAPI):
            # Startup
            self.logger.info("FastAPI application starting up...")
            yield
            # Shutdown
            self.logger.info("FastAPI application shutting down...")
        
        # Create FastAPI app
        self.app = FastAPI(
            title="Sparkling Owl Spin API",
            description="Unified API for web scraping and data processing",
            version="2.0.0",
            lifespan=lifespan,
            docs_url="/docs",
            redoc_url="/redoc",
            openapi_url="/openapi.json"
        )
        
        # Add middleware
        await self._setup_middleware()
        
        # Add routes
        await self._setup_routes()
        
        # Add exception handlers
        await self._setup_exception_handlers()
    
    async def _setup_middleware(self) -> None:
        """Setup FastAPI middleware"""
        
        # CORS middleware
        cors_config = self.api_config.get("cors", {})
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=cors_config.get("allow_origins", ["*"]),
            allow_credentials=cors_config.get("allow_credentials", True),
            allow_methods=cors_config.get("allow_methods", ["*"]),
            allow_headers=cors_config.get("allow_headers", ["*"]),
        )
        
        # Gzip compression
        self.app.add_middleware(GZipMiddleware, minimum_size=1000)
        
        self.logger.info("✅ Middleware configured")
    
    async def _setup_routes(self) -> None:
        """Setup API routes"""
        
        # Health check endpoints
        @self.app.get("/health")
        async def health_check():
            """Basic health check"""
            return {
                "status": "healthy",
                "service": self.service_id,
                "timestamp": datetime.now().isoformat(),
                "version": "2.0.0"
            }
        
        @self.app.get("/health/detailed")
        async def detailed_health_check():
            """Detailed health check with service status"""
            if not self.orchestrator:
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail="Orchestrator not available"
                )
            
            health_checks = await self.orchestrator.get_all_health_checks()
            
            return {
                "status": "healthy" if all(hc.status == "healthy" for hc in health_checks) else "degraded",
                "timestamp": datetime.now().isoformat(),
                "services": [
                    {
                        "service_id": hc.service_id,
                        "status": hc.status,
                        "message": hc.message,
                        "last_check": hc.timestamp.isoformat()
                    }
                    for hc in health_checks
                ]
            }
        
        # Service management endpoints
        @self.app.get("/services")
        async def list_services():
            """List all registered services"""
            if not self.orchestrator:
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail="Orchestrator not available"
                )
            
            services = await self.orchestrator.registry.get_all_services()
            return {
                "services": [
                    {
                        "service_id": service.service_id,
                        "name": service.name,
                        "status": service.status.value,
                        "registered_at": service.registered_at.isoformat()
                    }
                    for service in services
                ]
            }
        
        @self.app.get("/services/{service_id}/status")
        async def get_service_status(service_id: str):
            """Get status of a specific service"""
            if not self.orchestrator:
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail="Orchestrator not available"
                )
            
            service = await self.orchestrator.registry.get_service(service_id)
            if not service:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Service {service_id} not found"
                )
            
            return {
                "service_id": service.service_id,
                "name": service.name,
                "status": service.status.value,
                "registered_at": service.registered_at.isoformat()
            }
        
        # Scraping endpoints
        @self.app.post("/scrape/url")
        async def scrape_single_url(request: dict):
            """Scrape a single URL"""
            if not self.orchestrator:
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail="Orchestrator not available"
                )
            
            url = request.get("url")
            if not url:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="URL is required"
                )
            
            # Get web scraper service
            scraper = await self.orchestrator.registry.get_service("web_scraper")
            if not scraper:
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail="Web scraper service not available"
                )
            
            # Create scraping task
            from engines.scraping.web_scraper import ScrapingTask, ScrapingBackend
            
            task = ScrapingTask(
                url=url,
                backend=ScrapingBackend(request.get("backend", "requests")),
                extraction_rules=request.get("extraction_rules"),
                headers=request.get("headers"),
                timeout=request.get("timeout", 30)
            )
            
            # Execute scraping
            result = await scraper.scrape(task)
            
            return {
                "success": result.success,
                "url": result.url,
                "status_code": result.status_code,
                "content_preview": result.content[:500] if result.content else None,
                "extracted_data": result.extracted_data,
                "metadata": result.metadata,
                "error": result.error,
                "timestamp": result.timestamp.isoformat()
            }
        
        @self.app.post("/scrape/batch")
        async def scrape_multiple_urls(request: dict):
            """Scrape multiple URLs"""
            if not self.orchestrator:
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail="Orchestrator not available"
                )
            
            urls = request.get("urls", [])
            if not urls:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="URLs list is required"
                )
            
            # Get web scraper service
            scraper = await self.orchestrator.registry.get_service("web_scraper")
            if not scraper:
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail="Web scraper service not available"
                )
            
            # Create scraping tasks
            from engines.scraping.web_scraper import ScrapingTask, ScrapingBackend
            
            tasks = []
            for url_config in urls:
                if isinstance(url_config, str):
                    url_config = {"url": url_config}
                
                task = ScrapingTask(
                    url=url_config["url"],
                    backend=ScrapingBackend(url_config.get("backend", "requests")),
                    extraction_rules=url_config.get("extraction_rules"),
                    headers=url_config.get("headers"),
                    timeout=url_config.get("timeout", 30)
                )
                tasks.append(task)
            
            # Execute batch scraping
            results = await scraper.scrape_multiple(tasks)
            
            return {
                "total": len(results),
                "successful": sum(1 for r in results if r.success),
                "failed": sum(1 for r in results if not r.success),
                "results": [
                    {
                        "success": result.success,
                        "url": result.url,
                        "status_code": result.status_code,
                        "content_preview": result.content[:200] if result.content else None,
                        "extracted_data": result.extracted_data,
                        "metadata": result.metadata,
                        "error": result.error,
                        "timestamp": result.timestamp.isoformat()
                    }
                    for result in results
                ]
            }
        
        # Statistics endpoints
        @self.app.get("/stats/system")
        async def get_system_stats():
            """Get system statistics"""
            if not self.orchestrator:
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail="Orchestrator not available"
                )
            
            stats = await self.orchestrator.get_system_statistics()
            return stats
        
        @self.app.get("/stats/scraper")
        async def get_scraper_stats():
            """Get scraper statistics"""
            if not self.orchestrator:
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail="Orchestrator not available"
                )
            
            scraper = await self.orchestrator.registry.get_service("web_scraper")
            if not scraper:
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail="Web scraper service not available"
                )
            
            stats = scraper.get_statistics()
            return stats
        
        self.logger.info("✅ API routes configured")
    
    async def _setup_exception_handlers(self) -> None:
        """Setup exception handlers"""
        
        @self.app.exception_handler(HTTPException)
        async def http_exception_handler(request, exc: HTTPException):
            return JSONResponse(
                status_code=exc.status_code,
                content={
                    "error": True,
                    "message": exc.detail,
                    "status_code": exc.status_code,
                    "timestamp": datetime.now().isoformat()
                }
            )
        
        @self.app.exception_handler(RequestValidationError)
        async def validation_exception_handler(request, exc: RequestValidationError):
            return JSONResponse(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                content={
                    "error": True,
                    "message": "Validation error",
                    "details": exc.errors(),
                    "timestamp": datetime.now().isoformat()
                }
            )
        
        @self.app.exception_handler(Exception)
        async def general_exception_handler(request, exc: Exception):
            self.logger.error(f"Unhandled exception: {exc}", exc_info=True)
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={
                    "error": True,
                    "message": "Internal server error",
                    "timestamp": datetime.now().isoformat()
                }
            )
        
        self.logger.info("✅ Exception handlers configured")
    
    async def health_check(self) -> ServiceHealthCheck:
        """Service health check"""
        try:
            # Check if app is created and orchestrator is running
            if not self.app:
                status_val = "unhealthy"
                message = "FastAPI app not initialized"
            elif not self.orchestrator or self.orchestrator.status != ServiceStatus.RUNNING:
                status_val = "degraded"
                message = "Orchestrator not running"
            elif self.status != ServiceStatus.RUNNING:
                status_val = "degraded"
                message = f"Service status: {self.status.value}"
            else:
                status_val = "healthy"
                message = "API server is operational"
            
            return ServiceHealthCheck(
                service_id=self.service_id,
                status=status_val,
                message=message,
                timestamp=datetime.now(),
                details={
                    "host": self.host,
                    "port": self.port,
                    "orchestrator_status": self.orchestrator.status.value if self.orchestrator else "none"
                }
            )
            
        except Exception as e:
            return ServiceHealthCheck(
                service_id=self.service_id,
                status="unhealthy",
                message=f"Health check failed: {str(e)}",
                timestamp=datetime.now()
            )


# Standalone server function
async def run_server():
    """Run the API server standalone"""
    server = APIServer()
    
    try:
        await server.start()
        
        # Keep running until interrupted
        while server.status == ServiceStatus.RUNNING:
            await asyncio.sleep(1)
            
    except KeyboardInterrupt:
        print("\n🛑 Server interrupted by user")
    except Exception as e:
        print(f"❌ Server error: {e}")
    finally:
        await server.stop()


if __name__ == "__main__":
    asyncio.run(run_server())
