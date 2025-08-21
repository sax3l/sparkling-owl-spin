"""
Job-related Pydantic schemas for API request/response validation.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field, HttpUrl, validator
from enum import Enum


class JobStatus(str, Enum):
    """Job status enumeration."""
    PENDING = "pending"
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    PAUSED = "paused"
    RETRYING = "retrying"


class JobPriority(str, Enum):
    """Job priority enumeration."""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"


class OutputFormat(str, Enum):
    """Output format enumeration."""
    JSON = "json"
    CSV = "csv"
    EXCEL = "excel"
    XML = "xml"


# Crawl Job Schemas

class CrawlJobCreate(BaseModel):
    """Schema for creating crawl jobs."""
    name: str = Field(..., min_length=1, max_length=255, description="Job name")
    description: Optional[str] = Field(None, max_length=1000, description="Job description")
    start_urls: List[HttpUrl] = Field(..., min_items=1, max_items=100, description="Starting URLs")
    max_pages: int = Field(100, ge=1, le=10000, description="Maximum pages to crawl")
    max_depth: int = Field(5, ge=1, le=20, description="Maximum crawl depth")
    concurrent_requests: int = Field(10, ge=1, le=50, description="Concurrent requests")
    
    # Domain filtering
    allowed_domains: Optional[List[str]] = Field(None, description="Allowed domains")
    forbidden_domains: Optional[List[str]] = Field(None, description="Forbidden domains")
    url_patterns: Optional[List[str]] = Field(None, description="URL regex patterns")
    content_types: List[str] = Field(["text/html"], description="Allowed content types")
    
    # Browser configuration
    use_browser: bool = Field(False, description="Use browser for JavaScript rendering")
    browser_type: str = Field("chromium", description="Browser type")
    headless: bool = Field(True, description="Run browser in headless mode")
    user_agent: Optional[str] = Field(None, max_length=500, description="Custom user agent")
    
    # Anti-bot measures
    randomize_delays: bool = Field(True, description="Randomize request delays")
    min_delay_seconds: float = Field(1.0, ge=0.1, le=60.0, description="Minimum delay")
    max_delay_seconds: float = Field(5.0, ge=0.1, le=60.0, description="Maximum delay")
    rotate_proxies: bool = Field(False, description="Rotate proxy servers")
    rotate_user_agents: bool = Field(False, description="Rotate user agents")
    
    # Scheduling and priority
    priority: JobPriority = Field(JobPriority.NORMAL, description="Job priority")
    scheduled_at: Optional[datetime] = Field(None, description="Schedule job for later")
    
    # Output configuration
    output_format: OutputFormat = Field(OutputFormat.JSON, description="Output format")
    
    @validator('max_delay_seconds')
    def validate_delays(cls, v, values):
        if 'min_delay_seconds' in values and v < values['min_delay_seconds']:
            raise ValueError('max_delay_seconds must be >= min_delay_seconds')
        return v


class CrawlJobUpdate(BaseModel):
    """Schema for updating crawl jobs."""
    name: Optional[str] = Field(None, min_length=1, max_length=255, description="Job name")
    description: Optional[str] = Field(None, max_length=1000, description="Job description")
    max_pages: Optional[int] = Field(None, ge=1, le=10000, description="Maximum pages")
    max_depth: Optional[int] = Field(None, ge=1, le=20, description="Maximum depth")
    priority: Optional[JobPriority] = Field(None, description="Job priority")
    scheduled_at: Optional[datetime] = Field(None, description="Reschedule job")
    

class CrawlJobResponse(BaseModel):
    """Schema for crawl job responses."""
    id: str = Field(..., description="Job ID")
    name: str = Field(..., description="Job name")
    description: Optional[str] = Field(None, description="Job description")
    start_urls: List[str] = Field(..., description="Starting URLs")
    max_pages: int = Field(..., description="Maximum pages to crawl")
    max_depth: int = Field(..., description="Maximum crawl depth")
    concurrent_requests: int = Field(..., description="Concurrent requests")
    
    # Domain filtering
    allowed_domains: Optional[List[str]] = Field(None, description="Allowed domains")
    forbidden_domains: Optional[List[str]] = Field(None, description="Forbidden domains")
    
    # Browser configuration
    use_browser: bool = Field(..., description="Using browser")
    browser_type: str = Field(..., description="Browser type")
    headless: bool = Field(..., description="Headless mode")
    
    # Anti-bot measures
    randomize_delays: bool = Field(..., description="Randomized delays")
    min_delay_seconds: float = Field(..., description="Minimum delay")
    max_delay_seconds: float = Field(..., description="Maximum delay")
    
    # Status and progress
    status: JobStatus = Field(..., description="Job status")
    priority: JobPriority = Field(..., description="Job priority")
    progress_percentage: float = Field(..., description="Progress percentage")
    pages_crawled: int = Field(..., description="Pages crawled")
    pages_found: int = Field(..., description="Pages found")
    errors_count: int = Field(..., description="Error count")
    results_count: int = Field(..., description="Results count")
    
    # Resource usage
    bandwidth_used_mb: float = Field(..., description="Bandwidth used (MB)")
    processing_time_seconds: float = Field(..., description="Processing time")
    
    # Timestamps
    created_at: datetime = Field(..., description="Creation timestamp")
    scheduled_at: Optional[datetime] = Field(None, description="Scheduled timestamp")
    started_at: Optional[datetime] = Field(None, description="Start timestamp")
    completed_at: Optional[datetime] = Field(None, description="Completion timestamp")
    
    # Error information
    error_message: Optional[str] = Field(None, description="Error message")
    retry_count: int = Field(..., description="Retry count")
    max_retries: int = Field(..., description="Maximum retries")
    
    # Output
    output_format: str = Field(..., description="Output format")
    output_location: Optional[str] = Field(None, description="Output location")
    
    # User
    user_id: str = Field(..., description="Owner user ID")
    
    class Config:
        from_attributes = True


# Scrape Job Schemas

class ScrapeJobCreate(BaseModel):
    """Schema for creating scrape jobs."""
    name: str = Field(..., min_length=1, max_length=255, description="Job name")
    description: Optional[str] = Field(None, max_length=1000, description="Job description")
    target_urls: List[HttpUrl] = Field(..., min_items=1, max_items=1000, description="Target URLs")
    template_name: str = Field(..., min_length=1, max_length=100, description="Scraping template")
    template_version: str = Field("latest", description="Template version")
    
    # Extraction configuration
    extract_fields: Optional[List[str]] = Field(None, description="Specific fields to extract")
    custom_selectors: Optional[Dict[str, str]] = Field(None, description="Custom selectors")
    data_transformations: Optional[Dict[str, Any]] = Field(None, description="Data transformations")
    
    # Browser configuration
    use_browser: bool = Field(True, description="Use browser for rendering")
    browser_type: str = Field("chromium", description="Browser type")
    headless: bool = Field(True, description="Headless mode")
    wait_for_selector: Optional[str] = Field(None, max_length=200, description="Wait for selector")
    page_load_timeout: int = Field(30, ge=5, le=300, description="Page load timeout")
    
    # Anti-bot measures
    randomize_delays: bool = Field(True, description="Randomize delays")
    min_delay_seconds: float = Field(2.0, ge=0.1, le=60.0, description="Minimum delay")
    max_delay_seconds: float = Field(8.0, ge=0.1, le=60.0, description="Maximum delay")
    use_proxies: bool = Field(False, description="Use proxy rotation")
    stealth_mode: bool = Field(True, description="Use stealth mode")
    
    # Scheduling and priority
    priority: JobPriority = Field(JobPriority.NORMAL, description="Job priority")
    scheduled_at: Optional[datetime] = Field(None, description="Schedule for later")
    
    # Output configuration
    output_format: OutputFormat = Field(OutputFormat.JSON, description="Output format")
    include_metadata: bool = Field(True, description="Include metadata")
    include_raw_html: bool = Field(False, description="Include raw HTML")
    
    @validator('max_delay_seconds')
    def validate_delays(cls, v, values):
        if 'min_delay_seconds' in values and v < values['min_delay_seconds']:
            raise ValueError('max_delay_seconds must be >= min_delay_seconds')
        return v


class ScrapeJobUpdate(BaseModel):
    """Schema for updating scrape jobs."""
    name: Optional[str] = Field(None, min_length=1, max_length=255, description="Job name")
    description: Optional[str] = Field(None, max_length=1000, description="Job description")
    template_name: Optional[str] = Field(None, min_length=1, max_length=100, description="Template")
    template_version: Optional[str] = Field(None, description="Template version")
    priority: Optional[JobPriority] = Field(None, description="Job priority")
    scheduled_at: Optional[datetime] = Field(None, description="Reschedule job")


class ScrapeJobResponse(BaseModel):
    """Schema for scrape job responses."""
    id: str = Field(..., description="Job ID")
    name: str = Field(..., description="Job name")
    description: Optional[str] = Field(None, description="Job description")
    target_urls: List[str] = Field(..., description="Target URLs")
    template_name: str = Field(..., description="Scraping template")
    template_version: str = Field(..., description="Template version")
    
    # Extraction configuration
    extract_fields: Optional[List[str]] = Field(None, description="Extract fields")
    
    # Browser configuration
    use_browser: bool = Field(..., description="Using browser")
    browser_type: str = Field(..., description="Browser type")
    headless: bool = Field(..., description="Headless mode")
    wait_for_selector: Optional[str] = Field(None, description="Wait selector")
    page_load_timeout: int = Field(..., description="Page load timeout")
    
    # Anti-bot measures
    randomize_delays: bool = Field(..., description="Randomized delays")
    min_delay_seconds: float = Field(..., description="Minimum delay")
    max_delay_seconds: float = Field(..., description="Maximum delay")
    use_proxies: bool = Field(..., description="Using proxies")
    stealth_mode: bool = Field(..., description="Stealth mode")
    
    # Status and progress
    status: JobStatus = Field(..., description="Job status")
    priority: JobPriority = Field(..., description="Job priority")
    progress_percentage: float = Field(..., description="Progress percentage")
    success_rate: float = Field(..., description="Success rate percentage")
    pages_processed: int = Field(..., description="Pages processed")
    pages_successful: int = Field(..., description="Successful pages")
    pages_failed: int = Field(..., description="Failed pages")
    
    # Data extraction
    records_extracted: int = Field(..., description="Records extracted")
    fields_extracted: int = Field(..., description="Fields extracted")
    data_quality_score: Optional[float] = Field(None, description="Data quality score")
    
    # Resource usage
    bandwidth_used_mb: float = Field(..., description="Bandwidth used (MB)")
    processing_time_seconds: float = Field(..., description="Processing time")
    browser_sessions_used: int = Field(..., description="Browser sessions used")
    
    # Timestamps
    created_at: datetime = Field(..., description="Creation timestamp")
    scheduled_at: Optional[datetime] = Field(None, description="Scheduled timestamp")
    started_at: Optional[datetime] = Field(None, description="Start timestamp")
    completed_at: Optional[datetime] = Field(None, description="Completion timestamp")
    
    # Error information
    error_message: Optional[str] = Field(None, description="Error message")
    retry_count: int = Field(..., description="Retry count")
    max_retries: int = Field(..., description="Maximum retries")
    
    # Output
    output_format: str = Field(..., description="Output format")
    output_location: Optional[str] = Field(None, description="Output location")
    include_metadata: bool = Field(..., description="Include metadata")
    include_raw_html: bool = Field(..., description="Include raw HTML")
    
    # User
    user_id: str = Field(..., description="Owner user ID")
    
    class Config:
        from_attributes = True


# Common Job Schemas

class JobSummary(BaseModel):
    """Schema for job summary information."""
    id: str = Field(..., description="Job ID")
    name: str = Field(..., description="Job name")
    type: str = Field(..., description="Job type (crawl/scrape)")
    status: JobStatus = Field(..., description="Job status")
    priority: JobPriority = Field(..., description="Job priority")
    progress_percentage: float = Field(..., description="Progress percentage")
    created_at: datetime = Field(..., description="Creation timestamp")
    started_at: Optional[datetime] = Field(None, description="Start timestamp")
    completed_at: Optional[datetime] = Field(None, description="Completion timestamp")
    user_id: str = Field(..., description="Owner user ID")


class JobFilter(BaseModel):
    """Schema for filtering jobs."""
    status: Optional[JobStatus] = Field(None, description="Filter by status")
    priority: Optional[JobPriority] = Field(None, description="Filter by priority")
    user_id: Optional[str] = Field(None, description="Filter by user")
    created_after: Optional[datetime] = Field(None, description="Created after date")
    created_before: Optional[datetime] = Field(None, description="Created before date")
    job_type: Optional[str] = Field(None, description="Filter by job type")


class JobStats(BaseModel):
    """Schema for job statistics."""
    total_jobs: int = Field(..., description="Total number of jobs")
    pending_jobs: int = Field(..., description="Pending jobs")
    running_jobs: int = Field(..., description="Running jobs")
    completed_jobs: int = Field(..., description="Completed jobs")
    failed_jobs: int = Field(..., description="Failed jobs")
    success_rate: float = Field(..., description="Success rate percentage")
    average_processing_time: float = Field(..., description="Average processing time")
    total_bandwidth_used: float = Field(..., description="Total bandwidth used (MB)")


class JobBulkAction(BaseModel):
    """Schema for bulk job actions."""
    job_ids: List[str] = Field(..., min_items=1, description="List of job IDs")
    action: str = Field(..., description="Action to perform")
    
    @validator('action')
    def validate_action(cls, v):
        valid_actions = ["cancel", "pause", "resume", "retry", "delete"]
        if v not in valid_actions:
            raise ValueError(f'Invalid action: {v}')
        return v


class JobBulkActionResponse(BaseModel):
    """Schema for bulk job action responses."""
    total_requested: int = Field(..., description="Total jobs requested")
    successful: int = Field(..., description="Successfully processed jobs")
    failed: int = Field(..., description="Failed job operations")
    results: List[Dict[str, Any]] = Field(..., description="Detailed results")


class JobTemplate(BaseModel):
    """Schema for job templates."""
    name: str = Field(..., description="Template name")
    description: str = Field(..., description="Template description")
    job_type: str = Field(..., description="Job type (crawl/scrape)")
    default_config: Dict[str, Any] = Field(..., description="Default configuration")
    

class JobSchedule(BaseModel):
    """Schema for job scheduling."""
    name: str = Field(..., description="Schedule name")
    cron_expression: str = Field(..., description="Cron expression")
    job_template: str = Field(..., description="Job template to use")
    enabled: bool = Field(True, description="Whether schedule is enabled")
    next_run: Optional[datetime] = Field(None, description="Next scheduled run")


class JobExport(BaseModel):
    """Schema for job data export."""
    job_ids: List[str] = Field(..., description="Job IDs to export")
    format: OutputFormat = Field(OutputFormat.JSON, description="Export format")
    include_results: bool = Field(True, description="Include job results")
    include_logs: bool = Field(False, description="Include job logs")
    
    
class TemplateValidation(BaseModel):
    """Schema for template validation."""
    template_name: str = Field(..., description="Template name")
    test_urls: List[HttpUrl] = Field(..., min_items=1, description="URLs to test with")
    validate_selectors: bool = Field(True, description="Validate CSS selectors")
    validate_data_types: bool = Field(True, description="Validate data types")
