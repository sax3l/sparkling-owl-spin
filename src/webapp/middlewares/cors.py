"""
CORS (Cross-Origin Resource Sharing) middleware for the FastAPI application.
"""
from typing import List, Optional, Union
from fastapi import Request, Response
from fastapi.middleware.cors import CORSMiddleware as FastAPICORSMiddleware
import re
from urllib.parse import urlparse

class CustomCORSMiddleware:
    """Enhanced CORS middleware with additional security features."""
    
    def __init__(
        self,
        allow_origins: Union[List[str], str] = None,
        allow_origin_regex: Optional[str] = None,
        allow_methods: List[str] = None,
        allow_headers: List[str] = None,
        allow_credentials: bool = False,
        expose_headers: List[str] = None,
        max_age: int = 600,
        allow_private_networks: bool = False
    ):
        self.allow_origins = allow_origins or ["*"]
        self.allow_origin_regex = allow_origin_regex
        self.allow_methods = allow_methods or ["GET", "POST", "PUT", "DELETE", "OPTIONS", "HEAD", "PATCH"]
        self.allow_headers = allow_headers or [
            "Accept",
            "Accept-Language", 
            "Content-Language",
            "Content-Type",
            "Authorization",
            "X-Requested-With",
            "X-Request-ID",
            "X-API-Key",
            "X-Client-Version"
        ]
        self.allow_credentials = allow_credentials
        self.expose_headers = expose_headers or ["X-Request-ID", "X-Rate-Limit-Remaining"]
        self.max_age = max_age
        self.allow_private_networks = allow_private_networks
        
        # Compile regex pattern for origin validation
        if self.allow_origin_regex:
            self.origin_pattern = re.compile(self.allow_origin_regex)
        else:
            self.origin_pattern = None
    
    async def __call__(self, request: Request, call_next):
        """Process CORS headers for requests."""
        origin = request.headers.get("Origin")
        
        # Handle preflight requests
        if request.method == "OPTIONS":
            response = Response(status_code=200)
            await self._add_cors_headers(response, origin, is_preflight=True)
            return response
        
        # Process regular request
        response = await call_next(request)
        await self._add_cors_headers(response, origin, is_preflight=False)
        
        return response
    
    async def _add_cors_headers(
        self, 
        response: Response, 
        origin: Optional[str], 
        is_preflight: bool = False
    ):
        """Add appropriate CORS headers to response."""
        # Check if origin is allowed
        if origin and self._is_origin_allowed(origin):
            response.headers["Access-Control-Allow-Origin"] = origin
        elif "*" in self.allow_origins and not self.allow_credentials:
            response.headers["Access-Control-Allow-Origin"] = "*"
        
        # Add credentials header if needed
        if self.allow_credentials:
            response.headers["Access-Control-Allow-Credentials"] = "true"
        
        # Add exposed headers
        if self.expose_headers:
            response.headers["Access-Control-Expose-Headers"] = ", ".join(self.expose_headers)
        
        # Add preflight-specific headers
        if is_preflight:
            # Methods
            response.headers["Access-Control-Allow-Methods"] = ", ".join(self.allow_methods)
            
            # Headers
            response.headers["Access-Control-Allow-Headers"] = ", ".join(self.allow_headers)
            
            # Max age
            response.headers["Access-Control-Max-Age"] = str(self.max_age)
            
            # Private network access (for local development)
            if self.allow_private_networks:
                response.headers["Access-Control-Allow-Private-Network"] = "true"
    
    def _is_origin_allowed(self, origin: str) -> bool:
        """Check if the origin is allowed."""
        # Check exact matches
        if origin in self.allow_origins:
            return True
        
        # Check regex pattern
        if self.origin_pattern and self.origin_pattern.match(origin):
            return True
        
        # Check for wildcard subdomains
        for allowed_origin in self.allow_origins:
            if allowed_origin.startswith("*."):
                domain = allowed_origin[2:]  # Remove *.
                parsed_origin = urlparse(origin)
                if parsed_origin.netloc.endswith(f".{domain}") or parsed_origin.netloc == domain:
                    return True
        
        return False

