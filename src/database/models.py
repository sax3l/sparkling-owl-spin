import datetime
import enum
import uuid
from typing import Optional, List, Dict, Any

from pydantic import BaseModel, Field
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

# --- Core Schema Models ---
# ... (existing models remain unchanged)
class Person(Base):
    __tablename__ = "persons"
    person_id = Column(BigInteger, primary_key=True)
    personal_number_enc = Column(LargeBinary)
    personal_number_hash = Column(Text, unique=True)
    first_name = Column(Text)
    middle_name = Column(Text)
    last_name = Column(Text)
    birth_date = Column(Date)
    gender = Column(SAEnum(GenderEnum), default=GenderEnum.unknown)
    civil_status = Column(Text)
    economy_summary = Column(Text)
    salary_decimal = Column(Numeric(14, 2))
    has_remarks = Column(Boolean)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())
    
    addresses = relationship("PersonAddress", back_populates="person", cascade="all, delete-orphan")
    contacts = relationship("PersonContact", back_populates="person", cascade="all, delete-orphan")
    company_roles = relationship("CompanyRole", back_populates="person")
    vehicle_ownerships = relationship("VehicleOwnership", back_populates="person")

class PersonAddress(Base):
    __tablename__ = "person_addresses"
    address_id = Column(BigInteger, primary_key=True)
    person_id = Column(BigInteger, ForeignKey('persons.person_id', ondelete='CASCADE'), nullable=False)
    street = Column(Text)
    postal_code = Column(Text)
    city = Column(Text)
    municipality = Column(Text)
    county = Column(Text)
    special_address = Column(Text)
    start_date = Column(Date)
    end_date = Column(Date)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    person = relationship("Person", back_populates="addresses")

class PersonContact(Base):
    __tablename__ = "person_contacts"
    contact_id = Column(BigInteger, primary_key=True)
    person_id = Column(BigInteger, ForeignKey('persons.person_id', ondelete='CASCADE'), nullable=False)
    phone_number_enc = Column(LargeBinary)
    phone_number_hash = Column(Text, index=True)
    operator = Column(Text)
    user_type = Column(Text)
    last_porting_date = Column(Date)
    previous_operator = Column(Text)
    kind = Column(Text)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    person = relationship("Person", back_populates="contacts")

class Company(Base):
    __tablename__ = "companies"
    company_id = Column(BigInteger, primary_key=True)
    org_number = Column(Text, unique=True)
    name = Column(Text, index=True)
    email = Column(Text)
    website = Column(Text)
    registration_date = Column(Date)
    status = Column(Text)
    company_form = Column(Text)
    county_seat = Column(Text)
    municipal_seat = Column(Text)
    sni_code = Column(Text, index=True)
    industry = Column(Text)
    remark_control = Column(Text)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())
    
    roles = relationship("CompanyRole", back_populates="company")
    financials = relationship("CompanyFinancials", back_populates="company", cascade="all, delete-orphan")
    vehicle_ownerships = relationship("VehicleOwnership", back_populates="company")

class CompanyRole(Base):
    __tablename__ = "company_roles"
    role_id = Column(BigInteger, primary_key=True)
    person_id = Column(BigInteger, ForeignKey('persons.person_id', ondelete='CASCADE'), nullable=False)
    company_id = Column(BigInteger, ForeignKey('companies.company_id', ondelete='CASCADE'), nullable=False)
    role_name = Column(Text)
    is_beneficial_owner = Column(Boolean, default=False)
    start_date = Column(Date)
    end_date = Column(Date)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    
    person = relationship("Person", back_populates="company_roles")
    company = relationship("Company", back_populates="roles")

class CompanyFinancials(Base):
    __tablename__ = "company_financials"
    finance_id = Column(BigInteger, primary_key=True)
    company_id = Column(BigInteger, ForeignKey('companies.company_id', ondelete='CASCADE'), nullable=False)
    fiscal_year = Column(Date, nullable=False)
    turnover = Column(Numeric(16, 2))
    result_after_financial_items = Column(Numeric(16, 2))
    annual_result = Column(Numeric(16, 2))
    total_assets = Column(Numeric(16, 2))
    profit_margin = Column(Numeric(8, 3))
    cash_liquidity = Column(Numeric(8, 3))
    solidity = Column(Numeric(8, 3))
    employee_count = Column(Integer)
    share_capital = Column(Numeric(16, 2))
    risk_buffer = Column(Numeric(16, 2))
    report_url = Column(Text)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    
    company = relationship("Company", back_populates="financials")

