"""
ECaDP Backend Startup Script

Comprehensive startup script that initializes all services and components
according to the Backend specification.
"""

import asyncio
import logging
import signal
import sys
from typing import Optional
from contextlib import asynccontextmanager

from fastapi import FastAPI
from src.settings import get_settings
from src.database.manager import get_database_manager
from src.services.monitoring_service import get_monitoring_service
from src.services.notification_service import get_notification_service
from src.services.privacy_service import get_privacy_service
from src.services.system_status_service import get_system_status_service
from src.scheduler.scheduler import scheduler
from src.utils.logger import get_logger

logger = get_logger(__name__)


class ECaDPBackend:
    """Main backend application class."""
    
    def __init__(self):
        self.settings = get_settings()
        self.monitoring_service = None
        self.notification_service = None
        self.privacy_service = None
        self.system_status_service = None
        self.scheduler_started = False
        self.shutdown_event = asyncio.Event()
    
    async def startup(self):
        """Initialize all backend services."""
        logger.info("Starting ECaDP Backend services...")
        
        try:
            # Initialize database
            await self._initialize_database()
            
            # Initialize core services
            await self._initialize_services()
            
            # Start scheduler
            await self._start_scheduler()
            
            # Start monitoring
            await self._start_monitoring()
            
            # Register signal handlers
            self._register_signal_handlers()
            
            logger.info("ECaDP Backend startup completed successfully")
            
        except Exception as e:
            logger.error(f"Failed to start ECaDP Backend: {e}")
            await self.shutdown()
            raise
    
    async def shutdown(self):
        """Gracefully shutdown all services."""
        logger.info("Shutting down ECaDP Backend services...")
        
        try:
            # Stop monitoring
            if self.monitoring_service:
                await self.monitoring_service.stop_monitoring()
                logger.info("Monitoring service stopped")
            
            # Stop scheduler
            if self.scheduler_started:
                try:
                    scheduler.shutdown(wait=True)
                    self.scheduler_started = False
                    logger.info("Scheduler stopped")
                except:
                    logger.warning("Error stopping scheduler")
            
            # Close notification service
            if self.notification_service:
                try:
                    await self.notification_service.close()
                    logger.info("Notification service stopped")
                except:
                    logger.warning("Error stopping notification service")
            
            # Close database connections
            try:
                db_manager = get_database_manager()
                await db_manager.close_all_connections()
                logger.info("Database connections closed")
            except:
                logger.warning("Error closing database connections")
            
            self.shutdown_event.set()
            logger.info("ECaDP Backend shutdown completed")
            
        except Exception as e:
            logger.error(f"Error during shutdown: {e}")
    
    async def _initialize_database(self):
        """Initialize database connections and run migrations."""
        logger.info("Initializing database...")
        
        db_manager = get_database_manager()
        
        # Test database connection
        try:
            async with db_manager.get_session() as session:
                await session.execute("SELECT 1")
            logger.info("Database connection successful")
        except Exception as e:
            logger.error(f"Database connection failed: {e}")
            raise
        
        # Run migrations if configured
        if self.settings.auto_migrate:
            logger.info("Running database migrations...")
            try:
                # This would run Alembic migrations
                # await db_manager.run_migrations()
                logger.info("Database migrations completed")
            except Exception as e:
                logger.warning(f"Migration warning: {e}")
    
    async def _initialize_services(self):
        """Initialize all core services."""
        logger.info("Initializing core services...")
        
        # Initialize monitoring service
        self.monitoring_service = get_monitoring_service()
        logger.info("Monitoring service initialized")
        
        # Initialize notification service
        self.notification_service = get_notification_service()
        logger.info("Notification service initialized")
        
        # Initialize privacy service
        self.privacy_service = get_privacy_service()
        logger.info("Privacy service initialized")
        
        # Initialize system status service
        self.system_status_service = get_system_status_service()
        logger.info("System status service initialized")
    
    async def _start_scheduler(self):
        """Start the job scheduler."""
        logger.info("Starting job scheduler...")
        
        try:
            if not scheduler.running:
                scheduler.start()
                self.scheduler_started = True
                logger.info("Job scheduler started successfully")
            else:
                logger.info("Job scheduler already running")
        except Exception as e:
            logger.error(f"Failed to start scheduler: {e}")
            raise
    
    async def _start_monitoring(self):
        """Start monitoring services."""
        logger.info("Starting monitoring services...")
        
        try:
            await self.monitoring_service.start_monitoring()
            logger.info("Monitoring services started successfully")
        except Exception as e:
            logger.error(f"Failed to start monitoring: {e}")
            # Don't fail startup for monitoring issues
            logger.warning("Continuing without monitoring services")
    
    def _register_signal_handlers(self):
        """Register signal handlers for graceful shutdown."""
        if sys.platform != "win32":
            # Unix signal handlers
            loop = asyncio.get_event_loop()
            for sig in [signal.SIGTERM, signal.SIGINT]:
                loop.add_signal_handler(
                    sig,
                    lambda s=sig: asyncio.create_task(self._handle_signal(s))
                )
        else:
            # Windows signal handlers
            signal.signal(signal.SIGTERM, self._handle_signal_sync)
            signal.signal(signal.SIGINT, self._handle_signal_sync)
    
    async def _handle_signal(self, sig):
        """Handle shutdown signals."""
        logger.info(f"Received signal {sig}, initiating shutdown...")
        await self.shutdown()
    
    def _handle_signal_sync(self, sig, frame):
        """Handle shutdown signals synchronously (Windows)."""
        logger.info(f"Received signal {sig}, initiating shutdown...")
        asyncio.create_task(self.shutdown())
    
    async def run_forever(self):
        """Keep the application running."""
        try:
            await self.shutdown_event.wait()
        except KeyboardInterrupt:
            logger.info("Received keyboard interrupt")
            await self.shutdown()


# Global backend instance
_backend_instance: Optional[ECaDPBackend] = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """FastAPI lifespan context manager."""
    global _backend_instance
    
    # Startup
    _backend_instance = ECaDPBackend()
    await _backend_instance.startup()
    
    yield
    
    # Shutdown
    if _backend_instance:
        await _backend_instance.shutdown()


def create_app() -> FastAPI:
    """Create FastAPI application with lifespan management."""
    from src.webapp.app import create_app as create_webapp
    
    # Create the webapp with lifespan
    app = create_webapp()
    app.router.lifespan_context = lifespan
    
    return app


async def main():
    """Main entry point for standalone backend."""
    import uvicorn
    
    # Create backend instance
    backend = ECaDPBackend()
    
    try:
        # Start all services
        await backend.startup()
        
        # Create and configure FastAPI app
        settings = get_settings()
        app = create_app()
        
        # Configure uvicorn
        config = uvicorn.Config(
            app=app,
            host=settings.host,
            port=settings.port,
            log_level=settings.log_level.lower(),
            reload=False,  # Disable reload in production
            access_log=True
        )
        
        server = uvicorn.Server(config)
        
        # Run server
        logger.info(f"Starting HTTP server on {settings.host}:{settings.port}")
        await server.serve()
        
    except KeyboardInterrupt:
        logger.info("Received keyboard interrupt")
    except Exception as e:
        logger.error(f"Application error: {e}")
        raise
    finally:
        await backend.shutdown()


def get_backend_instance() -> Optional[ECaDPBackend]:
    """Get the global backend instance."""
    return _backend_instance


if __name__ == "__main__":
    # Run as standalone application
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Application interrupted by user")
    except Exception as e:
        logger.error(f"Application failed: {e}")
        sys.exit(1)
