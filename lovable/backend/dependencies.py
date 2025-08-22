"""
Lovable Backend Dependencies

Dependency injection for FastAPI routes.
"""

import time
from typing import Optional
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

try:
    from jose import jwt, JWTError
except ImportError:
    try:
        import jwt
        from jwt import PyJWTError as JWTError
    except ImportError:
        # Mock for development
        class jwt:
            @staticmethod
            def decode(token, key, algorithms):
                return {"sub": "1"}
        
        class JWTError(Exception):
            pass

from .database import get_db
from .settings import get_settings
from .models import UserInDB
from .services import UserService, APIKeyService, AuditService


settings = get_settings()
security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> UserInDB:
    """Get current authenticated user from JWT token."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(
            credentials.credentials, 
            settings.jwt_secret_key, 
            algorithms=[settings.jwt_algorithm]
        )
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = UserService.get_user(db, user_id=int(user_id))
    if user is None:
        raise credentials_exception
    return user


async def get_current_active_user(
    current_user: UserInDB = Depends(get_current_user)
) -> UserInDB:
    """Get current active user."""
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


async def get_current_admin_user(
    current_user: UserInDB = Depends(get_current_active_user)
) -> UserInDB:
    """Get current admin user."""
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    return current_user


async def get_api_key_user(
    request: Request,
    db: Session = Depends(get_db)
) -> Optional[UserInDB]:
    """Get user from API key authentication."""
    api_key = request.headers.get("X-API-Key")
    if not api_key:
        return None

    db_key = APIKeyService.verify_api_key(db, api_key)
    if not db_key:
        return None

    user = UserService.get_user(db, db_key.user_id)
    return user


async def get_user_or_api_key(
    request: Request,
    db: Session = Depends(get_db),
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> UserInDB:
    """Get user from either JWT token or API key."""
    # Try API key first
    api_user = await get_api_key_user(request, db)
    if api_user:
        return api_user

    # Try JWT token
    if credentials:
        return await get_current_user(credentials, db)

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )


async def log_request(
    request: Request,
    current_user: Optional[UserInDB] = None,
    db: Session = Depends(get_db)
):
    """Log API request for audit purposes."""
    if current_user:
        AuditService.log_action(
            db=db,
            action=f"{request.method} {request.url.path}",
            user_id=current_user.id,
            ip_address=request.client.host if request.client else None,
            user_agent=request.headers.get("user-agent"),
            details={
                "method": request.method,
                "path": request.url.path,
                "query_params": dict(request.query_params)
            }
        )


class RateLimitDependency:
    """Rate limiting dependency."""

    def __init__(self, max_requests: int = 100, window_seconds: int = 60):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self._requests = {}

    async def __call__(self, request: Request):
        """Check rate limit."""
        client_ip = request.client.host if request.client else "unknown"
        current_time = int(time.time())
        window_start = current_time - self.window_seconds

        # Clean old requests
        if client_ip in self._requests:
            self._requests[client_ip] = [
                req_time for req_time in self._requests[client_ip]
                if req_time > window_start
            ]
        else:
            self._requests[client_ip] = []

        # Check rate limit
        if len(self._requests[client_ip]) >= self.max_requests:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Rate limit exceeded"
            )

        # Add current request
        self._requests[client_ip].append(current_time)


# Rate limit instances
rate_limit_strict = RateLimitDependency(max_requests=10, window_seconds=60)
rate_limit_normal = RateLimitDependency(max_requests=100, window_seconds=60)
rate_limit_lenient = RateLimitDependency(max_requests=1000, window_seconds=60)
