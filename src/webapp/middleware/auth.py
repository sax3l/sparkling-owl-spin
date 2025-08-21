"""
Authentication middleware for the web application.
"""
import logging
from typing import Callable, Optional
import jwt
from fastapi import Request, Response, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger(__name__)


class AuthMiddleware(BaseHTTPMiddleware):
    """Middleware for handling authentication."""
    
    def __init__(self, app, secret_key: str = "your-secret-key"):
        """Initialize authentication middleware.
        
        Args:
            app: FastAPI application
            secret_key: JWT secret key
        """
        super().__init__(app)
        self.secret_key = secret_key
        self.security = HTTPBearer()
        
        # Paths that don't require authentication
        self.exempt_paths = {
            "/health",
            "/metrics", 
            "/docs",
            "/redoc",
            "/openapi.json"
        }
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request through authentication middleware."""
        
        # Skip authentication for exempt paths
        if request.url.path in self.exempt_paths:
            return await call_next(request)
        
        # Skip authentication for OPTIONS requests
        if request.method == "OPTIONS":
            return await call_next(request)
        
        try:
            # Extract and validate token
            token = await self._extract_token(request)
            if token:
                user_info = await self._validate_token(token)
                if user_info:
                    # Add user info to request state
                    request.state.user = user_info
                    return await call_next(request)
            
            # No valid authentication found
            return Response(
                content='{"error": "Authentication required"}',
                status_code=401,
                media_type="application/json"
            )
        
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Authentication error: {e}")
            return Response(
                content='{"error": "Authentication failed"}',
                status_code=401,
                media_type="application/json"
            )
    
    async def _extract_token(self, request: Request) -> Optional[str]:
        """Extract authentication token from request.
        
        Args:
            request: FastAPI request object
            
        Returns:
            JWT token or None
        """
        # Check Authorization header
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            return auth_header.split(" ", 1)[1]
        
        # Check API key header
        api_key = request.headers.get("X-API-Key")
        if api_key:
            return api_key
        
        # Check query parameter
        api_key_param = request.query_params.get("api_key")
        if api_key_param:
            return api_key_param
        
        return None
    
    async def _validate_token(self, token: str) -> Optional[dict]:
        """Validate authentication token.
        
        Args:
            token: JWT token or API key
            
        Returns:
            User information dict or None
        """
        try:
            # Try to decode as JWT
            payload = jwt.decode(token, self.secret_key, algorithms=["HS256"])
            return {
                "user_id": payload.get("user_id"),
                "username": payload.get("username"),
                "scopes": payload.get("scopes", []),
                "token_type": "jwt"
            }
        except jwt.InvalidTokenError:
            # Try to validate as API key
            return await self._validate_api_key(token)
    
    async def _validate_api_key(self, api_key: str) -> Optional[dict]:
        """Validate API key.
        
        Args:
            api_key: API key to validate
            
        Returns:
            User information dict or None
        """
        # In a real implementation, this would check against a database
        # For now, accept any key that starts with "sk-"
        if api_key.startswith("sk-"):
            return {
                "user_id": "api_user",
                "username": "api_user",
                "scopes": ["scraping:read", "scraping:write"],
                "token_type": "api_key",
                "api_key": api_key[:8] + "..."  # Masked for logging
            }
        
        return None
    
    def create_token(self, user_id: str, username: str, scopes: list = None) -> str:
        """Create a JWT token for a user.
        
        Args:
            user_id: User identifier
            username: Username
            scopes: List of permission scopes
            
        Returns:
            JWT token
        """
        payload = {
            "user_id": user_id,
            "username": username,
            "scopes": scopes or [],
            "exp": jwt.datetime.utcnow() + jwt.timedelta(hours=24)
        }
        
        return jwt.encode(payload, self.secret_key, algorithm="HS256")
