"""
FastAPI dependencies for authentication, authorization, and common functionality.
"""

import os
from typing import List, Optional, Callable
from functools import wraps

from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials, APIKeyHeader
from sqlalchemy.orm import Session
import jwt
from jwt import PyJWTError

from .database import get_db
from .models import User, APIKey
from .config import get_settings

settings = get_settings()
security = HTTPBearer()
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

# JWT configuration
SECRET_KEY = os.getenv("SECRET_KEY") or settings.secret_key
ALGORITHM = "HS256"


async def get_current_user_from_token(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """
    Get current user from JWT token.
    
    Args:
        credentials: HTTP Bearer token credentials
        db: Database session
        
    Returns:
        User: Current authenticated user
        
    Raises:
        HTTPException: If token is invalid or user not found
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        token_type: str = payload.get("type", "access")
        
        if user_id is None or token_type != "access":
            raise credentials_exception
            
    except PyJWTError:
        raise credentials_exception
    
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise credentials_exception
        
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User account is disabled"
        )
        
    if user.is_locked():
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User account is locked"
        )
    
    return user


async def get_current_user_from_api_key(
    api_key: Optional[str] = Depends(api_key_header),
    request: Request = None,
    db: Session = Depends(get_db)
) -> Optional[User]:
    """
    Get current user from API key.
    
    Args:
        api_key: API key from header
        request: FastAPI request object
        db: Database session
        
    Returns:
        User: Current authenticated user or None if no API key
        
    Raises:
        HTTPException: If API key is invalid
    """
    if not api_key:
        return None
    
    # Hash the provided API key
    api_key_hash = APIKey.hash_key(api_key)
    
    # Find API key in database
    db_api_key = db.query(APIKey).filter(APIKey.key_hash == api_key_hash).first()
    
    if not db_api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key"
        )
    
    if not db_api_key.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API key is disabled"
        )
    
    if db_api_key.is_expired():
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API key has expired"
        )
    
    # Check IP restrictions
    if request and not db_api_key.is_ip_allowed(request.client.host):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="IP address not allowed for this API key"
        )
    
    # Record usage
    db_api_key.record_usage()
    db.commit()
    
    # Get associated user
    user = db.query(User).filter(User.id == db_api_key.user_id).first()
    
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User account associated with API key is disabled"
        )
    
    return user


async def get_current_user(
    token_user: Optional[User] = Depends(get_current_user_from_token),
    api_key_user: Optional[User] = Depends(get_current_user_from_api_key)
) -> User:
    """
    Get current user from either JWT token or API key.
    
    Args:
        token_user: User from JWT token (if provided)
        api_key_user: User from API key (if provided)
        
    Returns:
        User: Current authenticated user
        
    Raises:
        HTTPException: If no valid authentication provided
    """
    user = token_user or api_key_user
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return user


async def get_optional_user(
    token_user: Optional[User] = Depends(get_current_user_from_token),
    api_key_user: Optional[User] = Depends(get_current_user_from_api_key)
) -> Optional[User]:
    """
    Get current user if authenticated, otherwise return None.
    
    Args:
        token_user: User from JWT token (if provided)
        api_key_user: User from API key (if provided)
        
    Returns:
        User: Current authenticated user or None
    """
    return token_user or api_key_user


def require_permissions(permissions: List[str]) -> Callable:
    """
    Dependency factory to require specific permissions.
    
    Args:
        permissions: List of required permissions
        
    Returns:
        Callable: Dependency function that validates permissions
        
    Usage:
        @app.get("/admin/users")
        def get_users(user: User = Depends(require_permissions(["read:all_users"]))):
            return get_all_users()
    """
    def permission_dependency(current_user: User = Depends(get_current_user)) -> User:
        user_permissions = current_user.get_permissions()
        
        for permission in permissions:
            if permission not in user_permissions:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Permission '{permission}' required"
                )
        
        return current_user
    
    return permission_dependency


def require_superuser(current_user: User = Depends(get_current_user)) -> User:
    """
    Require current user to be a superuser.
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        User: Current user (if superuser)
        
    Raises:
        HTTPException: If user is not a superuser
    """
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Superuser access required"
        )
    
    return current_user


def require_verified_user(current_user: User = Depends(get_current_user)) -> User:
    """
    Require current user to be verified.
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        User: Current user (if verified)
        
    Raises:
        HTTPException: If user is not verified
    """
    if not current_user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Email verification required"
        )
    
    return current_user


async def get_api_key_permissions(
    api_key: Optional[str] = Depends(api_key_header),
    db: Session = Depends(get_db)
) -> List[str]:
    """
    Get permissions for the current API key.
    
    Args:
        api_key: API key from header
        db: Database session
        
    Returns:
        List[str]: List of API key permissions
    """
    if not api_key:
        return []
    
    api_key_hash = APIKey.hash_key(api_key)
    db_api_key = db.query(APIKey).filter(APIKey.key_hash == api_key_hash).first()
    
    if not db_api_key or not db_api_key.is_active or db_api_key.is_expired():
        return []
    
    return db_api_key.get_scopes()


def require_api_key_scope(scopes: List[str]) -> Callable:
    """
    Dependency factory to require specific API key scopes.
    
    Args:
        scopes: List of required scopes
        
    Returns:
        Callable: Dependency function that validates scopes
    """
    def scope_dependency(
        api_key_permissions: List[str] = Depends(get_api_key_permissions)
    ) -> List[str]:
        for scope in scopes:
            if scope not in api_key_permissions:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"API key scope '{scope}' required"
                )
        
        return api_key_permissions
    
    return scope_dependency


async def get_rate_limit_key(
    request: Request,
    current_user: Optional[User] = Depends(get_optional_user)
) -> str:
    """
    Get rate limiting key for the current request.
    
    Args:
        request: FastAPI request object
        current_user: Current authenticated user (if any)
        
    Returns:
        str: Rate limiting key
    """
    if current_user:
        return f"user:{current_user.id}"
    
    # Fall back to IP address for unauthenticated requests
    return f"ip:{request.client.host}"


def validate_content_type(allowed_types: List[str]) -> Callable:
    """
    Dependency factory to validate request content type.
    
    Args:
        allowed_types: List of allowed content types
        
    Returns:
        Callable: Dependency function that validates content type
    """
    def content_type_dependency(request: Request) -> str:
        content_type = request.headers.get("content-type", "")
        
        if not any(allowed_type in content_type for allowed_type in allowed_types):
            raise HTTPException(
                status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
                detail=f"Content type must be one of: {', '.join(allowed_types)}"
            )
        
        return content_type
    
    return content_type_dependency


async def get_user_agent(request: Request) -> str:
    """
    Get user agent from request headers.
    
    Args:
        request: FastAPI request object
        
    Returns:
        str: User agent string
    """
    return request.headers.get("user-agent", "Unknown")


async def get_client_ip(request: Request) -> str:
    """
    Get client IP address from request.
    
    Args:
        request: FastAPI request object
        
    Returns:
        str: Client IP address
    """
    # Check for forwarded headers first (for reverse proxy setups)
    forwarded_for = request.headers.get("x-forwarded-for")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()
    
    real_ip = request.headers.get("x-real-ip")
    if real_ip:
        return real_ip
    
    return request.client.host


def admin_required(func):
    """
    Decorator to require admin access for a function.
    
    Args:
        func: Function to decorate
        
    Returns:
        Decorated function that requires admin access
    """
    @wraps(func)
    async def wrapper(*args, **kwargs):
        # Extract current_user from kwargs
        current_user = kwargs.get("current_user")
        
        if not current_user or not current_user.can_access_admin():
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Admin access required"
            )
        
        return await func(*args, **kwargs)
    
    return wrapper


def require_feature_flag(flag_name: str) -> Callable:
    """
    Dependency factory to require a feature flag to be enabled.
    
    Args:
        flag_name: Name of the feature flag
        
    Returns:
        Callable: Dependency function that checks feature flag
    """
    def feature_flag_dependency() -> bool:
        # In a real implementation, this would check a feature flag service
        # For now, we'll check environment variables
        flag_value = os.getenv(f"FEATURE_{flag_name.upper()}", "false").lower()
        is_enabled = flag_value in ("true", "1", "yes", "on")
        
        if not is_enabled:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Feature not available"
            )
        
        return is_enabled
    
    return feature_flag_dependency
