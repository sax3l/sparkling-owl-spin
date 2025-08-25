#!/usr/bin/env python3
"""
Shared Utilities - Common utility functions for the pyramid architecture

Provides utilities used across all layers:
- Logging configuration
- Configuration management  
- HTTP utilities
- Data validation
- File operations
"""

import asyncio
import logging
import json
import yaml
import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
from datetime import datetime
import hashlib
import uuid

# Logging utilities
def setup_logging(level: Union[int, str] = logging.INFO, 
                 format_type: str = "standard",
                 log_file: Optional[str] = None) -> logging.Logger:
    """Setup logging configuration"""
    
    # Define log formats
    formats = {
        "standard": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        "detailed": "%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s",
        "json": None  # Will be handled separately
    }
    
    # Convert string level to logging constant
    if isinstance(level, str):
        level = getattr(logging, level.upper())
    
    # Create formatter
    if format_type == "json":
        # Custom JSON formatter would go here
        formatter = logging.Formatter(formats["detailed"])
    else:
        formatter = logging.Formatter(formats.get(format_type, formats["standard"]))
    
    # Setup root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    
    # Clear existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)
    
    # File handler if specified
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)
    
    return root_logger

def get_logger(name: str) -> logging.Logger:
    """Get logger instance"""
    return logging.getLogger(name)

# Configuration utilities
def load_config(config_path: Union[str, Path]) -> Dict[str, Any]:
    """Load configuration from YAML or JSON file"""
    
    config_path = Path(config_path)
    
    if not config_path.exists():
        raise FileNotFoundError(f"Configuration file not found: {config_path}")
    
    with open(config_path, 'r', encoding='utf-8') as f:
        if config_path.suffix.lower() in ['.yml', '.yaml']:
            return yaml.safe_load(f)
        elif config_path.suffix.lower() == '.json':
            return json.load(f)
        else:
            raise ValueError(f"Unsupported configuration format: {config_path.suffix}")

def save_config(config: Dict[str, Any], config_path: Union[str, Path]) -> None:
    """Save configuration to file"""
    
    config_path = Path(config_path)
    config_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(config_path, 'w', encoding='utf-8') as f:
        if config_path.suffix.lower() in ['.yml', '.yaml']:
            yaml.dump(config, f, default_flow_style=False, indent=2)
        elif config_path.suffix.lower() == '.json':
            json.dump(config, f, indent=2, ensure_ascii=False)
        else:
            raise ValueError(f"Unsupported configuration format: {config_path.suffix}")

def merge_configs(*configs: Dict[str, Any]) -> Dict[str, Any]:
    """Merge multiple configuration dictionaries"""
    result = {}
    
    for config in configs:
        for key, value in config.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = merge_configs(result[key], value)
            else:
                result[key] = value
    
    return result

def get_env_var(name: str, default: Any = None, var_type: type = str) -> Any:
    """Get environment variable with type conversion"""
    
    value = os.getenv(name, default)
    
    if value is None:
        return None
    
    # Convert to requested type
    try:
        if var_type == bool:
            return value.lower() in ('true', '1', 'yes', 'on')
        elif var_type == int:
            return int(value)
        elif var_type == float:
            return float(value)
        elif var_type == list:
            return value.split(',') if isinstance(value, str) else value
        else:
            return var_type(value)
    except (ValueError, TypeError):
        return default

# HTTP utilities
async def make_http_request(url: str, 
                          method: str = "GET",
                          headers: Optional[Dict[str, str]] = None,
                          data: Optional[Dict[str, Any]] = None,
                          timeout: int = 30,
                          retries: int = 3) -> Dict[str, Any]:
    """Make HTTP request with retries"""
    
    import aiohttp
    
    headers = headers or {}
    
    for attempt in range(retries + 1):
        try:
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=timeout)) as session:
                async with session.request(method, url, headers=headers, json=data) as response:
                    return {
                        'status': response.status,
                        'headers': dict(response.headers),
                        'data': await response.text(),
                        'success': True
                    }
        except Exception as e:
            if attempt == retries:
                return {
                    'status': 0,
                    'headers': {},
                    'data': '',
                    'error': str(e),
                    'success': False
                }
            await asyncio.sleep(2 ** attempt)  # Exponential backoff

def sanitize_url(url: str) -> str:
    """Sanitize URL for safe usage"""
    from urllib.parse import urlparse, urlunparse
    
    parsed = urlparse(url)
    
    # Remove dangerous characters and ensure proper format
    sanitized = urlunparse((
        parsed.scheme.lower(),
        parsed.netloc.lower(),
        parsed.path,
        parsed.params,
        parsed.query,
        ''  # Remove fragment for security
    ))
    
    return sanitized

def extract_domain(url: str) -> str:
    """Extract domain from URL"""
    from urllib.parse import urlparse
    return urlparse(url).netloc

# Data validation utilities
def validate_email(email: str) -> bool:
    """Validate email address format"""
    import re
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_url(url: str) -> bool:
    """Validate URL format"""
    from urllib.parse import urlparse
    
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except:
        return False

def sanitize_filename(filename: str) -> str:
    """Sanitize filename for safe file operations"""
    import re
    
    # Remove dangerous characters
    sanitized = re.sub(r'[<>:"/\\|?*]', '_', filename)
    
    # Remove leading/trailing whitespace and dots
    sanitized = sanitized.strip('. ')
    
    # Ensure reasonable length
    if len(sanitized) > 255:
        name, ext = os.path.splitext(sanitized)
        sanitized = name[:255-len(ext)] + ext
    
    return sanitized

