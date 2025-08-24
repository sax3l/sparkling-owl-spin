"""
ECaDP Database Models

Complete data model according to Backend specification with MySQL/PostgreSQL compatibility.
Includes all core tables for projects, jobs, crawling, scraping, exports, privacy, and audit.
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey, JSON, Index, Float, Enum as SQLEnum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.sql import func
from datetime import datetime
from typing import Optional, Dict, Any, List
from enum import Enum
import uuid


Base = declarative_base()


class JobStatus(str, Enum):
    """Job status enumeration."""
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    PAUSED = "PAUSED"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    TERMINATED = "TERMINATED"


class JobType(str, Enum):
    """Job type enumeration."""
    CRAWL = "CRAWL"
    SCRAPE = "SCRAPE"
    EXPORT = "EXPORT"
    DQ = "DQ"
    RETENTION = "RETENTION"
    ERASURE = "ERASURE"
    PROXY_VALIDATE = "PROXY_VALIDATE"


class URLStatus(str, Enum):
    """URL processing status."""
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    SKIPPED = "SKIPPED"


class ExportStatus(str, Enum):
    """Export status enumeration."""
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class PrivacyRequestType(str, Enum):
    """Privacy request types."""
    ACCESS = "ACCESS"
    RECTIFICATION = "RECTIFICATION"
    ERASURE = "ERASURE"
    PORTABILITY = "PORTABILITY"
    OBJECTION = "OBJECTION"


class PrivacyRequestStatus(str, Enum):
    """Privacy request status."""
    PENDING = "PENDING"
    PROCESSING = "PROCESSING" 
    COMPLETED = "COMPLETED"
    REJECTED = "REJECTED"


class DQStatus(str, Enum):
    """Data quality status."""
    VALID = "VALID"
    INVALID = "INVALID"
    QUARANTINE = "QUARANTINE"
    REVIEW = "REVIEW"


# Core tables
class Project(Base):
    """Projects table - main container for crawling/scraping configurations."""
    __tablename__ = "projects"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)
    config_json = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    is_active = Column(Boolean, default=True)
    
    # Relationships
    crawl_plans = relationship("CrawlPlan", back_populates="project")
    jobs = relationship("Job", back_populates="project")
    
    __table_args__ = (
        Index('ix_projects_name_active', 'name', 'is_active'),
    )


class CrawlPlan(Base):
    """Crawl plans - rules and configuration for URL discovery."""
    __tablename__ = "crawl_plans"
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    name = Column(String(255), nullable=False)
    rules_json = Column(JSON, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    is_active = Column(Boolean, default=True)
    
    # Relationships
    project = relationship("Project", back_populates="crawl_plans")
    jobs = relationship("Job", back_populates="crawl_plan")


class Template(Base):
    """Templates - extraction rules and data schemas."""
    __tablename__ = "templates"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    version = Column(String(50), nullable=False)
    spec_yaml = Column(Text, nullable=False)
    status = Column(String(50), default="DRAFT")
    published_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    jobs = relationship("Job", back_populates="template")
    extracted_items = relationship("ExtractedItem", back_populates="template")
    
    __table_args__ = (
        Index('ix_templates_name_version', 'name', 'version', unique=True),
        Index('ix_templates_status_published', 'status', 'published_at'),
    )


class Job(Base):
    """Jobs - execution units for crawl, scrape, export operations."""
    __tablename__ = "jobs"
    
    id = Column(Integer, primary_key=True, index=True)
    type = Column(String(50), nullable=False)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    template_id = Column(Integer, ForeignKey("templates.id"), nullable=True)
    plan_id = Column(Integer, ForeignKey("crawl_plans.id"), nullable=True)
    status = Column(String(50), default="PENDING")
    config_json = Column(JSON, nullable=True)
    priority = Column(Integer, default=5)
    started_at = Column(DateTime(timezone=True), nullable=True)
    finished_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    proxy_profile = Column(String(255), nullable=True)
    render_profile = Column(String(255), nullable=True)
    
    # Relationships
    project = relationship("Project", back_populates="jobs")
    template = relationship("Template", back_populates="jobs")
    crawl_plan = relationship("CrawlPlan", back_populates="jobs")
    job_logs = relationship("JobLog", back_populates="job")
    queue_urls = relationship("QueueUrl", back_populates="job")
    extracted_items = relationship("ExtractedItem", back_populates="job")
    
    __table_args__ = (
        Index('ix_jobs_status_priority', 'status', 'priority'),
        Index('ix_jobs_type_status', 'type', 'status'),
        Index('ix_jobs_created_status', 'created_at', 'status'),
    )


class JobLog(Base):
    """Job logs - execution logs and events for jobs."""
    __tablename__ = "job_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(Integer, ForeignKey("jobs.id"), nullable=False)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    level = Column(String(50), nullable=False)
    code = Column(String(100), nullable=True)
    message = Column(Text, nullable=False)
    meta_json = Column(JSON, nullable=True)
    
    # Relationships
    job = relationship("Job", back_populates="job_logs")
    
    __table_args__ = (
        Index('ix_job_logs_job_timestamp', 'job_id', 'timestamp'),
        Index('ix_job_logs_level_timestamp', 'level', 'timestamp'),
    )


class QueueUrl(Base):
    """Queue URLs - URLs to be processed by scraping jobs."""
    __tablename__ = "queue_urls"
    
    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(Integer, ForeignKey("jobs.id"), nullable=False)
    url = Column(Text, nullable=False)
    status = Column(String(50), default="PENDING")
    attempts = Column(Integer, default=0)
    last_error = Column(Text, nullable=True)
    fingerprint_hash = Column(String(64), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    processed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    job = relationship("Job", back_populates="queue_urls")
    
    __table_args__ = (
        Index('ix_queue_urls_fingerprint', 'fingerprint_hash', unique=True),
        Index('ix_queue_urls_status_created', 'status', 'created_at'),
        Index('ix_queue_urls_job_status', 'job_id', 'status'),
    )


class ExtractedItem(Base):
    """Extracted items - data extracted from scraped pages."""
    __tablename__ = "extracted_items"
    
    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(Integer, ForeignKey("jobs.id"), nullable=False)
    template_id = Column(Integer, ForeignKey("templates.id"), nullable=False)
    item_key = Column(String(255), nullable=False)  # Hash of key fields
    payload_json = Column(JSON, nullable=False)
    dq_status = Column(String(50), default="VALID")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    lineage_json = Column(JSON, nullable=True)
    
    # Relationships
    job = relationship("Job", back_populates="extracted_items")
    template = relationship("Template", back_populates="extracted_items")
    dq_violations = relationship("DQViolation", back_populates="item")
    pii_scan_results = relationship("PIIScanResult", back_populates="item")
    
    __table_args__ = (
        Index('ix_extracted_items_item_template', 'item_key', 'template_id', unique=True),
        Index('ix_extracted_items_dq_status', 'dq_status'),
        Index('ix_extracted_items_created', 'created_at'),
    )


class DQViolation(Base):
    """Data Quality violations - validation rule failures."""
    __tablename__ = "dq_violations"
    
    id = Column(Integer, primary_key=True, index=True)
    item_id = Column(Integer, ForeignKey("extracted_items.id"), nullable=False)
    rule = Column(String(255), nullable=False)
    details_json = Column(JSON, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    item = relationship("ExtractedItem", back_populates="dq_violations")
    
    __table_args__ = (
        Index('ix_dq_violations_rule_created', 'rule', 'created_at'),
    )


class Export(Base):
    """Exports - data export operations and results."""
    __tablename__ = "exports"
    
    id = Column(Integer, primary_key=True, index=True)
    query_json = Column(JSON, nullable=False)
    target = Column(String(255), nullable=False)
    status = Column(String(50), default="PENDING")
    file_path = Column(String(1000), nullable=True)
    checksum = Column(String(64), nullable=True)
    row_count = Column(Integer, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    finished_at = Column(DateTime(timezone=True), nullable=True)
    
    __table_args__ = (
        Index('ix_exports_status_created', 'status', 'created_at'),
        Index('ix_exports_target_status', 'target', 'status'),
    )


class Proxy(Base):
    """Proxies - proxy pool management."""
    __tablename__ = "proxies"
    
    id = Column(Integer, primary_key=True, index=True)
    pool = Column(String(255), nullable=False)
    endpoint = Column(String(500), nullable=False)
    geo = Column(String(10), nullable=True)
    health_state = Column(String(50), default="UNKNOWN")
    last_checked = Column(DateTime(timezone=True), nullable=True)
    stats_json = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    health_checks = relationship("ProxyHealth", back_populates="proxy")
    
    __table_args__ = (
        Index('ix_proxies_pool_health', 'pool', 'health_state'),
        Index('ix_proxies_geo_health', 'geo', 'health_state'),
    )


class AuditEvent(Base):
    """Audit events - system activity tracking."""
    __tablename__ = "audit_events"
    
    id = Column(Integer, primary_key=True, index=True)
    who = Column(String(255), nullable=False)  # User ID or system
    what = Column(String(255), nullable=False)  # Action
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    before_json = Column(JSON, nullable=True)
    after_json = Column(JSON, nullable=True)
    scope = Column(String(255), nullable=False)  # Object type/ID
    correlation_id = Column(String(100), nullable=True)
    
    __table_args__ = (
        Index('ix_audit_events_who_timestamp', 'who', 'timestamp'),
        Index('ix_audit_events_what_timestamp', 'what', 'timestamp'),
        Index('ix_audit_events_scope', 'scope'),
        Index('ix_audit_events_correlation', 'correlation_id'),
    )


class User(Base):
    """Users - system user accounts."""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    name = Column(String(255), nullable=False)
    role = Column(String(100), nullable=False, default="Reader")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    last_login = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    api_keys = relationship("APIKey", back_populates="user")
    audit_logs = relationship("AuditLog", back_populates="user")
    
    __table_args__ = (
        Index('ix_users_role_active', 'role', 'is_active'),
    )


class APIKey(Base):
    """API Keys - programmatic access tokens."""
    __tablename__ = "api_keys"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    key_hash = Column(String(255), nullable=False, index=True)
    scope = Column(String(500), nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    last_used = Column(DateTime(timezone=True), nullable=True)
    is_active = Column(Boolean, default=True)
    
    # Relationships
    user = relationship("User", back_populates="api_keys")
    
    __table_args__ = (
        Index('ix_api_keys_hash_active', 'key_hash', 'is_active'),
        Index('ix_api_keys_expires', 'expires_at'),
    )


class Policy(Base):
    """Policies - domain-specific crawling/scraping policies."""
    __tablename__ = "policies"
    
    id = Column(Integer, primary_key=True, index=True)
    domain = Column(String(255), nullable=False, index=True)
    config_json = Column(JSON, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    is_active = Column(Boolean, default=True)
    
    __table_args__ = (
        Index('ix_policies_domain_active', 'domain', 'is_active', unique=True),
    )


class Notification(Base):
    """Notifications - system notifications and alerts."""
    __tablename__ = "notifications"
    
    id = Column(Integer, primary_key=True, index=True)
    channel = Column(String(100), nullable=False)  # email, slack, webhook
    payload_json = Column(JSON, nullable=False)
    status = Column(String(50), default="PENDING")
    attempts = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    sent_at = Column(DateTime(timezone=True), nullable=True)
    
    __table_args__ = (
        Index('ix_notifications_status_created', 'status', 'created_at'),
        Index('ix_notifications_channel_status', 'channel', 'status'),
    )


class PrivacyRequest(Base):
    """Privacy requests - GDPR/privacy compliance requests."""
    __tablename__ = "privacy_requests"
    
    id = Column(Integer, primary_key=True, index=True)
    type = Column(String(50), nullable=False)
    subject_reference = Column(String(255), nullable=False)  # Email, ID, etc.
    status = Column(String(50), default="PENDING")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    finished_at = Column(DateTime(timezone=True), nullable=True)
    meta_json = Column(JSON, nullable=True)
    
    __table_args__ = (
        Index('ix_privacy_requests_subject', 'subject_reference'),
        Index('ix_privacy_requests_type_status', 'type', 'status'),
    )


class PIIScanResult(Base):
    """PII Scan Results - personally identifiable information detection results."""
    __tablename__ = "pii_scan_results"
    
    id = Column(Integer, primary_key=True, index=True)
    item_id = Column(Integer, ForeignKey("extracted_items.id"), nullable=False)
    pii_type = Column(String(100), nullable=False)  # email, ssn, phone, etc.
    snippet = Column(String(500), nullable=False)  # Truncated/masked snippet
    field_path = Column(String(255), nullable=False)  # JSON path to field
    confidence = Column(Float, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    item = relationship("ExtractedItem", back_populates="pii_scan_results")
    
    __table_args__ = (
        Index('ix_pii_scan_results_type', 'pii_type'),
        Index('ix_pii_scan_results_confidence', 'confidence'),
    )


class RetentionPolicy(Base):
    """Retention policies - data lifecycle management."""
    __tablename__ = "retention_policies"
    
    id = Column(Integer, primary_key=True, index=True)
    target = Column(String(255), nullable=False)  # table, file type, etc.
    ttl_days = Column(Integer, nullable=False)
    config_json = Column(JSON, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    is_active = Column(Boolean, default=True)
    
    __table_args__ = (
        Index('ix_retention_policies_target', 'target'),
        Index('ix_retention_policies_active', 'is_active'),
    )


# Helper functions
def generate_item_key(template_id: int, key_fields: Dict[str, Any]) -> str:
    """Generate a unique item key based on template ID and key fields."""
    import hashlib
    import json
    
    # Sort keys for consistent hashing
    sorted_fields = json.dumps(key_fields, sort_keys=True)
    content = f"{template_id}:{sorted_fields}"
    return hashlib.sha256(content.encode()).hexdigest()[:32]


class UserQuota(Base):
    """User quota and usage tracking."""
    __tablename__ = 'user_quotas'
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    quota_type: Mapped[str] = mapped_column(String(50), nullable=False)  # pages, requests, data_gb, etc.
    quota_limit: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    quota_used: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    reset_period: Mapped[str] = mapped_column(String(20), nullable=False, default='monthly')  # daily, weekly, monthly
    reset_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=func.now())
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=func.now(), onupdate=func.now())
    
    # Indexes for performance
    __table_args__ = (
        Index('ix_user_quotas_user_type', 'user_id', 'quota_type'),
        Index('ix_user_quotas_reset', 'reset_at'),
    )
    
    @property
    def quota_remaining(self) -> int:
        """Get remaining quota."""
        return max(0, self.quota_limit - self.quota_used)
    
    @property
    def usage_percentage(self) -> float:
        """Get usage as percentage."""
        if self.quota_limit == 0:
            return 0.0
        return min(100.0, (self.quota_used / self.quota_limit) * 100.0)
    
    def is_quota_exceeded(self) -> bool:
        """Check if quota is exceeded."""
        return self.quota_used >= self.quota_limit


class IdempotencyKey(Base):
    """Idempotency key model for preventing duplicate operations."""
    
    __tablename__ = "idempotency_keys"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    key: Mapped[str] = mapped_column(String(255), nullable=False)
    tenant_id: Mapped[str] = mapped_column(String(255), nullable=False)  
    path: Mapped[str] = mapped_column(String(500), nullable=False)
    method: Mapped[str] = mapped_column(String(10), nullable=False)
    response_code: Mapped[Optional[int]] = mapped_column(Integer)
    response_body: Mapped[Optional[str]] = mapped_column(Text)
    response_headers: Mapped[Optional[str]] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now(), nullable=False)
    expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    
    # Composite index for efficient lookups
    __table_args__ = (
        Index('idx_idempotency_lookup', 'key', 'tenant_id', 'path', 'method'),
        Index('idx_idempotency_expires', 'expires_at'),
    )
    
    def is_expired(self) -> bool:
        """Check if the idempotency key has expired."""
        if not self.expires_at:
            return False
        return datetime.utcnow() > self.expires_at


def generate_url_fingerprint(url: str) -> str:
    """Generate URL fingerprint for deduplication."""
    import hashlib
    from urllib.parse import urlparse, parse_qs
    
    # Parse and normalize URL
    parsed = urlparse(url.lower().strip())
    
    # Create normalized version
    normalized = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
    
    # Add sorted query parameters
    if parsed.query:
        sorted_params = sorted(parse_qs(parsed.query).items())
        normalized += "?" + "&".join(f"{k}={v[0] if v else ''}" for k, v in sorted_params)
    
    return hashlib.sha256(normalized.encode()).hexdigest()


class AuditLog(Base):
    """Audit logs - comprehensive system audit trail."""
    __tablename__ = "audit_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    action = Column(String(100), nullable=False)
    resource_type = Column(String(100), nullable=False)
    resource_id = Column(String(255), nullable=True)
    details = Column(JSON, nullable=True)
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(String(500), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User", back_populates="audit_logs")
    
    __table_args__ = (
        Index('ix_audit_logs_user_action', 'user_id', 'action'),
        Index('ix_audit_logs_resource', 'resource_type', 'resource_id'),
        Index('ix_audit_logs_created_at', 'created_at'),
    )


class ProxyHealth(Base):
    """Proxy health monitoring - tracks proxy performance and availability."""
    __tablename__ = "proxy_health"
    
    id = Column(Integer, primary_key=True, index=True)
    proxy_id = Column(Integer, ForeignKey("proxies.id"), nullable=False)
    response_time_ms = Column(Float, nullable=False)
    success_rate = Column(Float, nullable=False)
    last_check = Column(DateTime(timezone=True), server_default=func.now())
    is_healthy = Column(Boolean, default=True)
    error_count = Column(Integer, default=0)
    consecutive_failures = Column(Integer, default=0)
    
    # Relationships
    proxy = relationship("Proxy", back_populates="health_checks")
    
    __table_args__ = (
        Index('ix_proxy_health_proxy_id', 'proxy_id'),
        Index('ix_proxy_health_last_check', 'last_check'),
        Index('ix_proxy_health_healthy', 'is_healthy'),
    )


class ScrapedData(Base):
    """
    Scraped data model - placeholder for data quality jobs.
    Contains scraped content and metadata.
    """
    __tablename__ = 'scraped_data'
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    url = Column(String, nullable=False)
    data = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Data quality metadata
    quality_score = Column(Float, nullable=True)
    completeness_score = Column(Float, nullable=True)
    freshness_score = Column(Float, nullable=True)


# Pydantic schemas for API validation
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class ExportCreate(BaseModel):
    """Schema for creating exports"""
    target: str
    format: str
    filters: Optional[dict] = None
    fields: Optional[list] = None
    
class ExportRead(BaseModel):
    """Schema for reading exports"""
    id: str
    target: str
    format: str
    status: str
    created_at: datetime
    
    class Config:
        from_attributes = True
