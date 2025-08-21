"""
Logging middleware for the FastAPI application.
"""
import time
import json
import uuid
from typing import Callable, Dict, Any, Optional
from fastapi import Request, Response
from fastapi.routing import Match
import structlog
from datetime import datetime

# Configure structured logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger(__name__)

class LoggingMiddleware:
    """Comprehensive logging middleware for request/response tracking."""
    
    def __init__(
        self,
        skip_paths: Optional[list] = None,
        log_request_body: bool = False,
        log_response_body: bool = False,
        sensitive_headers: Optional[list] = None
    ):
        self.skip_paths = skip_paths or ["/health", "/metrics", "/docs", "/openapi.json"]
        self.log_request_body = log_request_body
        self.log_response_body = log_response_body
        self.sensitive_headers = sensitive_headers or [
            "authorization", "cookie", "x-api-key", "x-auth-token"
        ]
    
    async def __call__(self, request: Request, call_next: Callable):
        """Process request with comprehensive logging."""
        # Generate request ID
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id
        
        # Skip logging for certain paths
        if request.url.path in self.skip_paths:
            return await call_next(request)
        
        # Start timing
        start_time = time.time()
        
        # Log request
        await self._log_request(request, request_id)
        
        # Process request
        try:
            response = await call_next(request)
            
            # Calculate duration
            duration = time.time() - start_time
            
            # Log response
            await self._log_response(request, response, request_id, duration)
            
            # Add request ID to response headers
            response.headers["X-Request-ID"] = request_id
            
            return response
            
        except Exception as e:
            # Log error
            duration = time.time() - start_time
            await self._log_error(request, e, request_id, duration)
            raise
    
    async def _log_request(self, request: Request, request_id: str):
        """Log incoming request details."""
        # Get client information
        client_ip = request.client.host
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            client_ip = forwarded_for.split(",")[0].strip()
        
        user_agent = request.headers.get("User-Agent", "Unknown")
        
        # Prepare headers (excluding sensitive ones)
        headers = dict(request.headers)
        for sensitive_header in self.sensitive_headers:
            if sensitive_header in headers:
                headers[sensitive_header] = "***REDACTED***"
        
        # Prepare request body if enabled
        request_body = None
        if self.log_request_body and request.method in ["POST", "PUT", "PATCH"]:
            try:
                body = await request.body()
                if body:
                    # Try to parse as JSON for better logging
                    try:
                        request_body = json.loads(body.decode())
                    except (json.JSONDecodeError, UnicodeDecodeError):
                        request_body = body.decode("utf-8", errors="ignore")[:1000]
            except Exception:
                request_body = "Unable to read request body"
        
        # Log request
        logger.info(
            "HTTP request received",
            request_id=request_id,
            method=request.method,
            url=str(request.url),
            path=request.url.path,
            query_params=dict(request.query_params),
            client_ip=client_ip,
            user_agent=user_agent,
            headers=headers,
            body=request_body,
            timestamp=datetime.utcnow().isoformat()
        )
    
    async def _log_response(
        self, 
        request: Request, 
        response: Response, 
        request_id: str, 
        duration: float
    ):
        """Log response details."""
        # Prepare response body if enabled
        response_body = None
        if self.log_response_body and hasattr(response, "body"):
            try:
                if response.body:
                    # Try to parse as JSON for better logging
                    try:
                        response_body = json.loads(response.body.decode())
                    except (json.JSONDecodeError, UnicodeDecodeError):
                        response_body = response.body.decode("utf-8", errors="ignore")[:1000]
            except Exception:
                response_body = "Unable to read response body"
        
        # Determine log level based on status code
        if response.status_code >= 500:
            log_level = "error"
        elif response.status_code >= 400:
            log_level = "warning"
        else:
            log_level = "info"
        
        # Log response
        getattr(logger, log_level)(
            "HTTP response sent",
            request_id=request_id,
            method=request.method,
            url=str(request.url),
            path=request.url.path,
            status_code=response.status_code,
            duration_ms=round(duration * 1000, 2),
            response_headers=dict(response.headers),
            body=response_body,
            timestamp=datetime.utcnow().isoformat()
        )
    
    async def _log_error(
        self, 
        request: Request, 
        error: Exception, 
        request_id: str, 
        duration: float
    ):
        """Log request error."""
        logger.error(
            "HTTP request failed",
            request_id=request_id,
            method=request.method,
            url=str(request.url),
            path=request.url.path,
            error_type=type(error).__name__,
            error_message=str(error),
            duration_ms=round(duration * 1000, 2),
            timestamp=datetime.utcnow().isoformat(),
            exc_info=True
        )

