import datetime
import enum
import uuid
from typing import Optional, List, Dict, Any, Literal

from pydantic import BaseModel, Field, model_validator
from sqlalchemy import (BigInteger, Boolean, Column, Date, DateTime, Enum as SAEnum,
                        ForeignKey, Integer, LargeBinary, Numeric, String, Text, func)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

# Enum Types
class GenderEnum(enum.Enum):
    unknown = 'unknown'
    female = 'female'
    male = 'male'
    other = 'other'

class OwnerKindEnum(enum.Enum):
    person = 'person'
    company = 'company'

class JobType(str, enum.Enum):
    CRAWL = "crawl"
    SCRAPE = "scrape"

class JobStatus(str, enum.Enum):
    PENDING = "pending"
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

# --- Core Schema Models ---
# ... (existing models remain unchanged)
class Person(Base):
    __tablename__ = "persons"
    person_id = Column(BigInteger, primary_key=True)
    # ... columns
    
class PersonAddress(Base):
    __tablename__ = "person_addresses"
    address_id = Column(BigInteger, primary_key=True)
    # ... columns

class PersonContact(Base):
    __tablename__ = "person_contacts"
    contact_id = Column(BigInteger, primary_key=True)
    # ... columns

class Company(Base):
    __tablename__ = "companies"
    company_id = Column(BigInteger, primary_key=True)
    # ... columns

class CompanyRole(Base):
    __tablename__ = "company_roles"
    role_id = Column(BigInteger, primary_key=True)
    # ... columns

class CompanyFinancials(Base):
    __tablename__ = "company_financials"
    finance_id = Column(BigInteger, primary_key=True)
    # ... columns

class Vehicle(Base):
    __tablename__ = "vehicles"
    vehicle_id = Column(BigInteger, primary_key=True)
    # ... columns

class VehicleTechnicalSpecs(Base):
    __tablename__ = "vehicle_technical_specs"
    spec_id = Column(BigInteger, primary_key=True)
    # ... columns

class VehicleOwnership(Base):
    __tablename__ = "vehicle_ownership"
    vehicle_owner_id = Column(BigInteger, primary_key=True)
    # ... columns

class VehicleHistory(Base):
    __tablename__ = "vehicle_history"
    history_id = Column(BigInteger, primary_key=True)
    # ... columns

# --- Operational Models ---

class Job(Base):
    __tablename__ = "scraping_jobs"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    job_type = Column(String, nullable=False)
    start_url = Column(String, nullable=False)
    status = Column(String, default=JobStatus.PENDING.value, nullable=False)
    params = Column(JSONB)
    result = Column(JSONB)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    started_at = Column(DateTime(timezone=True))
    finished_at = Column(DateTime(timezone=True))

class Template(Base):
    __tablename__ = "templates"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False, unique=True)
    dsl = Column(JSONB, nullable=False)
    version = Column(Integer, nullable=False, default=1)
    created_by = Column(UUID(as_uuid=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

# ... other operational models

# --- Pydantic Models for API ---

# Crawl Job Models
class FeatureFlags(BaseModel):
    detect_templates: bool = True
    paginate_auto: bool = True
    infinite_scroll: bool = False

class CrawlPolicy(BaseModel):
    respect_robots: bool = True
    crawl_delay_ms: int = 1000
    parallelism: int = 8
    transport: str = "http"
    user_agent_profile: str = "chrome-stable"
    feature_flags: FeatureFlags = Field(default_factory=FeatureFlags)

class CrawlCaps(BaseModel):
    rps_per_domain: float = 1.5
    max_concurrent_per_domain: int = 4

class CrawlJobCreate(BaseModel):
    seeds: List[str]
    max_depth: int = 3
    max_urls: int = 20000
    allow_domains: List[str]
    disallow_patterns: List[str] = Field(default_factory=list)
    policy: CrawlPolicy = Field(default_factory=CrawlPolicy)
    caps: CrawlCaps = Field(default_factory=CrawlCaps)
    tags: List[str] = Field(default_factory=list)

# Scrape Job Models
class SitemapQuery(BaseModel):
    domain: str
    pattern: str
    limit: int = 5000

class ScrapeSource(BaseModel):
    sitemap_query: Optional[SitemapQuery] = None
    urls: Optional[List[str]] = None

    @model_validator(mode='after')
    def check_exactly_one_source(self) -> 'ScrapeSource':
        if self.sitemap_query is not None and self.urls is not None:
            raise ValueError('Either sitemap_query or urls must be provided, not both.')
        if self.sitemap_query is None and self.urls is None:
            raise ValueError('Either sitemap_query or urls must be provided.')
        return self

class ScrapePolicy(BaseModel):
    transport: Literal["http", "browser", "auto"] = "auto"
    max_retries: int = 2
    delay_profile: str = "default"

class ScrapeCaps(BaseModel):
    max_concurrent: int = 16
    browser_pool_size: int = 4

class ExportDestination(BaseModel):
    type: Literal["internal_staging", "s3_presigned", "gcs_signed"] = "internal_staging"
    retention_hours: int = 72

class ExportConfig(BaseModel):
    format: Literal["json", "csv", "ndjson"] = "ndjson"
    compress: Literal["none", "gzip"] = "gzip"
    destination: ExportDestination = Field(default_factory=ExportDestination)

class ScrapeJobCreate(BaseModel):
    template_id: str
    template_version: Optional[str] = None
    source: ScrapeSource
    policy: ScrapePolicy = Field(default_factory=ScrapePolicy)
    caps: ScrapeCaps = Field(default_factory=ScrapeCaps)
    export: ExportConfig = Field(default_factory=ExportConfig)
    tags: List[str] = Field(default_factory=list)

# General Job Models
class JobRead(BaseModel):
    id: uuid.UUID
    job_type: JobType
    start_url: str
    status: JobStatus
    params: Optional[Dict[str, Any]] = None
    result: Optional[Dict[str, Any]] = None
    created_at: datetime.datetime
    started_at: Optional[datetime.datetime] = None
    finished_at: Optional[datetime.datetime] = None
    links: Dict[str, str]

    class Config:
        orm_mode = True

# Template Models
class TemplateBase(BaseModel):
    name: str = Field(..., pattern=r"^[a-zA-Z0-9_.-]+$")
    dsl: Dict[str, Any]

class TemplateCreate(TemplateBase):
    pass

class TemplateUpdate(TemplateBase):
    pass

class TemplateRead(TemplateBase):
    id: uuid.UUID
    version: int
    created_at: datetime.datetime
    updated_at: Optional[datetime.datetime] = None

    class Config:
        orm_mode = True