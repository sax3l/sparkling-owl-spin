"""
Error handling middleware and exception handlers for the FastAPI application.
"""
import traceback
import sys
from typing import Dict, Any, Optional, Callable, Union
from fastapi import Request, Response, HTTPException
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError, ResponseValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.status import HTTP_500_INTERNAL_SERVER_ERROR
import structlog
from datetime import datetime
import uuid

logger = structlog.get_logger(__name__)

class ErrorHandlingMiddleware:
    """Comprehensive error handling middleware."""
    
    def __init__(
        self,
        include_stack_trace: bool = False,
        log_errors: bool = True,
        custom_error_handlers: Optional[Dict[type, Callable]] = None
    ):
        self.include_stack_trace = include_stack_trace
        self.log_errors = log_errors
        self.custom_error_handlers = custom_error_handlers or {}
    
    async def __call__(self, request: Request, call_next: Callable):
        """Handle all unhandled exceptions."""
        try:
            return await call_next(request)
        except Exception as e:
            return await self._handle_exception(request, e)
    
    async def _handle_exception(self, request: Request, exc: Exception) -> JSONResponse:
        """Handle an exception and return appropriate response."""
        error_id = str(uuid.uuid4())
        
        # Check for custom handlers
        for exc_type, handler in self.custom_error_handlers.items():
            if isinstance(exc, exc_type):
                return await handler(request, exc, error_id)
        
        # Default handling
        if isinstance(exc, HTTPException):
            return await self._handle_http_exception(request, exc, error_id)
        elif isinstance(exc, RequestValidationError):
            return await self._handle_validation_error(request, exc, error_id)
        else:
            return await self._handle_generic_exception(request, exc, error_id)
    
    async def _handle_http_exception(
        self, 
        request: Request, 
        exc: HTTPException, 
        error_id: str
    ) -> JSONResponse:
        """Handle HTTP exceptions."""
        error_data = {
            "error": {
                "type": "http_error",
                "code": exc.status_code,
                "message": exc.detail,
                "error_id": error_id,
                "timestamp": datetime.utcnow().isoformat()
            }
        }
        
        # Log error if enabled
        if self.log_errors:
            logger.warning(
                "HTTP exception occurred",
                error_id=error_id,
                status_code=exc.status_code,
                detail=exc.detail,
                path=request.url.path,
                method=request.method,
                client_ip=request.client.host if request.client else None
            )
        
        return JSONResponse(
            status_code=exc.status_code,
            content=error_data
        )
    
    async def _handle_validation_error(
        self, 
        request: Request, 
        exc: RequestValidationError, 
        error_id: str
    ) -> JSONResponse:
        """Handle request validation errors."""
        error_data = {
            "error": {
                "type": "validation_error",
                "code": 422,
                "message": "Request validation failed",
                "details": exc.errors(),
                "error_id": error_id,
                "timestamp": datetime.utcnow().isoformat()
            }
        }
        
        # Log validation error
        if self.log_errors:
            logger.warning(
                "Request validation error",
                error_id=error_id,
                validation_errors=exc.errors(),
                path=request.url.path,
                method=request.method,
                client_ip=request.client.host if request.client else None
            )
        
        return JSONResponse(
            status_code=422,
            content=error_data
        )
    
    async def _handle_generic_exception(
        self, 
        request: Request, 
        exc: Exception, 
        error_id: str
    ) -> JSONResponse:
        """Handle generic unhandled exceptions."""
        error_data = {
            "error": {
                "type": "internal_server_error",
                "code": 500,
                "message": "An internal server error occurred",
                "error_id": error_id,
                "timestamp": datetime.utcnow().isoformat()
            }
        }
        
        # Include stack trace if enabled
        if self.include_stack_trace:
            error_data["error"]["stack_trace"] = traceback.format_exc()
        
        # Log error
        if self.log_errors:
            logger.error(
                "Unhandled exception occurred",
                error_id=error_id,
                exception_type=type(exc).__name__,
                exception_message=str(exc),
                path=request.url.path,
                method=request.method,
                client_ip=request.client.host if request.client else None,
                exc_info=True
            )
        
        return JSONResponse(
            status_code=500,
            content=error_data
        )

# Custom exception classes
class CrawlerException(Exception):
    """Base exception for crawler-related errors."""
    def __init__(self, message: str, error_code: Optional[str] = None):
        self.message = message
        self.error_code = error_code
        super().__init__(message)

class ScrapingException(CrawlerException):
    """Exception for scraping-related errors."""
    pass

class RateLimitExceededException(CrawlerException):
    """Exception for rate limit violations."""
    def __init__(self, message: str = "Rate limit exceeded", retry_after: Optional[int] = None):
        super().__init__(message)
        self.retry_after = retry_after

class AuthenticationException(CrawlerException):
    """Exception for authentication failures."""
    pass

class AuthorizationException(CrawlerException):
    """Exception for authorization failures."""
    pass

class DataValidationException(CrawlerException):
    """Exception for data validation errors."""
    def __init__(self, message: str, field: Optional[str] = None, value: Any = None):
        super().__init__(message)
        self.field = field
        self.value = value

class ExternalServiceException(CrawlerException):
    """Exception for external service errors."""
    def __init__(self, message: str, service: str, status_code: Optional[int] = None):
        super().__init__(message)
        self.service = service
        self.status_code = status_code