def validate_json_schema(data: Dict[str, Any], schema: Dict[str, Any]) -> bool:
    """Basic JSON schema validation"""
    # This is a simplified implementation
    # For production use, consider using jsonschema library
    
    if not isinstance(data, dict):
        return False
    
    required_fields = schema.get('required', [])
    for field in required_fields:
        if field not in data:
            return False
    
    properties = schema.get('properties', {})
    for field, field_schema in properties.items():
        if field in data:
            field_type = field_schema.get('type')
            if field_type == 'string' and not isinstance(data[field], str):
                return False
            elif field_type == 'integer' and not isinstance(data[field], int):
                return False
            elif field_type == 'number' and not isinstance(data[field], (int, float)):
                return False
            elif field_type == 'boolean' and not isinstance(data[field], bool):
                return False
            elif field_type == 'array' and not isinstance(data[field], list):
                return False
            elif field_type == 'object' and not isinstance(data[field], dict):
                return False
    
    return True

# File operation utilities
def ensure_directory(path: Union[str, Path]) -> Path:
    """Ensure directory exists"""
    path = Path(path)
    path.mkdir(parents=True, exist_ok=True)
    return path

def safe_file_read(file_path: Union[str, Path], encoding: str = 'utf-8') -> Optional[str]:
    """Safely read file content"""
    try:
        with open(file_path, 'r', encoding=encoding) as f:
            return f.read()
    except Exception as e:
        get_logger(__name__).error(f"Failed to read file {file_path}: {e}")
        return None

def safe_file_write(file_path: Union[str, Path], content: str, encoding: str = 'utf-8') -> bool:
    """Safely write content to file"""
    try:
        file_path = Path(file_path)
        ensure_directory(file_path.parent)
        
        with open(file_path, 'w', encoding=encoding) as f:
            f.write(content)
        return True
    except Exception as e:
        get_logger(__name__).error(f"Failed to write file {file_path}: {e}")
        return False

# Hashing and ID utilities
def generate_hash(data: str, algorithm: str = 'sha256') -> str:
    """Generate hash of data"""
    hash_obj = hashlib.new(algorithm)
    hash_obj.update(data.encode('utf-8'))
    return hash_obj.hexdigest()

def generate_uuid() -> str:
    """Generate UUID string"""
    return str(uuid.uuid4())

def generate_short_id(length: int = 8) -> str:
    """Generate short random ID"""
    return str(uuid.uuid4()).replace('-', '')[:length]

# Async utilities
async def run_with_timeout(coro, timeout: float):
    """Run coroutine with timeout"""
    try:
        return await asyncio.wait_for(coro, timeout=timeout)
    except asyncio.TimeoutError:
        raise TimeoutError(f"Operation timed out after {timeout} seconds")

async def gather_with_exceptions(*coros):
    """Gather coroutines and return results with exceptions"""
    results = await asyncio.gather(*coros, return_exceptions=True)
    return results

class RateLimiter:
    """Simple rate limiter"""
    
    def __init__(self, calls: int, period: float):
        self.calls = calls
        self.period = period
        self.call_times = []
    
    async def acquire(self):
        """Acquire rate limit token"""
        now = datetime.now().timestamp()
        
        # Remove old calls
        self.call_times = [t for t in self.call_times if now - t < self.period]
        
        # Check if we can make a call
        if len(self.call_times) >= self.calls:
            sleep_time = self.period - (now - self.call_times[0])
            if sleep_time > 0:
                await asyncio.sleep(sleep_time)
        
        # Record this call
        self.call_times.append(now)

# Cache utilities
class SimpleCache:
    """Simple in-memory cache"""
    
    def __init__(self, ttl: int = 3600):
        self.ttl = ttl
        self.cache = {}
        self.timestamps = {}
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        if key not in self.cache:
            return None
        
        # Check TTL
        if datetime.now().timestamp() - self.timestamps[key] > self.ttl:
            del self.cache[key]
            del self.timestamps[key]
            return None
        
        return self.cache[key]
    
    def set(self, key: str, value: Any) -> None:
        """Set value in cache"""
        self.cache[key] = value
        self.timestamps[key] = datetime.now().timestamp()
    
    def delete(self, key: str) -> None:
        """Delete value from cache"""
        self.cache.pop(key, None)
        self.timestamps.pop(key, None)
    
    def clear(self) -> None:
        """Clear entire cache"""
        self.cache.clear()
        self.timestamps.clear()

# Retry decorator
def retry(max_attempts: int = 3, delay: float = 1.0, backoff: float = 2.0):
    """Retry decorator for functions"""
    def decorator(func):
        async def async_wrapper(*args, **kwargs):
            for attempt in range(max_attempts):
                try:
                    if asyncio.iscoroutinefunction(func):
                        return await func(*args, **kwargs)
                    else:
                        return func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_attempts - 1:
                        raise e
                    await asyncio.sleep(delay * (backoff ** attempt))
        
        def sync_wrapper(*args, **kwargs):
            import time
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_attempts - 1:
                        raise e
                    time.sleep(delay * (backoff ** attempt))
        
        return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper
    return decorator

# Export utilities
__all__ = [
    'setup_logging', 'get_logger',
    'load_config', 'save_config', 'merge_configs', 'get_env_var',
    'make_http_request', 'sanitize_url', 'extract_domain',
    'validate_email', 'validate_url', 'sanitize_filename', 'validate_json_schema',
    'ensure_directory', 'safe_file_read', 'safe_file_write',
    'generate_hash', 'generate_uuid', 'generate_short_id',
    'run_with_timeout', 'gather_with_exceptions',
    'RateLimiter', 'SimpleCache', 'retry'
]
