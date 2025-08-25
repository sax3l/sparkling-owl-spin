"""
Lovable Backend Exception Handlers

Custom exceptions and error handling.
"""

from typing import Any, Dict, Optional
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
import logging

logger = logging.getLogger(__name__)


class LovableException(Exception):
    """Base exception for Lovable backend."""
    
    def __init__(self, message: str, code: Optional[str] = None, details: Any = None):
        self.message = message
        self.code = code
        self.details = details
        super().__init__(self.message)


class AuthenticationError(LovableException):
    """Authentication failed."""
    pass


class AuthorizationError(LovableException):
    """Authorization failed."""
    pass


class ValidationError(LovableException):
    """Validation failed."""
    pass


class NotFoundError(LovableException):
    """Resource not found."""
    pass


class ConflictError(LovableException):
    """Resource conflict."""
    pass


class RateLimitError(LovableException):
    """Rate limit exceeded."""
    pass


class ServiceUnavailableError(LovableException):
    """Service unavailable."""
    pass


async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """Handle HTTP exceptions."""
    logger.warning(f"HTTP exception: {exc.status_code} - {exc.detail}")
    
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error": "HTTP_ERROR",
            "message": exc.detail,
            "status_code": exc.status_code
        }
    )


async def starlette_exception_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
    """Handle Starlette HTTP exceptions."""
    logger.warning(f"Starlette exception: {exc.status_code} - {exc.detail}")
    
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error": "HTTP_ERROR",
            "message": exc.detail,
            "status_code": exc.status_code
        }
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """Handle validation exceptions."""
    logger.warning(f"Validation error: {exc.errors()}")
    
    # Format validation errors
    errors = []
    for error in exc.errors():
        field = '.'.join(str(loc) for loc in error['loc'][1:])  # Skip 'body' prefix
        errors.append({
            "field": field,
            "message": error['msg'],
            "type": error['type']
        })
    
    return JSONResponse(
        status_code=422,
        content={
            "success": False,
            "error": "VALIDATION_ERROR",
            "message": "Validation failed",
            "details": errors
        }
    )


async def lovable_exception_handler(request: Request, exc: LovableException) -> JSONResponse:
    """Handle custom Lovable exceptions."""
    logger.warning(f"Lovable exception: {exc.code} - {exc.message}")
    
    # Map exception types to HTTP status codes
    status_code_map = {
        AuthenticationError: 401,
        AuthorizationError: 403,
        NotFoundError: 404,
        ConflictError: 409,
        ValidationError: 422,
        RateLimitError: 429,
        ServiceUnavailableError: 503
    }
    
    status_code = status_code_map.get(type(exc), 500)
    
    response_content = {
        "success": False,
        "error": exc.code or type(exc).__name__.upper(),
        "message": exc.message
    }
    
    if exc.details:
        response_content["details"] = exc.details
    
    return JSONResponse(
        status_code=status_code,
        content=response_content
    )


async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle general exceptions."""
    logger.error(f"Unhandled exception: {type(exc).__name__} - {str(exc)}")
    
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": "INTERNAL_SERVER_ERROR",
            "message": "An unexpected error occurred"
        }
    )


def setup_exception_handlers(app):
    """Setup exception handlers for FastAPI app."""
    app.add_exception_handler(HTTPException, http_exception_handler)
    app.add_exception_handler(StarletteHTTPException, starlette_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(LovableException, lovable_exception_handler)
    app.add_exception_handler(Exception, general_exception_handler)