# Exception handlers
async def crawler_exception_handler(
    request: Request, 
    exc: CrawlerException, 
    error_id: str
) -> JSONResponse:
    """Handle crawler-specific exceptions."""
    status_code = 400
    
    if isinstance(exc, AuthenticationException):
        status_code = 401
    elif isinstance(exc, AuthorizationException):
        status_code = 403
    elif isinstance(exc, RateLimitExceededException):
        status_code = 429
    elif isinstance(exc, ExternalServiceException):
        status_code = 502
    
    error_data = {
        "error": {
            "type": type(exc).__name__.lower(),
            "code": status_code,
            "message": exc.message,
            "error_code": getattr(exc, 'error_code', None),
            "error_id": error_id,
            "timestamp": datetime.utcnow().isoformat()
        }
    }
    
    # Add specific fields for certain exceptions
    if isinstance(exc, RateLimitExceededException) and exc.retry_after:
        error_data["error"]["retry_after"] = exc.retry_after
    
    if isinstance(exc, DataValidationException):
        error_data["error"]["field"] = exc.field
        error_data["error"]["value"] = exc.value
    
    if isinstance(exc, ExternalServiceException):
        error_data["error"]["service"] = exc.service
        error_data["error"]["service_status_code"] = exc.status_code
    
    # Set Retry-After header for rate limit exceptions
    headers = {}
    if isinstance(exc, RateLimitExceededException) and exc.retry_after:
        headers["Retry-After"] = str(exc.retry_after)
    
    return JSONResponse(
        status_code=status_code,
        content=error_data,
        headers=headers
    )

async def database_exception_handler(
    request: Request, 
    exc: Exception, 
    error_id: str
) -> JSONResponse:
    """Handle database-related exceptions."""
    error_data = {
        "error": {
            "type": "database_error",
            "code": 503,
            "message": "Database service temporarily unavailable",
            "error_id": error_id,
            "timestamp": datetime.utcnow().isoformat()
        }
    }
    
    logger.error(
        "Database error occurred",
        error_id=error_id,
        exception_type=type(exc).__name__,
        exception_message=str(exc),
        path=request.url.path,
        method=request.method,
        exc_info=True
    )
    
    return JSONResponse(
        status_code=503,
        content=error_data,
        headers={"Retry-After": "30"}
    )

async def timeout_exception_handler(
    request: Request, 
    exc: Exception, 
    error_id: str
) -> JSONResponse:
    """Handle timeout exceptions."""
    error_data = {
        "error": {
            "type": "timeout_error",
            "code": 408,
            "message": "Request timeout",
            "error_id": error_id,
            "timestamp": datetime.utcnow().isoformat()
        }
    }
    
    return JSONResponse(
        status_code=408,
        content=error_data
    )

# Error response models
def create_error_response(
    status_code: int,
    message: str,
    error_type: str = "error",
    details: Optional[Dict[str, Any]] = None,
    error_code: Optional[str] = None
) -> JSONResponse:
    """Create a standardized error response."""
    error_data = {
        "error": {
            "type": error_type,
            "code": status_code,
            "message": message,
            "timestamp": datetime.utcnow().isoformat()
        }
    }
    
    if error_code:
        error_data["error"]["error_code"] = error_code
    
    if details:
        error_data["error"]["details"] = details
    
    return JSONResponse(
        status_code=status_code,
        content=error_data
    )

def create_validation_error_response(
    message: str = "Validation failed",
    field_errors: Optional[list] = None
) -> JSONResponse:
    """Create a validation error response."""
    return create_error_response(
        status_code=422,
        message=message,
        error_type="validation_error",
        details={"field_errors": field_errors} if field_errors else None
    )

def create_not_found_response(resource: str = "Resource") -> JSONResponse:
    """Create a not found error response."""
    return create_error_response(
        status_code=404,
        message=f"{resource} not found",
        error_type="not_found_error"
    )

def create_unauthorized_response(message: str = "Authentication required") -> JSONResponse:
    """Create an unauthorized error response."""
    return create_error_response(
        status_code=401,
        message=message,
        error_type="authentication_error"
    )

def create_forbidden_response(message: str = "Insufficient permissions") -> JSONResponse:
    """Create a forbidden error response."""
    return create_error_response(
        status_code=403,
        message=message,
        error_type="authorization_error"
    )

def setup_exception_handlers() -> Dict[Union[int, type], Callable]:
    """Setup all exception handlers for the FastAPI app."""
    custom_handlers = {
        CrawlerException: crawler_exception_handler,
        ScrapingException: crawler_exception_handler,
        RateLimitExceededException: crawler_exception_handler,
        AuthenticationException: crawler_exception_handler,
        AuthorizationException: crawler_exception_handler,
        DataValidationException: crawler_exception_handler,
        ExternalServiceException: crawler_exception_handler,
    }
    
    # Add database-specific handlers (these would be imported based on your DB library)
    try:
        import sqlalchemy.exc
        custom_handlers[sqlalchemy.exc.SQLAlchemyError] = database_exception_handler
    except ImportError:
        pass
    
    try:
        import asyncio
        custom_handlers[asyncio.TimeoutError] = timeout_exception_handler
    except ImportError:
        pass
    
    return custom_handlers

def create_error_middleware(
    environment: str = "production",
    include_debug_info: bool = None
) -> ErrorHandlingMiddleware:
    """Create error handling middleware based on environment."""
    if include_debug_info is None:
        include_debug_info = environment in ["development", "staging"]
    
    return ErrorHandlingMiddleware(
        include_stack_trace=include_debug_info,
        log_errors=True,
        custom_error_handlers=setup_exception_handlers()
    )
