"""
Security middleware for the FastAPI application.
"""
import hashlib
import secrets
import time
from typing import Optional, List, Dict, Any, Callable
from fastapi import Request, Response, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from datetime import datetime, timedelta
import re
import ipaddress
from urllib.parse import unquote

class SecurityHeadersMiddleware:
    """Middleware to add security headers to responses."""
    
    def __init__(
        self,
        force_https: bool = True,
        hsts_max_age: int = 31536000,  # 1 year
        content_type_nosniff: bool = True,
        frame_options: str = "DENY",
        xss_protection: bool = True,
        referrer_policy: str = "strict-origin-when-cross-origin",
        csp_policy: Optional[str] = None
    ):
        self.force_https = force_https
        self.hsts_max_age = hsts_max_age
        self.content_type_nosniff = content_type_nosniff
        self.frame_options = frame_options
        self.xss_protection = xss_protection
        self.referrer_policy = referrer_policy
        self.csp_policy = csp_policy or (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' 'unsafe-eval'; "
            "style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data: https:; "
            "font-src 'self'; "
            "connect-src 'self'; "
            "frame-ancestors 'none'"
        )
    
    async def __call__(self, request: Request, call_next: Callable):
        """Add security headers to response."""
        response = await call_next(request)
        
        # Security headers
        security_headers = {}
        
        # HTTPS enforcement
        if self.force_https:
            security_headers["Strict-Transport-Security"] = (
                f"max-age={self.hsts_max_age}; includeSubDomains; preload"
            )
        
        # Content type protection
        if self.content_type_nosniff:
            security_headers["X-Content-Type-Options"] = "nosniff"
        
        # Frame protection
        if self.frame_options:
            security_headers["X-Frame-Options"] = self.frame_options
        
        # XSS protection
        if self.xss_protection:
            security_headers["X-XSS-Protection"] = "1; mode=block"
        
        # Referrer policy
        if self.referrer_policy:
            security_headers["Referrer-Policy"] = self.referrer_policy
        
        # Content Security Policy
        if self.csp_policy:
            security_headers["Content-Security-Policy"] = self.csp_policy
        
        # Additional security headers
        security_headers.update({
            "X-Permitted-Cross-Domain-Policies": "none",
            "X-Download-Options": "noopen",
            "Cache-Control": "no-cache, no-store, must-revalidate",
            "Pragma": "no-cache",
            "Expires": "0"
        })
        
        # Apply headers
        for header, value in security_headers.items():
            response.headers[header] = value
        
        return response

