"""
Job models for crawler and scraper operations.
"""

import json
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
from enum import Enum

from sqlalchemy import Column, String, Boolean, DateTime, Text, Integer, Float, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID, JSONB

from .base import BaseModel


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


class CrawlJob(BaseModel):
    """Crawl job model for web crawling operations."""
    
    __tablename__ = "crawl_jobs"
    
    # Job identification
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    
    # Job configuration
    start_urls = Column(JSONB, nullable=False)  # List of URLs to start crawling
    max_pages = Column(Integer, default=100, nullable=False)
    max_depth = Column(Integer, default=5, nullable=False)
    concurrent_requests = Column(Integer, default=10, nullable=False)
    
    # Crawl rules and filters
    allowed_domains = Column(Text, nullable=True)  # Comma-separated domains
    forbidden_domains = Column(Text, nullable=True)  # Comma-separated domains
    url_patterns = Column(JSONB, nullable=True)  # Regex patterns for URL filtering
    content_types = Column(Text, default="text/html", nullable=False)  # Allowed content types
    
    # Browser configuration
    use_browser = Column(Boolean, default=False, nullable=False)
    browser_type = Column(String(20), default="chromium", nullable=False)
    headless = Column(Boolean, default=True, nullable=False)
    user_agent = Column(String(500), nullable=True)
    
    # Anti-bot measures
    randomize_delays = Column(Boolean, default=True, nullable=False)
    min_delay_seconds = Column(Float, default=1.0, nullable=False)
    max_delay_seconds = Column(Float, default=5.0, nullable=False)
    rotate_proxies = Column(Boolean, default=False, nullable=False)
    rotate_user_agents = Column(Boolean, default=False, nullable=False)
    
    # Status and scheduling
    status = Column(SQLEnum(JobStatus), default=JobStatus.PENDING, nullable=False)
    priority = Column(SQLEnum(JobPriority), default=JobPriority.NORMAL, nullable=False)
    scheduled_at = Column(DateTime(timezone=True), nullable=True)
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Progress tracking
    pages_crawled = Column(Integer, default=0, nullable=False)
    pages_found = Column(Integer, default=0, nullable=False)
    errors_count = Column(Integer, default=0, nullable=False)
    
    # Resource usage
    bandwidth_used_mb = Column(Float, default=0.0, nullable=False)
    processing_time_seconds = Column(Float, default=0.0, nullable=False)
    
    # Results and output
    output_format = Column(String(20), default="json", nullable=False)
    output_location = Column(String(500), nullable=True)  # File path or storage location
    results_count = Column(Integer, default=0, nullable=False)
    
    # Error handling
    error_message = Column(Text, nullable=True)
    error_details = Column(JSONB, nullable=True)
    retry_count = Column(Integer, default=0, nullable=False)
    max_retries = Column(Integer, default=3, nullable=False)
    
    # User association
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    user = relationship("User")
    
    def get_start_urls(self) -> List[str]:
        """Get list of start URLs."""
        if isinstance(self.start_urls, list):
            return self.start_urls
        return []
    
    def get_allowed_domains(self) -> List[str]:
        """Get list of allowed domains."""
        if not self.allowed_domains:
            return []
        return [domain.strip() for domain in self.allowed_domains.split(",")]
    
    def get_forbidden_domains(self) -> List[str]:
        """Get list of forbidden domains."""
        if not self.forbidden_domains:
            return []
        return [domain.strip() for domain in self.forbidden_domains.split(",")]
    
    def is_url_allowed(self, url: str) -> bool:
        """Check if URL is allowed for crawling."""
        from urllib.parse import urlparse
        
        domain = urlparse(url).netloc
        
        # Check forbidden domains first
        forbidden = self.get_forbidden_domains()
        if forbidden and any(domain.endswith(fd) for fd in forbidden):
            return False
            
        # Check allowed domains
        allowed = self.get_allowed_domains()
        if allowed:
            return any(domain.endswith(ad) for ad in allowed)
            
        return True
    
    def start_job(self) -> None:
        """Mark job as started."""
        self.status = JobStatus.RUNNING
        self.started_at = datetime.utcnow()
    
    def complete_job(self, results_count: int = 0) -> None:
        """Mark job as completed."""
        self.status = JobStatus.COMPLETED
        self.completed_at = datetime.utcnow()
        self.results_count = results_count
        
        if self.started_at:
            self.processing_time_seconds = (self.completed_at - self.started_at).total_seconds()
    
    def fail_job(self, error_message: str, error_details: Dict[str, Any] = None) -> None:
        """Mark job as failed."""
        self.status = JobStatus.FAILED
        self.error_message = error_message
        self.error_details = error_details
        self.completed_at = datetime.utcnow()
    
    def cancel_job(self) -> None:
        """Cancel the job."""
        self.status = JobStatus.CANCELLED
        self.completed_at = datetime.utcnow()
    
    def retry_job(self) -> bool:
        """Attempt to retry the job."""
        if self.retry_count >= self.max_retries:
            return False
            
        self.retry_count += 1
        self.status = JobStatus.RETRYING
        self.error_message = None
        self.error_details = None
        
        return True
    
    def update_progress(self, pages_crawled: int, pages_found: int, errors_count: int = 0) -> None:
        """Update job progress."""
        self.pages_crawled = pages_crawled
        self.pages_found = pages_found
        self.errors_count += errors_count
    
    def get_progress_percentage(self) -> float:
        """Calculate progress percentage."""
        if self.max_pages == 0:
            return 0.0
        return min((self.pages_crawled / self.max_pages) * 100, 100.0)
    
    def get_job_summary(self) -> Dict[str, Any]:
        """Get job summary."""
        return {
            "id": str(self.id),
            "name": self.name,
            "status": self.status.value,
            "priority": self.priority.value,
            "progress_percentage": self.get_progress_percentage(),
            "pages_crawled": self.pages_crawled,
            "pages_found": self.pages_found,
            "errors_count": self.errors_count,
            "results_count": self.results_count,
            "processing_time_seconds": self.processing_time_seconds,
            "bandwidth_used_mb": self.bandwidth_used_mb,
            "created_at": self.created_at.isoformat(),
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None
        }


