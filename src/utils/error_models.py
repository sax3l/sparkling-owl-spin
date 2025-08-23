from typing import Optional, Dict, Any
from pydantic import BaseModel, Field
import logging
import traceback


class ErrorDetail(BaseModel):
    field: Optional[str] = None
    reason: Optional[str] = None
    code: Optional[str] = None # Specific error code for the detail


class ErrorResponse(BaseModel):
    code: str = Field(..., description="A unique error code (e.g., VALIDATION_FAILED, NOT_FOUND).")
    message: str = Field(..., description="A human-readable error message.")
    details: Optional[Dict[str, Any]] = Field(None, description="Optional: More specific details about the error, e.g., validation errors per field.")
    request_id: Optional[str] = Field(None, description="A unique ID for the request, useful for tracing and support.")


class CustomException(Exception):
    """Base custom exception class."""
    
    def __init__(self, message: str, code: str = "GENERAL_ERROR", details: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.message = message
        self.code = code
        self.details = details or {}


class ErrorHandler:
    """Error handling utility class."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def handle_exception(self, error: Exception, context: Optional[Dict[str, Any]] = None) -> ErrorResponse:
        """Handle an exception and return an ErrorResponse."""
        context = context or {}
        
        if isinstance(error, CustomException):
            return ErrorResponse(
                code=error.code,
                message=error.message,
                details=error.details,
                request_id=context.get('request_id')
            )
        
        # Log unexpected errors
        self.logger.error(f"Unexpected error: {str(error)}", exc_info=True)
        
        return ErrorResponse(
            code="INTERNAL_ERROR",
            message="An internal error occurred",
            details={"error_type": type(error).__name__, "trace": traceback.format_exc()},
            request_id=context.get('request_id')
        )
    
    def create_validation_error(self, field_errors: Dict[str, str], request_id: Optional[str] = None) -> ErrorResponse:
        """Create a validation error response."""
        return ErrorResponse(
            code="VALIDATION_ERROR",
            message="Validation failed",
            details=field_errors,
            request_id=request_id
        )