class CSRFProtectionMiddleware:
    """CSRF protection middleware using double-submit cookie pattern."""
    
    def __init__(
        self,
        secret_key: str,
        exempt_paths: Optional[List[str]] = None,
        safe_methods: Optional[List[str]] = None,
        token_header: str = "X-CSRF-Token",
        cookie_name: str = "csrf_token"
    ):
        self.secret_key = secret_key.encode()
        self.exempt_paths = exempt_paths or ["/docs", "/openapi.json", "/health"]
        self.safe_methods = safe_methods or ["GET", "HEAD", "OPTIONS", "TRACE"]
        self.token_header = token_header
        self.cookie_name = cookie_name
    
    async def __call__(self, request: Request, call_next: Callable):
        """Validate CSRF token for unsafe methods."""
        # Skip CSRF check for safe methods and exempt paths
        if (request.method in self.safe_methods or 
            request.url.path in self.exempt_paths or
            request.url.path.startswith("/api/docs")):
            response = await call_next(request)
            # Set CSRF token for safe requests
            if request.method == "GET":
                csrf_token = self._generate_csrf_token()
                response.set_cookie(
                    key=self.cookie_name,
                    value=csrf_token,
                    httponly=False,  # Needs to be accessible to JavaScript
                    secure=True,
                    samesite="strict"
                )
            return response
        
        # Validate CSRF token for unsafe methods
        cookie_token = request.cookies.get(self.cookie_name)
        header_token = request.headers.get(self.token_header)
        
        if not cookie_token or not header_token:
            raise HTTPException(
                status_code=403,
                detail="CSRF token missing"
            )
        
        if not self._validate_csrf_token(cookie_token, header_token):
            raise HTTPException(
                status_code=403,
                detail="CSRF token invalid"
            )
        
        return await call_next(request)
    
    def _generate_csrf_token(self) -> str:
        """Generate a new CSRF token."""
        timestamp = str(int(time.time()))
        random_value = secrets.token_urlsafe(32)
        token_data = f"{timestamp}:{random_value}"
        
        # Create HMAC signature
        signature = hashlib.hmac.new(
            self.secret_key,
            token_data.encode(),
            hashlib.sha256
        ).hexdigest()
        
        return f"{token_data}:{signature}"
    
    def _validate_csrf_token(self, cookie_token: str, header_token: str) -> bool:
        """Validate CSRF tokens."""
        # Tokens must match
        if cookie_token != header_token:
            return False
        
        try:
            parts = cookie_token.split(":")
            if len(parts) != 3:
                return False
            
            timestamp, random_value, signature = parts
            token_data = f"{timestamp}:{random_value}"
            
            # Verify signature
            expected_signature = hashlib.hmac.new(
                self.secret_key,
                token_data.encode(),
                hashlib.sha256
            ).hexdigest()
            
            if not secrets.compare_digest(signature, expected_signature):
                return False
            
            # Check if token is not too old (1 hour)
            token_time = int(timestamp)
            current_time = int(time.time())
            if current_time - token_time > 3600:
                return False
            
            return True
            
        except (ValueError, TypeError):
            return False

class IPWhitelistMiddleware:
    """IP whitelist/blacklist middleware."""
    
    def __init__(
        self,
        whitelist: Optional[List[str]] = None,
        blacklist: Optional[List[str]] = None,
        enable_forwarded_headers: bool = True
    ):
        self.whitelist = self._parse_ip_list(whitelist or [])
        self.blacklist = self._parse_ip_list(blacklist or [])
        self.enable_forwarded_headers = enable_forwarded_headers
    
    def _parse_ip_list(self, ip_list: List[str]) -> List:
        """Parse IP addresses and networks."""
        parsed = []
        for ip_str in ip_list:
            try:
                # Try as network first (supports CIDR notation)
                parsed.append(ipaddress.ip_network(ip_str, strict=False))
            except ValueError:
                try:
                    # Try as individual IP
                    parsed.append(ipaddress.ip_address(ip_str))
                except ValueError:
                    # Skip invalid IPs
                    continue
        return parsed
    
    async def __call__(self, request: Request, call_next: Callable):
        """Check IP against whitelist/blacklist."""
        client_ip = self._get_client_ip(request)
        
        if not client_ip:
            raise HTTPException(
                status_code=400,
                detail="Unable to determine client IP"
            )
        
        try:
            ip_addr = ipaddress.ip_address(client_ip)
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail="Invalid client IP address"
            )
        
        # Check blacklist first
        if self._is_ip_in_list(ip_addr, self.blacklist):
            raise HTTPException(
                status_code=403,
                detail="IP address is blacklisted"
            )
        
        # Check whitelist if configured
        if self.whitelist and not self._is_ip_in_list(ip_addr, self.whitelist):
            raise HTTPException(
                status_code=403,
                detail="IP address not whitelisted"
            )
        
        return await call_next(request)
    
    def _get_client_ip(self, request: Request) -> Optional[str]:
        """Extract client IP from request."""
        # Check forwarded headers if enabled
        if self.enable_forwarded_headers:
            # X-Forwarded-For header (comma-separated list)
            forwarded_for = request.headers.get("X-Forwarded-For")
            if forwarded_for:
                # Take the first IP (original client)
                return forwarded_for.split(",")[0].strip()
            
            # X-Real-IP header
            real_ip = request.headers.get("X-Real-IP")
            if real_ip:
                return real_ip.strip()
        
        # Fall back to direct connection IP
        return request.client.host if request.client else None
    
    def _is_ip_in_list(self, ip_addr, ip_list: List) -> bool:
        """Check if IP is in the given list."""
        for item in ip_list:
            if isinstance(item, ipaddress.IPv4Network) or isinstance(item, ipaddress.IPv6Network):
                if ip_addr in item:
                    return True
            elif ip_addr == item:
                return True
        return False