class SecurityCORSMiddleware:
    """CORS middleware with enhanced security features."""
    
    def __init__(
        self,
        allowed_origins: List[str],
        development_mode: bool = False,
        strict_mode: bool = True
    ):
        self.allowed_origins = allowed_origins
        self.development_mode = development_mode
        self.strict_mode = strict_mode
    
    async def __call__(self, request: Request, call_next):
        """Process request with security-focused CORS handling."""
        origin = request.headers.get("Origin")
        
        # In strict mode, reject requests with disallowed origins
        if self.strict_mode and origin and not self._is_secure_origin(origin):
            return Response(
                content="CORS policy violation: Origin not allowed",
                status_code=403,
                headers={"Content-Type": "text/plain"}
            )
        
        # Handle preflight
        if request.method == "OPTIONS":
            if origin and self._is_secure_origin(origin):
                response = Response(status_code=200)
                await self._add_secure_headers(response, origin)
                return response
            else:
                return Response(status_code=403)
        
        # Process request
        response = await call_next(request)
        
        if origin and self._is_secure_origin(origin):
            await self._add_secure_headers(response, origin)
        
        return response
    
    def _is_secure_origin(self, origin: str) -> bool:
        """Check if origin meets security requirements."""
        parsed = urlparse(origin)
        
        # In development mode, allow localhost
        if self.development_mode:
            if parsed.hostname in ["localhost", "127.0.0.1", "::1"]:
                return True
        
        # Check against allowed origins
        if origin in self.allowed_origins:
            return True
        
        # Require HTTPS for production origins
        if not self.development_mode and parsed.scheme != "https":
            return False
        
        # Additional security checks
        if parsed.hostname:
            # Block known malicious patterns
            malicious_patterns = [
                "xss", "malware", "phishing", "spam",
                "192.168.", "10.", "172.16.", "172.17.", "172.18.", "172.19."
            ]
            
            hostname_lower = parsed.hostname.lower()
            if any(pattern in hostname_lower for pattern in malicious_patterns):
                return False
        
        return False
    
    async def _add_secure_headers(self, response: Response, origin: str):
        """Add security-focused CORS headers."""
        response.headers.update({
            "Access-Control-Allow-Origin": origin,
            "Access-Control-Allow-Credentials": "true",
            "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
            "Access-Control-Allow-Headers": (
                "Content-Type, Authorization, X-Requested-With, "
                "X-API-Key, X-Client-Version, X-Request-ID"
            ),
            "Access-Control-Expose-Headers": "X-Request-ID, X-Rate-Limit-Remaining",
            "Access-Control-Max-Age": "300",  # Shorter max age for security
            "Vary": "Origin"  # Important for caching
        })

def create_cors_middleware(environment: str = "production") -> Union[CustomCORSMiddleware, FastAPICORSMiddleware]:
    """Create CORS middleware based on environment."""
    
    if environment == "development":
        # Permissive settings for development
        return FastAPICORSMiddleware(
            allow_origins=["*"],
            allow_credentials=False,
            allow_methods=["*"],
            allow_headers=["*"],
            max_age=3600
        )
    
    elif environment == "staging":
        # Moderate security for staging
        return CustomCORSMiddleware(
            allow_origins=[
                "https://staging.example.com",
                "https://staging-admin.example.com"
            ],
            allow_origin_regex=r"https://.*\.staging\.example\.com",
            allow_credentials=True,
            max_age=600
        )
    
    else:  # production
        # Strict security for production
        return SecurityCORSMiddleware(
            allowed_origins=[
                "https://app.example.com",
                "https://admin.example.com",
                "https://api.example.com"
            ],
            development_mode=False,
            strict_mode=True
        )

def create_development_cors() -> FastAPICORSMiddleware:
    """Create permissive CORS middleware for local development."""
    return FastAPICORSMiddleware(
        allow_origins=[
            "http://localhost:3000",
            "http://localhost:3001", 
            "http://localhost:8080",
            "http://127.0.0.1:3000",
            "http://127.0.0.1:3001",
            "http://127.0.0.1:8080"
        ],
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "HEAD", "PATCH"],
        allow_headers=["*"],
        max_age=3600
    )

def create_production_cors(allowed_domains: List[str]) -> SecurityCORSMiddleware:
    """Create secure CORS middleware for production."""
    https_origins = [f"https://{domain}" for domain in allowed_domains]
    
    return SecurityCORSMiddleware(
        allowed_origins=https_origins,
        development_mode=False,
        strict_mode=True
    )