class ScrapeJob(BaseModel):
    """Scrape job model for data extraction operations."""
    
    __tablename__ = "scrape_jobs"
    
    # Job identification
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    
    # Job configuration
    target_urls = Column(JSONB, nullable=False)  # List of URLs to scrape
    template_name = Column(String(100), nullable=False)  # Scraping template to use
    template_version = Column(String(20), default="latest", nullable=False)
    
    # Extraction configuration
    extract_fields = Column(JSONB, nullable=True)  # Specific fields to extract
    custom_selectors = Column(JSONB, nullable=True)  # Custom CSS/XPath selectors
    data_transformations = Column(JSONB, nullable=True)  # Data transformation rules
    
    # Browser configuration
    use_browser = Column(Boolean, default=True, nullable=False)
    browser_type = Column(String(20), default="chromium", nullable=False)
    headless = Column(Boolean, default=True, nullable=False)
    wait_for_selector = Column(String(200), nullable=True)
    page_load_timeout = Column(Integer, default=30, nullable=False)
    
    # Anti-bot measures
    randomize_delays = Column(Boolean, default=True, nullable=False)
    min_delay_seconds = Column(Float, default=2.0, nullable=False)
    max_delay_seconds = Column(Float, default=8.0, nullable=False)
    use_proxies = Column(Boolean, default=False, nullable=False)
    stealth_mode = Column(Boolean, default=True, nullable=False)
    
    # Status and scheduling
    status = Column(SQLEnum(JobStatus), default=JobStatus.PENDING, nullable=False)
    priority = Column(SQLEnum(JobPriority), default=JobPriority.NORMAL, nullable=False)
    scheduled_at = Column(DateTime(timezone=True), nullable=True)
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Progress tracking
    pages_processed = Column(Integer, default=0, nullable=False)
    pages_successful = Column(Integer, default=0, nullable=False)
    pages_failed = Column(Integer, default=0, nullable=False)
    
    # Data quality
    records_extracted = Column(Integer, default=0, nullable=False)
    fields_extracted = Column(Integer, default=0, nullable=False)
    data_quality_score = Column(Float, nullable=True)  # 0.0 to 1.0
    
    # Resource usage
    bandwidth_used_mb = Column(Float, default=0.0, nullable=False)
    processing_time_seconds = Column(Float, default=0.0, nullable=False)
    browser_sessions_used = Column(Integer, default=0, nullable=False)
    
    # Output configuration
    output_format = Column(String(20), default="json", nullable=False)
    output_location = Column(String(500), nullable=True)
    include_metadata = Column(Boolean, default=True, nullable=False)
    include_raw_html = Column(Boolean, default=False, nullable=False)
    
    # Error handling
    error_message = Column(Text, nullable=True)
    error_details = Column(JSONB, nullable=True)
    retry_count = Column(Integer, default=0, nullable=False)
    max_retries = Column(Integer, default=3, nullable=False)
    
    # User association
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    user = relationship("User")
    
    def get_target_urls(self) -> List[str]:
        """Get list of target URLs."""
        if isinstance(self.target_urls, list):
            return self.target_urls
        return []
    
    def get_extract_fields(self) -> List[str]:
        """Get list of fields to extract."""
        if isinstance(self.extract_fields, list):
            return self.extract_fields
        return []
    
    def start_job(self) -> None:
        """Mark job as started."""
        self.status = JobStatus.RUNNING
        self.started_at = datetime.utcnow()
    
    def complete_job(self, records_extracted: int = 0, data_quality_score: float = None) -> None:
        """Mark job as completed."""
        self.status = JobStatus.COMPLETED
        self.completed_at = datetime.utcnow()
        self.records_extracted = records_extracted
        
        if data_quality_score is not None:
            self.data_quality_score = data_quality_score
        
        if self.started_at:
            self.processing_time_seconds = (self.completed_at - self.started_at).total_seconds()
    
    def fail_job(self, error_message: str, error_details: Dict[str, Any] = None) -> None:
        """Mark job as failed."""
        self.status = JobStatus.FAILED
        self.error_message = error_message
        self.error_details = error_details
        self.completed_at = datetime.utcnow()
    
    def cancel_job(self) -> None:
        """Cancel the job."""
        self.status = JobStatus.CANCELLED
        self.completed_at = datetime.utcnow()
    
    def retry_job(self) -> bool:
        """Attempt to retry the job."""
        if self.retry_count >= self.max_retries:
            return False
            
        self.retry_count += 1
        self.status = JobStatus.RETRYING
        self.error_message = None
        self.error_details = None
        
        return True
    
    def update_progress(
        self, 
        pages_processed: int, 
        pages_successful: int, 
        pages_failed: int,
        records_extracted: int = None,
        fields_extracted: int = None
    ) -> None:
        """Update job progress."""
        self.pages_processed = pages_processed
        self.pages_successful = pages_successful
        self.pages_failed = pages_failed
        
        if records_extracted is not None:
            self.records_extracted = records_extracted
            
        if fields_extracted is not None:
            self.fields_extracted = fields_extracted
    
    def get_progress_percentage(self) -> float:
        """Calculate progress percentage."""
        total_urls = len(self.get_target_urls())
        if total_urls == 0:
            return 0.0
        return (self.pages_processed / total_urls) * 100
    
    def get_success_rate(self) -> float:
        """Calculate success rate."""
        if self.pages_processed == 0:
            return 0.0
        return (self.pages_successful / self.pages_processed) * 100
    
    def calculate_data_quality_score(self) -> float:
        """Calculate data quality score based on extraction success."""
        if self.records_extracted == 0:
            return 0.0
            
        expected_records = len(self.get_target_urls())
        if expected_records == 0:
            return 1.0
            
        # Base score on extraction success rate
        extraction_rate = min(self.records_extracted / expected_records, 1.0)
        
        # Adjust for field completeness if available
        expected_fields = len(self.get_extract_fields())
        if expected_fields > 0 and self.fields_extracted > 0:
            field_completeness = min(self.fields_extracted / (expected_fields * self.records_extracted), 1.0)
            score = (extraction_rate * 0.7) + (field_completeness * 0.3)
        else:
            score = extraction_rate
            
        return round(score, 3)
    
    def get_job_summary(self) -> Dict[str, Any]:
        """Get job summary."""
        return {
            "id": str(self.id),
            "name": self.name,
            "template_name": self.template_name,
            "status": self.status.value,
            "priority": self.priority.value,
            "progress_percentage": self.get_progress_percentage(),
            "success_rate": self.get_success_rate(),
            "pages_processed": self.pages_processed,
            "pages_successful": self.pages_successful,
            "pages_failed": self.pages_failed,
            "records_extracted": self.records_extracted,
            "data_quality_score": self.data_quality_score,
            "processing_time_seconds": self.processing_time_seconds,
            "bandwidth_used_mb": self.bandwidth_used_mb,
            "created_at": self.created_at.isoformat(),
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None
        }
