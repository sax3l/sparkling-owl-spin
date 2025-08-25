"""
Dependencies for the ECaDP Backend API.
"""

from typing import Optional, Any, AsyncGenerator
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from src.database.manager import DatabaseManager
from src.settings import get_settings


settings = get_settings()
security = HTTPBearer()
db_manager = DatabaseManager()


async def get_db_session() -> AsyncGenerator[Session, None]:
    """Get database session."""
    async with db_manager.get_session() as session:
        yield session


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db_session)
) -> Any:
    """Get current authenticated user from JWT token."""
    # TODO: Implement proper JWT token validation and user retrieval
    # For now, return a mock user for development
    class MockUser:
        def __init__(self):
            self.id = 1
            self.email = "dev@example.com"
            self.is_active = True
    
    return MockUser()


async def get_admin_user(
    current_user = Depends(get_current_user)
) -> Any:
    """Get current user and verify admin privileges."""
    # TODO: Implement proper admin verification
    return current_user


async def get_rate_limiter():
    """Get rate limiter instance."""
    # TODO: Implement rate limiting
    class MockRateLimiter:
        async def check_limit(self, key: str, limit: int, window: int) -> bool:
            return True
    
    return MockRateLimiter()
