"""
FastAPI dependencies for dependency injection.
"""
from typing import Annotated, Generator
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
import redis
from src.database.connection import get_db_connection
from src.database.models import User
from src.services.auth import AuthService
from src.services.cache import CacheService
from src.services.rate_limit import RateLimitService
from src.utils.config import get_settings

# Security scheme
security = HTTPBearer()

# Settings dependency
def get_app_settings():
    """Get application settings."""
    return get_settings()

# Database dependency
def get_database() -> Generator[Session, None, None]:
    """Get database session."""
    db = get_db_connection()
    try:
        yield db
    finally:
        db.close()

# Redis dependency
def get_redis_client():
    """Get Redis client."""
    settings = get_settings()
    return redis.from_url(
        settings.redis_url,
        encoding="utf-8",
        decode_responses=True,
        socket_keepalive=True,
        socket_keepalive_options={
            "TCP_KEEPIDLE": 1,
            "TCP_KEEPINTVL": 3,
            "TCP_KEEPCNT": 5,
        }
    )

# Cache service dependency
def get_cache_service(
    redis_client: Annotated[redis.Redis, Depends(get_redis_client)]
) -> CacheService:
    """Get cache service."""
    return CacheService(redis_client)

# Rate limit service dependency
def get_rate_limit_service(
    redis_client: Annotated[redis.Redis, Depends(get_redis_client)]
) -> RateLimitService:
    """Get rate limiting service."""
    return RateLimitService(redis_client)

# Auth service dependency
def get_auth_service(
    db: Annotated[Session, Depends(get_database)],
    cache: Annotated[CacheService, Depends(get_cache_service)]
) -> AuthService:
    """Get authentication service."""
    return AuthService(db, cache)

# Current user dependency
async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
    auth_service: Annotated[AuthService, Depends(get_auth_service)]
) -> User:
    """Get current authenticated user."""
    try:
        token = credentials.credentials
        user = await auth_service.get_user_from_token(token)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return user
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        ) from e

# Optional user dependency (for public endpoints that can work with/without auth)
async def get_current_user_optional(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    auth_service: AuthService = Depends(get_auth_service)
) -> User | None:
    """Get current user if authenticated, None otherwise."""
    if not credentials:
        return None
    
    try:
        token = credentials.credentials
        return await auth_service.get_user_from_token(token)
    except Exception:
        return None

# Admin user dependency
async def get_admin_user(
    current_user: Annotated[User, Depends(get_current_user)]
) -> User:
    """Ensure current user is an admin."""
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user

# Active user dependency
async def get_active_user(
    current_user: Annotated[User, Depends(get_current_user)]
) -> User:
    """Ensure current user is active."""
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is disabled"
        )
    return current_user

# Pagination dependency
class PaginationParams:
    """Pagination parameters."""
    
    def __init__(
        self,
        page: int = 1,
        size: int = 20,
        max_size: int = 100
    ):
        self.page = max(1, page)
        self.size = min(max_size, max(1, size))
        self.skip = (self.page - 1) * self.size

def get_pagination_params(
    page: int = 1,
    size: int = 20
) -> PaginationParams:
    """Get pagination parameters."""
    return PaginationParams(page=page, size=size)

# Sorting dependency
class SortParams:
    """Sorting parameters."""
    
    def __init__(
        self,
        sort_by: str = "created_at",
        sort_order: str = "desc"
    ):
        self.sort_by = sort_by
        self.sort_order = sort_order.lower()
        if self.sort_order not in ["asc", "desc"]:
            self.sort_order = "desc"

def get_sort_params(
    sort_by: str = "created_at",
    sort_order: str = "desc"
) -> SortParams:
    """Get sorting parameters."""
    return SortParams(sort_by=sort_by, sort_order=sort_order)

# Rate limiting dependency
def rate_limit(
    requests_per_minute: int = 60,
    requests_per_hour: int = 1000
):
    """Rate limiting decorator factory."""
    def dependency(
        request,
        rate_limit_service: Annotated[RateLimitService, Depends(get_rate_limit_service)]
    ):
        client_ip = request.client.host
        
        # Check minute limit
        minute_key = f"rate_limit:minute:{client_ip}"
        if not rate_limit_service.check_rate_limit(minute_key, requests_per_minute, 60):
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Rate limit exceeded: too many requests per minute"
            )
        
        # Check hour limit
        hour_key = f"rate_limit:hour:{client_ip}"
        if not rate_limit_service.check_rate_limit(hour_key, requests_per_hour, 3600):
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Rate limit exceeded: too many requests per hour"
            )
        
        return True
    
    return dependency

# API key dependency
async def get_api_key_user(
    api_key: str,
    auth_service: Annotated[AuthService, Depends(get_auth_service)]
) -> User:
    """Get user from API key."""
    user = await auth_service.get_user_from_api_key(api_key)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key"
        )
    return user

# Webhook signature verification dependency
def verify_webhook_signature(
    signature_header: str,
    raw_body: bytes,
    webhook_secret: str
) -> bool:
    """Verify webhook signature."""
    import hmac
    import hashlib
    
    if not signature_header.startswith("sha256="):
        return False
    
    signature = signature_header[7:]  # Remove "sha256=" prefix
    expected_signature = hmac.new(
        webhook_secret.encode(),
        raw_body,
        hashlib.sha256
    ).hexdigest()
    
    return hmac.compare_digest(signature, expected_signature)

# Feature flag dependency
def require_feature_flag(feature_name: str):
    """Require feature flag to be enabled."""
    def dependency(
        settings = Depends(get_app_settings)
    ):
        if not settings.is_feature_enabled(feature_name):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Feature not available"
            )
        return True
    
    return dependency

# Database type annotations
DatabaseSession = Annotated[Session, Depends(get_database)]
CurrentUser = Annotated[User, Depends(get_current_user)]
AdminUser = Annotated[User, Depends(get_admin_user)]
ActiveUser = Annotated[User, Depends(get_active_user)]
OptionalUser = Annotated[User | None, Depends(get_current_user_optional)]
PaginationDep = Annotated[PaginationParams, Depends(get_pagination_params)]
SortingDep = Annotated[SortParams, Depends(get_sort_params)]
CacheServiceDep = Annotated[CacheService, Depends(get_cache_service)]
RateLimitServiceDep = Annotated[RateLimitService, Depends(get_rate_limit_service)]
AuthServiceDep = Annotated[AuthService, Depends(get_auth_service)]