class Vehicle(Base):
    __tablename__ = "vehicles"
    vehicle_id = Column(BigInteger, primary_key=True)
    registration_number = Column(Text, unique=True)
    vin = Column(Text, index=True)
    make = Column(Text)
    model = Column(Text)
    model_year = Column(Integer)
    import_status = Column(Text)
    stolen_status = Column(Text)
    traffic_status = Column(Text)
    owner_count = Column(Integer)
    first_registration_date = Column(Date)
    traffic_in_sweden_since = Column(Date)
    next_inspection = Column(Date)
    emission_class = Column(Text)
    tax_year1_3 = Column(Numeric(12, 2))
    tax_year4 = Column(Numeric(12, 2))
    tax_month = Column(Integer)
    is_financed = Column(Boolean)
    is_leased = Column(Boolean)
    eu_category = Column(Text)
    type_approval_number = Column(Text)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())
    
    tech_specs = relationship("VehicleTechnicalSpecs", back_populates="vehicle", uselist=False, cascade="all, delete-orphan")
    ownerships = relationship("VehicleOwnership", back_populates="vehicle", cascade="all, delete-orphan")
    history = relationship("VehicleHistory", back_populates="vehicle", cascade="all, delete-orphan")

class VehicleTechnicalSpecs(Base):
    __tablename__ = "vehicle_technical_specs"
    spec_id = Column(BigInteger, primary_key=True)
    vehicle_id = Column(BigInteger, ForeignKey('vehicles.vehicle_id', ondelete='CASCADE'), nullable=False, unique=True)
    engine_power_kw = Column(Numeric(8, 2))
    engine_volume_cc = Column(Integer)
    top_speed_kmh = Column(Integer)
    fuel_type = Column(Text)
    gearbox = Column(Text)
    drive_type = Column(Text)
    wltp_consumption_l_100km = Column(Numeric(6, 3))
    wltp_co2_g_km = Column(Numeric(6, 1))
    noise_drive_db = Column(Integer)
    passenger_count = Column(Integer)
    airbag_info = Column(Text)
    length_mm = Column(Integer)
    width_mm = Column(Integer)
    height_mm = Column(Integer)
    curb_weight_kg = Column(Integer)
    total_weight_kg = Column(Integer)
    payload_kg = Column(Integer)
    trailer_braked_kg = Column(Integer)
    trailer_unbraked_kg = Column(Integer)
    trailer_total_b_kg = Column(Integer)
    trailer_total_b_plus_kg = Column(Integer)
    wheelbase_mm = Column(Integer)
    tire_front = Column(Text)
    tire_rear = Column(Text)
    rim_front = Column(Text)
    rim_rear = Column(Text)
    body_type = Column(Text)
    color = Column(Text)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    
    vehicle = relationship("Vehicle", back_populates="tech_specs")

class VehicleOwnership(Base):
    __tablename__ = "vehicle_ownership"
    vehicle_owner_id = Column(BigInteger, primary_key=True)
    vehicle_id = Column(BigInteger, ForeignKey('vehicles.vehicle_id', ondelete='CASCADE'), nullable=False)
    owner_kind = Column(SAEnum(OwnerKindEnum), nullable=False)
    person_id = Column(BigInteger, ForeignKey('persons.person_id', ondelete='CASCADE'))
    company_id = Column(BigInteger, ForeignKey('companies.company_id', ondelete='CASCADE'))
    role = Column(Text)
    start_date = Column(Date)
    end_date = Column(Date)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    
    vehicle = relationship("Vehicle", back_populates="ownerships")
    person = relationship("Person", back_populates="vehicle_ownerships")
    company = relationship("Company", back_populates="vehicle_ownerships")

class VehicleHistory(Base):
    __tablename__ = "vehicle_history"
    history_id = Column(BigInteger, primary_key=True)
    vehicle_id = Column(BigInteger, ForeignKey('vehicles.vehicle_id', ondelete='CASCADE'), nullable=False)
    event_date = Column(Date)
    event_kind = Column(Text)
    event_desc = Column(Text)
    event_link = Column(Text)
    raw_json = Column(JSONB)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    
    vehicle = relationship("Vehicle", back_populates="history")

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

class DataQualityMetrics(Base):
    __tablename__ = "data_quality_metrics"
    metric_id = Column(BigInteger, primary_key=True)
    entity_type = Column(Text)
    entity_id = Column(BigInteger)
    field_name = Column(Text)
    completeness = Column(Numeric(5, 2))
    validity = Column(Numeric(5, 2))
    consistency = Column(Numeric(5, 2))
    measured_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())

class StagingExtract(Base):
    __tablename__ = "staging_extracts"
    staging_id = Column(BigInteger, primary_key=True)
    job_id = Column(BigInteger, ForeignKey('scraping_jobs.job_id', ondelete='SET NULL'))
    domain = Column(Text, nullable=False)
    url = Column(Text, nullable=False)
    template_key = Column(Text, index=True)
    fetched_at = Column(DateTime(timezone=True), nullable=False)
    status = Column(Text)
    payload_json = Column(JSONB)
    issues_json = Column(JSONB)
    snapshot_ref = Column(Text)
    fingerprint = Column(Text)

# --- Pydantic Models for API ---

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