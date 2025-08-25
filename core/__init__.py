#!/usr/bin/env python3
"""
Core Package för Sparkling-Owl-Spin
Pyramid Architecture Core Layer - Foundation för alla system komponenter
"""

__version__ = "1.0.0"
__author__ = "Sparkling-Owl-Spin Development Team"

# Core components
from .orchestrator import EnhancedCoreOrchestrator, orchestrator
from .config_manager import EnhancedConfigManager
from .security_controller import SecurityController
from .api_gateway import APIGateway

# Core exceptions
class SparklingOwlSpinError(Exception):
    """Base exception för Sparkling-Owl-Spin"""
    pass

class ConfigurationError(SparklingOwlSpinError):
    """Configuration related errors"""
    pass

class SecurityError(SparklingOwlSpinError):
    """Security related errors"""
    pass

class OrchestrationError(SparklingOwlSpinError):
    """Orchestration related errors"""
    pass

class APIError(SparklingOwlSpinError):
    """API related errors"""
    pass

# Core utilities
import logging
import asyncio
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

async def initialize_core_system(config_path: Optional[str] = None) -> EnhancedCoreOrchestrator:
    """
    Initialize complete core system
    
    Args:
        config_path: Optional path to configuration directory
        
    Returns:
        EnhancedCoreOrchestrator: Initialized orchestrator instance
    """
    try:
        logger.info("🎯 Initializing Sparkling-Owl-Spin Core System")
        
        # Initialize orchestrator (this will initialize all other components)
        await orchestrator.initialize()
        
        logger.info("✅ Core System Initialization Complete")
        return orchestrator
        
    except Exception as e:
        logger.error(f"❌ Core System Initialization Failed: {str(e)}")
        raise OrchestrationError(f"Failed to initialize core system: {str(e)}")

async def shutdown_core_system():
    """Shutdown complete core system"""
    try:
        logger.info("🔄 Shutting down Sparkling-Owl-Spin Core System")
        
        await orchestrator.shutdown()
        
        logger.info("✅ Core System Shutdown Complete")
        
    except Exception as e:
        logger.error(f"❌ Core System Shutdown Failed: {str(e)}")
        raise OrchestrationError(f"Failed to shutdown core system: {str(e)}")

def get_core_status() -> Dict[str, Any]:
    """Get comprehensive core system status"""
    try:
        return {
            "version": __version__,
            "orchestrator": orchestrator.get_system_status(),
            "initialized": orchestrator.initialized,
            "components": {
                "orchestrator": orchestrator.initialized,
                "config_manager": orchestrator.config_manager.initialized,
                "security_controller": orchestrator.security_controller.initialized,
                "api_gateway": orchestrator.api_gateway.initialized
            }
        }
    except Exception as e:
        return {
            "version": __version__,
            "error": str(e),
            "initialized": False
        }

# Export all core components
__all__ = [
    # Core classes
    "EnhancedCoreOrchestrator",
    "EnhancedConfigManager", 
    "SecurityController",
    "APIGateway",
    
    # Singleton instance
    "orchestrator",
    
    # Exceptions
    "SparklingOwlSpinError",
    "ConfigurationError",
    "SecurityError",
    "OrchestrationError",
    "APIError",
    
    # Utilities
    "initialize_core_system",
    "shutdown_core_system",
    "get_core_status",
    
    # Metadata
    "__version__",
    "__author__"
]
