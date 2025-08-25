#!/usr/bin/env python3
"""
Core Orchestrator - Main application entry point for the pyramid-structured crawler platform.

This orchestrator manages all services in the pyramid architecture:
- Engines (bypass, scraping, pentesting)
- Agents (crew-based AI specialists)  
- Processing (data transformation)
- Integrations (Swedish market specific)
- Shared utilities and models

Provides unified interface for:
- Web API (FastAPI)
- Service management
- Health monitoring
- Configuration management
"""

import asyncio
import logging
import signal
import sys
import os
from contextlib import asynccontextmanager
from typing import Dict, Any, Optional
import uvicorn
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Import shared models and utilities
from shared.models.base import ServiceStatus, BaseService, ServiceHealthCheck
from shared.utils.helpers import setup_logging, get_logger, load_config
from core.utils.orchestration import ServiceOrchestrator, ServiceRegistry, ServiceHealthChecker
from core.utils.config_manager import ConfigManager
# Global orchestrator instance
orchestrator = None
config_manager = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan management"""
    global orchestrator, config_manager
    
    try:
        # Setup logging
        setup_logging(level="INFO")
        logger = get_logger(__name__)
        logger.info("🚀 Starting Pyramid Architecture Orchestrator")
        
        # Initialize configuration manager
        config_manager = ConfigManager()
        logger.info("✅ Configuration manager initialized")
        
        # Initialize service components
        registry = ServiceRegistry()
        health_checker = ServiceHealthChecker()
        orchestrator = ServiceOrchestrator(registry, health_checker)
        
        # Register available services (mock services for now)
        await _register_services(registry)
        
        # Start orchestrator
        await orchestrator.startup()
        logger.info("✅ Orchestrator started successfully")
        
        # Store in app state for access in routes
        app.state.orchestrator = orchestrator
        app.state.config_manager = config_manager
        
        yield
        
    except Exception as e:
        logger.error(f"❌ Failed to start orchestrator: {e}")
        raise
    
    finally:
        # Cleanup
        if orchestrator:
            logger.info("🛑 Shutting down orchestrator...")
            await orchestrator.shutdown()
            logger.info("✅ Orchestrator shutdown complete")

async def _register_services(registry: ServiceRegistry):
    """Register all pyramid services"""
    logger = get_logger(__name__)
    
    # Mock services for demonstration
    # In a real implementation, these would be actual service instances
    
    class MockScrapingEngine(BaseService):
        def __init__(self):
            super().__init__("scraping_engine", "Web Scraping Engine")
        
        async def start(self):
            self.status = ServiceStatus.RUNNING
            logger.info("Scraping engine started")
        
        async def stop(self):
            self.status = ServiceStatus.STOPPED
            logger.info("Scraping engine stopped")
        
        async def health_check(self):
            return ServiceHealthCheck(
                service_id=self.service_id,
                status="healthy",
                message="Scraping engine is operational",
                timestamp=asyncio.get_event_loop().time()
            )
    
    class MockPentestingEngine(BaseService):
        def __init__(self):
            super().__init__("pentesting_engine", "Pentesting Engine")
        
        async def start(self):
            self.status = ServiceStatus.RUNNING
            logger.info("Pentesting engine started")
        
        async def stop(self):
            self.status = ServiceStatus.STOPPED
            logger.info("Pentesting engine stopped")
        
        async def health_check(self):
            return ServiceHealthCheck(
                service_id=self.service_id,
                status="healthy",
                message="Pentesting engine is operational",
                timestamp=asyncio.get_event_loop().time()
            )
    
    class MockCrewAgent(BaseService):
        def __init__(self):
            super().__init__("crew_agent", "AI Crew Agent")
        
        async def start(self):
            self.status = ServiceStatus.RUNNING
            logger.info("Crew agent started")
        
        async def stop(self):
            self.status = ServiceStatus.STOPPED
            logger.info("Crew agent stopped")
        
        async def health_check(self):
            return ServiceHealthCheck(
                service_id=self.service_id,
                status="healthy",
                message="Crew agent is operational",
                timestamp=asyncio.get_event_loop().time()
            )
    
    # Register services
    registry.register_service(
        MockScrapingEngine(),
        dependencies=[],
        metadata={"layer": "engines", "type": "scraping"}
    )
    
    registry.register_service(
        MockPentestingEngine(), 
        dependencies=[],
        metadata={"layer": "engines", "type": "pentesting"}
    )
    
    registry.register_service(
        MockCrewAgent(),
        dependencies=["scraping_engine"],  # Depends on scraping engine
        metadata={"layer": "agents", "type": "crew"}
    )
    
    logger.info(f"Registered {len(registry.list_services())} services")

# Create FastAPI app
app = FastAPI(
    title="Pyramid Architecture Orchestrator",
    description="Centralized orchestrator for the pyramid-structured crawler platform",
    version="1.0.0",
    lifespan=lifespan
)
    """Main orchestrator for the pyramid architecture system"""
    
    def __init__(self):
        self.app: Optional[FastAPI] = None
        self.services: Dict[str, Any] = {}
        self.health_status: Dict[str, ServiceStatus] = {}
        
        # Initialize service registry
        self._initialize_service_registry()
    
    def _initialize_service_registry(self):
        """Initialize all services in the pyramid"""
        
        # Register engines
        self.services['cloudflare_bypass'] = CloudflareBypass()
        self.services['waf_bypass'] = WAFBypass()
        self.services['web_scraper'] = WebScraper()
        self.services['vulnerability_scanner'] = VulnerabilityScanner()
        
        # Register AI agents
        self.services['scraping_specialist'] = ScrapingSpecialistAgent()
        self.services['security_analyst'] = SecurityAnalystAgent()
        self.services['data_scientist'] = DataScientistAgent()
        
        # Register processing modules
        self.services['content_extractor'] = ContentExtractor()
        self.services['data_transformer'] = DataTransformer()
        
        # Register Swedish integrations
        self.services['blocket_api'] = BlocketAPI()
        self.services['vehicle_data_api'] = VehicleDataAPI()
        
        logger.info(f"Registered {len(self.services)} services in pyramid architecture")
    
    @asynccontextmanager
    async def lifespan(self, app: FastAPI):
        """Application lifespan manager"""
        # Startup
        logger.info("🚀 Starting Core Orchestrator...")
        await self._startup_services()
        
        yield
        
        # Shutdown
        logger.info("🛑 Shutting down Core Orchestrator...")
        await self._shutdown_services()
    
    async def _startup_services(self):
        """Initialize all services"""
        startup_tasks = []
        
        for service_name, service in self.services.items():
            if hasattr(service, 'initialize'):
                task = asyncio.create_task(
                    self._safe_service_startup(service_name, service)
                )
                startup_tasks.append(task)
        
        # Wait for all services to start
        if startup_tasks:
            await asyncio.gather(*startup_tasks, return_exceptions=True)
        
        logger.info("✅ All services initialized")
    
    async def _safe_service_startup(self, service_name: str, service: Any):
        """Safely start a service with error handling"""
        try:
            if hasattr(service, 'initialize'):
                await service.initialize()
            self.health_status[service_name] = ServiceStatus.HEALTHY
            logger.info(f"✅ Service '{service_name}' started successfully")
        except Exception as e:
            logger.error(f"❌ Failed to start service '{service_name}': {e}")
            self.health_status[service_name] = ServiceStatus.UNHEALTHY
    
    async def _shutdown_services(self):
        """Shutdown all services gracefully"""
        shutdown_tasks = []
        
        for service_name, service in self.services.items():
            if hasattr(service, 'cleanup'):
                task = asyncio.create_task(
                    self._safe_service_shutdown(service_name, service)
                )
                shutdown_tasks.append(task)
        
        if shutdown_tasks:
            await asyncio.gather(*shutdown_tasks, return_exceptions=True)
        
        logger.info("✅ All services shut down")
    
    async def _safe_service_shutdown(self, service_name: str, service: Any):
        """Safely shutdown a service"""
        try:
            if hasattr(service, 'cleanup'):
                await service.cleanup()
            logger.info(f"✅ Service '{service_name}' shut down successfully")
        except Exception as e:
            logger.error(f"❌ Error shutting down service '{service_name}': {e}")
    
    def create_app(self) -> FastAPI:
        """Create FastAPI application with pyramid architecture"""
        
        app = FastAPI(
            title="Pyramid Crawler Platform",
            description="Advanced multi-layer crawling and analysis platform",
            version="2.0.0",
            lifespan=self.lifespan
        )
        
        # Add CORS middleware
        app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],  # Configure appropriately for production
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        
        # Register routes
        self._register_routes(app)
        
        self.app = app
        return app
    
    def _register_routes(self, app: FastAPI):
        """Register all API routes"""
        
        @app.get("/health")
        async def health_check():
            """System health check"""
            overall_health = SystemHealth.HEALTHY
            
            if any(status == ServiceStatus.UNHEALTHY 
                  for status in self.health_status.values()):
                overall_health = SystemHealth.DEGRADED
            
            return {
                "status": overall_health.value,
                "services": {
                    name: status.value 
                    for name, status in self.health_status.items()
                },
                "total_services": len(self.services),
                "healthy_services": sum(
                    1 for s in self.health_status.values() 
                    if s == ServiceStatus.HEALTHY
                )
            }
        
        @app.get("/services")
        async def list_services():
            """List all registered services"""
            return {
                "services": list(self.services.keys()),
                "count": len(self.services),
                "pyramid_layers": {
                    "engines": ["cloudflare_bypass", "waf_bypass", "web_scraper", "vulnerability_scanner"],
                    "agents": ["scraping_specialist", "security_analyst", "data_scientist"],
                    "processing": ["content_extractor", "data_transformer"],
                    "integrations": ["blocket_api", "vehicle_data_api"]
                }
            }
        
        @app.post("/orchestrate/scraping-task")
        async def orchestrate_scraping_task(request: Dict[str, Any]):
            """Orchestrate a complete scraping task through all pyramid layers"""
            try:
                # 1. Use scraping specialist to analyze target
                specialist = self.services['scraping_specialist']
                analysis = await specialist.analyze_target(request.get('url'))
                
                # 2. Execute scraping with recommended strategy
                task_request = {
                    'target_url': request.get('url'),
                    'strategy': analysis.get('suggested_strategy'),
                    'selectors': request.get('selectors', {})
                }
                
                # 3. Process extracted data
                extractor = self.services['content_extractor']
                transformer = self.services['data_transformer']
                
                # 4. Return orchestrated results
                return {
                    "success": True,
                    "analysis": analysis,
                    "task_request": task_request,
                    "orchestration_layers": ["analysis", "extraction", "transformation"]
                }
                
            except Exception as e:
                logger.error(f"Orchestration failed: {e}")
                return {
                    "success": False,
                    "error": str(e)
                }
        
        @app.post("/orchestrate/security-analysis")
        async def orchestrate_security_analysis(request: Dict[str, Any]):
            """Orchestrate a complete security analysis"""
            try:
                # Use security analyst
                analyst = self.services['security_analyst']
                
                # Create security target
                target = {
                    'target_url': request.get('url'),
                    'analysis_type': request.get('analysis_type', 'vulnerability_assessment')
                }
                
                return {
                    "success": True,
                    "message": "Security analysis orchestrated",
                    "target": target
                }
                
            except Exception as e:
                logger.error(f"Security orchestration failed: {e}")
                return {
                    "success": False,
                    "error": str(e)
                }

# Global orchestrator instance
orchestrator = CoreOrchestrator()

def create_app() -> FastAPI:
    """Create application instance"""
    return orchestrator.create_app()

def setup_signal_handlers():
    """Setup signal handlers for graceful shutdown"""
    def signal_handler(signum, frame):
        logger.info(f"Received signal {signum}, initiating graceful shutdown...")
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

def main():
    """Main entry point"""
    # Setup logging
    setup_logging(level=logging.INFO)
    
    # Setup signal handlers
    setup_signal_handlers()
    
    # Create application
    app = create_app()
    
    # Run server
    logger.info("🚀 Starting Pyramid Crawler Platform...")
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        reload=False,  # Disable in production
        log_level="info"
    )

if __name__ == "__main__":
    main()
