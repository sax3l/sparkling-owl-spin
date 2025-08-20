from typing import Optional, Dict, Any
from pydantic import BaseModel, Field

class ErrorDetail(BaseModel):
    field: Optional[str] = None
    reason: Optional[str] = None
    code: Optional[str] = None # Specific error code for the detail

class ErrorResponse(BaseModel):
    code: str = Field(..., description="A unique error code (e.g., VALIDATION_FAILED, NOT_FOUND).")
    message: str = Field(..., description="A human-readable error message.")
    details: Optional[Dict[str, Any]] = Field(None, description="Optional: More specific details about the error, e.g., validation errors per field.")
    request_id: Optional[str] = Field(None, description="A unique ID for the request, useful for tracing and support.")