class InputValidationMiddleware:
    """Input validation and sanitization middleware."""
    
    def __init__(
        self,
        max_content_length: int = 10 * 1024 * 1024,  # 10MB
        blocked_patterns: Optional[List[str]] = None,
        blocked_user_agents: Optional[List[str]] = None
    ):
        self.max_content_length = max_content_length
        self.blocked_patterns = blocked_patterns or [
            r"<script[^>]*>.*?</script>",  # Script tags
            r"javascript:",  # JavaScript protocol
            r"vbscript:",  # VBScript protocol
            r"on\w+\s*=",  # Event handlers
            r"eval\s*\(",  # eval() calls
            r"union\s+select",  # SQL injection
            r"drop\s+table",  # SQL injection
            r"\.\./",  # Path traversal
            r"\.\.\\",  # Path traversal (Windows)
        ]
        self.blocked_user_agents = blocked_user_agents or [
            "sqlmap", "nikto", "nmap", "masscan", "openvas",
            "w3af", "skipfish", "burp", "zap"
        ]
        
        # Compile regex patterns
        self.pattern_regex = [re.compile(pattern, re.IGNORECASE) for pattern in self.blocked_patterns]
    
    async def __call__(self, request: Request, call_next: Callable):
        """Validate and sanitize request input."""
        # Check content length
        content_length = request.headers.get("Content-Length")
        if content_length and int(content_length) > self.max_content_length:
            raise HTTPException(
                status_code=413,
                detail="Request entity too large"
            )
        
        # Check user agent
        user_agent = request.headers.get("User-Agent", "").lower()
        for blocked_agent in self.blocked_user_agents:
            if blocked_agent in user_agent:
                raise HTTPException(
                    status_code=403,
                    detail="Blocked user agent"
                )
        
        # Check URL for malicious patterns
        url_str = unquote(str(request.url))
        for pattern in self.pattern_regex:
            if pattern.search(url_str):
                raise HTTPException(
                    status_code=400,
                    detail="Malicious pattern detected in URL"
                )
        
        # Check query parameters
        for key, value in request.query_params.items():
            decoded_value = unquote(value)
            for pattern in self.pattern_regex:
                if pattern.search(decoded_value):
                    raise HTTPException(
                        status_code=400,
                        detail=f"Malicious pattern detected in parameter: {key}"
                    )
        
        return await call_next(request)

def create_security_middleware_stack(
    environment: str = "production",
    secret_key: str = None,
    allowed_ips: Optional[List[str]] = None,
    blocked_ips: Optional[List[str]] = None
) -> List:
    """Create a complete security middleware stack."""
    middlewares = []
    
    # Input validation (first line of defense)
    middlewares.append(InputValidationMiddleware())
    
    # IP filtering
    if allowed_ips or blocked_ips:
        middlewares.append(IPWhitelistMiddleware(
            whitelist=allowed_ips,
            blacklist=blocked_ips
        ))
    
    # CSRF protection
    if secret_key:
        middlewares.append(CSRFProtectionMiddleware(secret_key=secret_key))
    
    # Security headers (last to ensure they're applied)
    if environment == "production":
        middlewares.append(SecurityHeadersMiddleware(
            force_https=True,
            frame_options="DENY",
            csp_policy=(
                "default-src 'self'; "
                "script-src 'self'; "
                "style-src 'self' 'unsafe-inline'; "
                "img-src 'self' data: https:; "
                "font-src 'self'; "
                "connect-src 'self'; "
                "frame-ancestors 'none'; "
                "base-uri 'self'; "
                "form-action 'self'"
            )
        ))
    else:
        middlewares.append(SecurityHeadersMiddleware(
            force_https=False,
            frame_options="SAMEORIGIN"
        ))
    
    return middlewares
