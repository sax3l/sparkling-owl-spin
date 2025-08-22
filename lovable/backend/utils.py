"""
Lovable Backend Utilities

Utility functions and helper classes.
"""

import asyncio
import hashlib
import secrets
import string
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Union
from pathlib import Path
import json
import re


class IDGenerator:
    """Generate various types of IDs."""
    
    @staticmethod
    def uuid4() -> str:
        """Generate UUID4."""
        return str(uuid.uuid4())
    
    @staticmethod
    def short_id(length: int = 8) -> str:
        """Generate short alphanumeric ID."""
        alphabet = string.ascii_letters + string.digits
        return ''.join(secrets.choice(alphabet) for _ in range(length))
    
    @staticmethod
    def api_key() -> str:
        """Generate API key."""
        return f"lv_{secrets.token_urlsafe(32)}"


class HashUtils:
    """Hashing utilities."""
    
    @staticmethod
    def sha256(data: Union[str, bytes]) -> str:
        """Generate SHA256 hash."""
        if isinstance(data, str):
            data = data.encode('utf-8')
        return hashlib.sha256(data).hexdigest()
    
    @staticmethod
    def md5(data: Union[str, bytes]) -> str:
        """Generate MD5 hash."""
        if isinstance(data, str):
            data = data.encode('utf-8')
        return hashlib.md5(data).hexdigest()


class DateTimeUtils:
    """DateTime utilities."""
    
    @staticmethod
    def utcnow() -> datetime:
        """Get current UTC datetime."""
        return datetime.now(timezone.utc)
    
    @staticmethod
    def timestamp() -> int:
        """Get current timestamp."""
        return int(DateTimeUtils.utcnow().timestamp())
    
    @staticmethod
    def iso_string(dt: Optional[datetime] = None) -> str:
        """Convert datetime to ISO string."""
        if dt is None:
            dt = DateTimeUtils.utcnow()
        return dt.isoformat()


class ValidationUtils:
    """Validation utilities."""
    
    @staticmethod
    def is_valid_email(email: str) -> bool:
        """Validate email format."""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))
    
    @staticmethod
    def is_valid_username(username: str) -> bool:
        """Validate username format."""
        pattern = r'^[a-zA-Z0-9_-]{3,50}$'
        return bool(re.match(pattern, username))
    
    @staticmethod
    def is_strong_password(password: str) -> bool:
        """Check if password is strong."""
        if len(password) < 8:
            return False
        
        has_upper = any(c.isupper() for c in password)
        has_lower = any(c.islower() for c in password)
        has_digit = any(c.isdigit() for c in password)
        has_special = any(c in '!@#$%^&*(),.?":{}|<>' for c in password)
        
        return sum([has_upper, has_lower, has_digit, has_special]) >= 3


class FileUtils:
    """File utilities."""
    
    @staticmethod
    def ensure_dir(path: Union[str, Path]) -> Path:
        """Ensure directory exists."""
        path = Path(path)
        path.mkdir(parents=True, exist_ok=True)
        return path
    
    @staticmethod
    def safe_filename(filename: str) -> str:
        """Make filename safe for filesystem."""
        # Remove dangerous characters
        safe = re.sub(r'[^\w\s-.]', '', filename)
        # Replace spaces with underscores
        safe = re.sub(r'[\s]+', '_', safe)
        # Remove multiple underscores
        safe = re.sub(r'_+', '_', safe)
        return safe.strip('_.')
    
    @staticmethod
    def read_json(path: Union[str, Path]) -> Dict[str, Any]:
        """Read JSON file."""
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    @staticmethod
    def write_json(path: Union[str, Path], data: Dict[str, Any], indent: int = 2):
        """Write JSON file."""
        FileUtils.ensure_dir(Path(path).parent)
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=indent, ensure_ascii=False)


class AsyncUtils:
    """Async utilities."""
    
    @staticmethod
    async def run_in_executor(func, *args, **kwargs):
        """Run sync function in thread pool executor."""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, func, *args, **kwargs)
    
    @staticmethod
    async def gather_with_concurrency(limit: int, *coroutines):
        """Run coroutines with concurrency limit."""
        semaphore = asyncio.Semaphore(limit)
        
        async def sem_coro(coro):
            async with semaphore:
                return await coro
        
        return await asyncio.gather(*(sem_coro(c) for c in coroutines))


class ConfigUtils:
    """Configuration utilities."""
    
    @staticmethod
    def get_env_bool(key: str, default: bool = False) -> bool:
        """Get boolean environment variable."""
        import os
        value = os.getenv(key, '').lower()
        return value in ('true', '1', 'yes', 'on')
    
    @staticmethod
    def get_env_int(key: str, default: int = 0) -> int:
        """Get integer environment variable."""
        import os
        try:
            return int(os.getenv(key, str(default)))
        except ValueError:
            return default
    
    @staticmethod
    def get_env_list(key: str, separator: str = ',', default: Optional[List[str]] = None) -> List[str]:
        """Get list environment variable."""
        import os
        value = os.getenv(key)
        if not value:
            return default or []
        return [item.strip() for item in value.split(separator)]


class TextUtils:
    """Text processing utilities."""
    
    @staticmethod
    def truncate(text: str, max_length: int, suffix: str = '...') -> str:
        """Truncate text to max length."""
        if len(text) <= max_length:
            return text
        return text[:max_length - len(suffix)] + suffix
    
    @staticmethod
    def slug(text: str) -> str:
        """Convert text to URL-friendly slug."""
        # Convert to lowercase
        text = text.lower()
        # Replace spaces and special chars with hyphens
        text = re.sub(r'[^\w\s-]', '', text)
        text = re.sub(r'[\s_-]+', '-', text)
        # Remove leading/trailing hyphens
        return text.strip('-')
    
    @staticmethod
    def camel_to_snake(name: str) -> str:
        """Convert camelCase to snake_case."""
        s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
        return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()
    
    @staticmethod
    def snake_to_camel(name: str) -> str:
        """Convert snake_case to camelCase."""
        components = name.split('_')
        return components[0] + ''.join(x.capitalize() for x in components[1:])


class ResponseUtils:
    """API response utilities."""
    
    @staticmethod
    def success(data: Any = None, message: str = "Success") -> Dict[str, Any]:
        """Create success response."""
        response = {"success": True, "message": message}
        if data is not None:
            response["data"] = data
        return response
    
    @staticmethod
    def error(message: str, code: Optional[str] = None, details: Any = None) -> Dict[str, Any]:
        """Create error response."""
        response = {"success": False, "message": message}
        if code:
            response["code"] = code
        if details:
            response["details"] = details
        return response
    
    @staticmethod
    def paginated(items: List[Any], total: int, page: int, per_page: int) -> Dict[str, Any]:
        """Create paginated response."""
        total_pages = (total + per_page - 1) // per_page
        return {
            "items": items,
            "pagination": {
                "total": total,
                "page": page,
                "per_page": per_page,
                "total_pages": total_pages,
                "has_next": page < total_pages,
                "has_prev": page > 1
            }
        }
