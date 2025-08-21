"""
Common Pydantic schemas for shared data structures.
"""

from datetime import datetime
from typing import Any, Dict, Generic, List, Optional, TypeVar
from pydantic import BaseModel, Field


class StatusResponse(BaseModel):
    """Standard status response."""
    success: bool = Field(..., description="Whether the operation was successful")
    message: str = Field(..., description="Status message")
    data: Optional[Dict[str, Any]] = Field(None, description="Additional data")


class ErrorResponse(BaseModel):
    """Standard error response."""
    error: bool = Field(True, description="Indicates this is an error response")
    message: str = Field(..., description="Error message")
    code: Optional[str] = Field(None, description="Error code")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional error details")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Error timestamp")


T = TypeVar('T')


class PaginatedResponse(BaseModel, Generic[T]):
    """Paginated response wrapper."""
    items: List[T] = Field(..., description="List of items")
    total: int = Field(..., description="Total number of items")
    page: int = Field(..., description="Current page number")
    size: int = Field(..., description="Number of items per page")
    pages: int = Field(..., description="Total number of pages")
    has_next: bool = Field(..., description="Whether there are more pages")
    has_prev: bool = Field(..., description="Whether there are previous pages")


class HealthResponse(BaseModel):
    """Health check response."""
    status: str = Field(..., description="Overall health status")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Health check timestamp")
    version: str = Field(..., description="Application version")
    uptime_seconds: float = Field(..., description="Application uptime in seconds")
    
    # System metrics
    cpu_usage_percent: Optional[float] = Field(None, description="CPU usage percentage")
    memory_usage_percent: Optional[float] = Field(None, description="Memory usage percentage")
    disk_usage_percent: Optional[float] = Field(None, description="Disk usage percentage")
    
    # Service checks
    database_status: str = Field(..., description="Database connection status")
    redis_status: Optional[str] = Field(None, description="Redis connection status")
    
    # Application metrics
    active_jobs: Optional[int] = Field(None, description="Number of active jobs")
    queue_size: Optional[int] = Field(None, description="Job queue size")
    
    # Detailed checks (for detailed health endpoint)
    checks: Optional[Dict[str, Dict[str, Any]]] = Field(None, description="Detailed health checks")


class MetricsResponse(BaseModel):
    """Metrics response for monitoring."""
    metrics: Dict[str, Any] = Field(..., description="Application metrics")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Metrics timestamp")
    

class ValidationErrorDetail(BaseModel):
    """Validation error detail."""
    field: str = Field(..., description="Field name with error")
    message: str = Field(..., description="Error message")
    value: Any = Field(None, description="Invalid value")


class ValidationErrorResponse(BaseModel):
    """Validation error response."""
    error: bool = Field(True, description="Indicates this is an error response")
    message: str = Field("Validation error", description="Error message")
    errors: List[ValidationErrorDetail] = Field(..., description="List of validation errors")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Error timestamp")


class RateLimitResponse(BaseModel):
    """Rate limit response."""
    error: bool = Field(True, description="Indicates this is an error response")
    message: str = Field("Rate limit exceeded", description="Error message")
    retry_after: int = Field(..., description="Seconds to wait before retry")
    limit: int = Field(..., description="Rate limit threshold")
    window: int = Field(..., description="Rate limit window in seconds")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Error timestamp")


class BulkOperationResponse(BaseModel):
    """Response for bulk operations."""
    total_requested: int = Field(..., description="Total number of items requested")
    successful: int = Field(..., description="Number of successful operations")
    failed: int = Field(..., description="Number of failed operations")
    errors: List[Dict[str, Any]] = Field(default_factory=list, description="List of errors")
    results: List[Dict[str, Any]] = Field(default_factory=list, description="Operation results")


class FileUploadResponse(BaseModel):
    """File upload response."""
    filename: str = Field(..., description="Uploaded filename")
    size: int = Field(..., description="File size in bytes")
    content_type: str = Field(..., description="File content type")
    url: Optional[str] = Field(None, description="File URL if available")
    checksum: Optional[str] = Field(None, description="File checksum")
    
    
class ExportResponse(BaseModel):
    """Data export response."""
    export_id: str = Field(..., description="Export operation ID")
    format: str = Field(..., description="Export format")
    status: str = Field(..., description="Export status")
    download_url: Optional[str] = Field(None, description="Download URL when ready")
    expires_at: Optional[datetime] = Field(None, description="Download URL expiration")
    file_size: Optional[int] = Field(None, description="File size in bytes")
    records_count: Optional[int] = Field(None, description="Number of exported records")


class SearchResponse(BaseModel, Generic[T]):
    """Search response wrapper."""
    query: str = Field(..., description="Search query")
    results: List[T] = Field(..., description="Search results")
    total_results: int = Field(..., description="Total number of results")
    page: int = Field(..., description="Current page number")
    size: int = Field(..., description="Number of results per page")
    search_time_ms: float = Field(..., description="Search time in milliseconds")
    filters: Optional[Dict[str, Any]] = Field(None, description="Applied filters")
    
    
class BatchJobResponse(BaseModel):
    """Batch job response."""
    batch_id: str = Field(..., description="Batch operation ID")
    job_count: int = Field(..., description="Number of jobs in batch")
    status: str = Field(..., description="Batch status")
    created_jobs: List[str] = Field(..., description="List of created job IDs")
    failed_jobs: List[Dict[str, Any]] = Field(default_factory=list, description="Failed job creations")


class ConfigurationResponse(BaseModel):
    """Configuration response."""
    section: str = Field(..., description="Configuration section")
    settings: Dict[str, Any] = Field(..., description="Configuration settings")
    editable: bool = Field(..., description="Whether settings can be modified")
    requires_restart: bool = Field(False, description="Whether changes require restart")


class SystemInfoResponse(BaseModel):
    """System information response."""
    application: Dict[str, Any] = Field(..., description="Application information")
    system: Dict[str, Any] = Field(..., description="System information")
    runtime: Dict[str, Any] = Field(..., description="Runtime information")
    environment: Dict[str, Any] = Field(..., description="Environment information")
    
    
class MaintenanceResponse(BaseModel):
    """Maintenance mode response."""
    maintenance_mode: bool = Field(..., description="Whether maintenance mode is active")
    message: Optional[str] = Field(None, description="Maintenance message")
    estimated_duration: Optional[str] = Field(None, description="Estimated maintenance duration")
    allowed_operations: List[str] = Field(default_factory=list, description="Operations allowed during maintenance")