class AccessLogMiddleware:
    """Simple access log middleware for basic request logging."""
    
    def __init__(self, skip_paths: Optional[list] = None):
        self.skip_paths = skip_paths or ["/health", "/metrics"]
    
    async def __call__(self, request: Request, call_next: Callable):
        """Log basic access information."""
        if request.url.path in self.skip_paths:
            return await call_next(request)
        
        start_time = time.time()
        
        # Get client IP
        client_ip = request.client.host
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            client_ip = forwarded_for.split(",")[0].strip()
        
        try:
            response = await call_next(request)
            duration = time.time() - start_time
            
            # Log in Apache Common Log Format style
            logger.info(
                f'{client_ip} - - [{datetime.utcnow().strftime("%d/%b/%Y:%H:%M:%S +0000")}] '
                f'"{request.method} {request.url.path} HTTP/1.1" {response.status_code} '
                f'- "{request.headers.get("Referer", "-")}" '
                f'"{request.headers.get("User-Agent", "-")}" {duration:.3f}s'
            )
            
            return response
            
        except Exception as e:
            duration = time.time() - start_time
            
            logger.error(
                f'{client_ip} - - [{datetime.utcnow().strftime("%d/%b/%Y:%H:%M:%S +0000")}] '
                f'"{request.method} {request.url.path} HTTP/1.1" 500 '
                f'- "{request.headers.get("Referer", "-")}" '
                f'"{request.headers.get("User-Agent", "-")}" {duration:.3f}s ERROR: {str(e)}'
            )
            
            raise

class SecurityLogMiddleware:
    """Security-focused logging middleware."""
    
    def __init__(self):
        self.security_events = [
            "authentication_failure",
            "authorization_failure", 
            "suspicious_request",
            "rate_limit_exceeded",
            "invalid_token",
            "sql_injection_attempt",
            "xss_attempt"
        ]
    
    async def __call__(self, request: Request, call_next: Callable):
        """Monitor for security events."""
        client_ip = request.client.host
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            client_ip = forwarded_for.split(",")[0].strip()
        
        # Check for suspicious patterns
        suspicious_patterns = await self._check_suspicious_patterns(request)
        
        if suspicious_patterns:
            logger.warning(
                "Suspicious request detected",
                client_ip=client_ip,
                url=str(request.url),
                patterns=suspicious_patterns,
                user_agent=request.headers.get("User-Agent"),
                timestamp=datetime.utcnow().isoformat()
            )
        
        try:
            response = await call_next(request)
            
            # Check for security-related status codes
            if response.status_code in [401, 403, 429]:
                logger.warning(
                    "Security event detected",
                    event_type="access_denied",
                    status_code=response.status_code,
                    client_ip=client_ip,
                    url=str(request.url),
                    timestamp=datetime.utcnow().isoformat()
                )
            
            return response
            
        except Exception as e:
            logger.error(
                "Request processing error",
                client_ip=client_ip,
                url=str(request.url),
                error=str(e),
                timestamp=datetime.utcnow().isoformat()
            )
            raise
    
    async def _check_suspicious_patterns(self, request: Request) -> list:
        """Check for suspicious request patterns."""
        suspicious = []
        
        url_str = str(request.url).lower()
        
        # SQL injection patterns
        sql_patterns = ["union select", "drop table", "insert into", "delete from", "' or '1'='1"]
        if any(pattern in url_str for pattern in sql_patterns):
            suspicious.append("sql_injection_attempt")
        
        # XSS patterns
        xss_patterns = ["<script>", "javascript:", "onerror=", "onload="]
        if any(pattern in url_str for pattern in xss_patterns):
            suspicious.append("xss_attempt")
        
        # Path traversal
        if "../" in url_str or "..%2f" in url_str:
            suspicious.append("path_traversal_attempt")
        
        # Large request size
        content_length = request.headers.get("Content-Length")
        if content_length and int(content_length) > 10 * 1024 * 1024:  # 10MB
            suspicious.append("large_request_body")
        
        # Unusual user agents
        user_agent = request.headers.get("User-Agent", "").lower()
        suspicious_agents = ["sqlmap", "nikto", "nmap", "masscan"]
        if any(agent in user_agent for agent in suspicious_agents):
            suspicious.append("suspicious_user_agent")
        
        return suspicious

def create_logging_middleware(
    log_level: str = "info",
    log_requests: bool = True,
    log_responses: bool = False
) -> LoggingMiddleware:
    """Create logging middleware with specified configuration."""
    return LoggingMiddleware(
        log_request_body=log_requests,
        log_response_body=log_responses
    )
