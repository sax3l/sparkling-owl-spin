#!/usr/bin/env python3
"""
Core Utils Helpers - Consolidated utility functions

This file consolidates helper functions and logging utilities:
- Originally from utils/helpers.py + utils/logger.py
- Common utility functions used across the pyramid
- Logging configuration and management
- File operations and data validation
"""

import os
import sys
import logging
import json
import yaml
from pathlib import Path
from typing import Dict, List, Any, Optional, Union
from datetime import datetime
import hashlib
import uuid

# Re-export shared utilities for backwards compatibility
from shared.utils.helpers import *

# Additional core-specific utilities
def setup_core_logging(service_name: str = "core", level: str = "INFO") -> logging.Logger:
    """Setup logging specifically for core services"""
    
    # Create logs directory if it doesn't exist
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    # Configure logging with both file and console handlers
    log_file = log_dir / f"{service_name}.log"
    
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    logger = logging.getLogger(service_name)
    logger.info(f"✅ Core logging initialized for {service_name}")
    
    return logger


def load_core_config(config_path: Optional[Path] = None) -> Dict[str, Any]:
    """Load core configuration with fallbacks"""
    
    if config_path is None:
        config_path = Path("config/services.yaml")
    
    try:
        if config_path.exists():
            return load_config(config_path)
        else:
            # Return default configuration
            return {
                'core': {
                    'orchestration': {
                        'host': '0.0.0.0',
                        'port': 8000,
                        'workers': 1
                    },
                    'logging': {
                        'level': 'INFO',
                        'format': 'standard'
                    }
                },
                'engines': {
                    'scraping': {'enabled': True},
                    'bypass': {'enabled': True},
                    'pentesting': {'enabled': False}
                },
                'agents': {
                    'crew': {'enabled': True}
                }
            }
    except Exception as e:
        get_logger(__name__).error(f"Failed to load core config: {e}")
        return {}


def validate_core_environment() -> bool:
    """Validate that core environment is properly set up"""
    
    required_dirs = [
        "core", "shared", "engines", "agents", 
        "processing", "api", "config", "logs"
    ]
    
    missing_dirs = []
    for dir_name in required_dirs:
        if not Path(dir_name).exists():
            missing_dirs.append(dir_name)
    
    if missing_dirs:
        logger = get_logger(__name__)
        logger.error(f"Missing required directories: {missing_dirs}")
        return False
    
    return True


def get_core_version() -> str:
    """Get core system version"""
    
    version_file = Path("VERSION")
    if version_file.exists():
        return version_file.read_text().strip()
    else:
        return "1.0.0"


def create_service_id(service_type: str, instance_id: Optional[str] = None) -> str:
    """Create standardized service ID"""
    
    if instance_id:
        return f"{service_type}_{instance_id}"
    else:
        return f"{service_type}_{generate_short_id()}"


def format_service_status(service_id: str, status: str, message: str = "") -> Dict[str, Any]:
    """Format service status for consistent reporting"""
    
    return {
        "service_id": service_id,
        "status": status,
        "message": message,
        "timestamp": datetime.now().isoformat(),
        "version": get_core_version()
    }


def merge_service_configs(*configs: Dict[str, Any]) -> Dict[str, Any]:
    """Merge multiple service configurations with conflict resolution"""
    
    result = {}
    
    for config in configs:
        if not isinstance(config, dict):
            continue
        
        for key, value in config.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = merge_service_configs(result[key], value)
            else:
                result[key] = value
    
    return result


def validate_service_config(config: Dict[str, Any], required_keys: List[str]) -> bool:
    """Validate service configuration has required keys"""
    
    for key in required_keys:
        if '.' in key:
            # Handle nested keys
            parts = key.split('.')
            current = config
            
            for part in parts:
                if not isinstance(current, dict) or part not in current:
                    return False
                current = current[part]
        else:
            if key not in config:
                return False
    
    return True


def create_error_response(error: Exception, service_id: str = "unknown") -> Dict[str, Any]:
    """Create standardized error response"""
    
    return {
        "success": False,
        "error": {
            "type": type(error).__name__,
            "message": str(error),
            "service_id": service_id,
            "timestamp": datetime.now().isoformat()
        }
    }


def create_success_response(data: Any = None, service_id: str = "unknown") -> Dict[str, Any]:
    """Create standardized success response"""
    
    response = {
        "success": True,
        "service_id": service_id,
        "timestamp": datetime.now().isoformat()
    }
    
    if data is not None:
        response["data"] = data
    
    return response


# Legacy compatibility functions (from old utils/logger.py)
def get_colored_logger(name: str) -> logging.Logger:
    """Get colored logger (legacy compatibility)"""
    return get_logger(name)


def log_service_start(service_name: str) -> None:
    """Log service startup (legacy compatibility)"""
    logger = get_logger(service_name)
    logger.info(f"🚀 Starting {service_name} service")


def log_service_stop(service_name: str) -> None:
    """Log service shutdown (legacy compatibility)"""
    logger = get_logger(service_name)
    logger.info(f"🛑 Stopping {service_name} service")


# Export all utilities
__all__ = [
    # From shared.utils.helpers
    'setup_logging', 'get_logger', 'load_config', 'save_config', 
    'merge_configs', 'get_env_var', 'make_http_request', 'sanitize_url',
    'validate_email', 'validate_url', 'ensure_directory', 'generate_uuid',
    
    # Core-specific utilities
    'setup_core_logging', 'load_core_config', 'validate_core_environment',
    'get_core_version', 'create_service_id', 'format_service_status',
    'merge_service_configs', 'validate_service_config', 'create_error_response',
    'create_success_response',
    
    # Legacy compatibility
    'get_colored_logger', 'log_service_start', 'log_service_stop'
]
