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
    EXPORT = "export" # Added EXPORT job type
    DIAGNOSTIC = "diagnostic" # Added DIAGNOSTIC job type

class JobStatus(str, enum.Enum):
    PENDING = "pending"
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

# --- Core Schema Models ---
class Person(Base):
    __tablename__ = "persons"
    person_id = Column(BigInteger, primary_key=True)
    personal_number_enc = Column(LargeBinary)
    personal_number_hash = Column(Text)
    first_name = Column(Text)
    middle_name = Column(Text)
    last_name = Column(Text)
    birth_date = Column(Date)
    gender = Column(SAEnum(GenderEnum, name='gender_enum'), default=GenderEnum.unknown)
    civil_status = Column(Text)
    economy_summary = Column(Text)
    salary_decimal = Column(Numeric)
    has_remarks = Column(Boolean)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    source_job_id = Column(UUID(as_uuid=True), ForeignKey('scraping_jobs.id')) # New field

class PersonAddress(Base):
    __tablename__ = "person_addresses"
    address_id = Column(BigInteger, primary_key=True)
    person_id = Column(BigInteger, ForeignKey('persons.person_id'), nullable=False)
    street = Column(Text)
    postal_code = Column(Text)
    city = Column(Text)
    municipality = Column(Text)
    county = Column(Text)
    special_address = Column(Text)
    start_date = Column(Date)
    end_date = Column(Date)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class PersonContact(Base):
    __tablename__ = "person_contacts"
    contact_id = Column(BigInteger, primary_key=True)
    person_id = Column(BigInteger, ForeignKey('persons.person_id'), nullable=False)
    phone_number_enc = Column(LargeBinary)
    phone_number_hash = Column(Text)
    operator = Column(Text)
    user_type = Column(Text)
    last_porting_date = Column(Date)
    previous_operator = Column(Text)
    kind = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Company(Base):
    __tablename__ = "companies"
    company_id = Column(BigInteger, primary_key=True)
    org_number = Column(Text, unique=True)
    name = Column(Text)
    email = Column(Text)
    website = Column(Text)
    registration_date = Column(Date)
    status = Column(Text)
    company_form = Column(Text)
    county_seat = Column(Text)
    municipal_seat = Column(Text)
    sni_code = Column(Text)
    industry = Column(Text)
    remark_control = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    source_job_id = Column(UUID(as_uuid=True), ForeignKey('scraping_jobs.id')) # New field

class CompanyRole(Base):
    __tablename__ = "company_roles"
    role_id = Column(BigInteger, primary_key=True)
    person_id = Column(BigInteger, ForeignKey('persons.person_id'), nullable=False)
    company_id = Column(BigInteger, ForeignKey('companies.company_id'), nullable=False)
    role_name = Column(Text)
    is_beneficial_owner = Column(Boolean, default=False)
    start_date = Column(Date)
    end_date = Column(Date)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class CompanyFinancials(Base):
    __tablename__ = "company_financials"
    finance_id = Column(BigInteger, primary_key=True)
    company_id = Column(BigInteger, ForeignKey('companies.company_id'), nullable=False)
    fiscal_year = Column(Date, nullable=False)
    turnover = Column(Numeric)
    result_after_financial_items = Column(Numeric)
    annual_result = Column(Numeric)
    total_assets = Column(Numeric)
    profit_margin = Column(Numeric)
    cash_liquidity = Column(Numeric)
    solidity = Column(Numeric)
    employee_count = Column(Integer)
    share_capital = Column(Numeric)
    risk_buffer = Column(Numeric)
    report_url = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Vehicle(Base):
    __tablename__ = "vehicles"
    vehicle_id = Column(BigInteger, primary_key=True)
    registration_number = Column(Text, unique=True)
    vin = Column(Text, unique=True)
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
    tax_year1_3 = Column(Numeric)
    tax_year4 = Column(Numeric)
    tax_month = Column(Integer)
    is_financed = Column(Boolean)
    is_leased = Column(Boolean)
    eu_category = Column(Text)
    type_approval_number = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    source_job_id = Column(UUID(as_uuid=True), ForeignKey('scraping_jobs.id')) # New field

class VehicleTechnicalSpecs(Base):
    __tablename__ = "vehicle_technical_specs"
    spec_id = Column(BigInteger, primary_key=True)
    vehicle_id = Column(BigInteger, ForeignKey('vehicles.vehicle_id'), nullable=False)
    engine_power_kw = Column(Numeric)
    engine_volume_cc = Column(Integer)
    top_speed_kmh = Column(Integer)
    fuel_type = Column(Text)
    gearbox = Column(Text)
    drive_type = Column(Text)
    wltp_consumption_l_100km = Column(Numeric)
    wltp_co2_g_km = Column(Numeric)
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
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class VehicleOwnership(Base):
    __tablename__ = "vehicle_ownership"
    vehicle_owner_id = Column(BigInteger, primary_key=True)
    vehicle_id = Column(BigInteger, ForeignKey('vehicles.vehicle_id'), nullable=False)
    owner_kind = Column(SAEnum(OwnerKindEnum, name='owner_kind_enum'), nullable=False)
    person_id = Column(BigInteger, ForeignKey('persons.person_id'))
    company_id = Column(BigInteger, ForeignKey('companies.company_id'))
    role = Column(Text)
    start_date = Column(Date)
    end_date = Column(Date)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class VehicleHistory(Base):
    __tablename__ = "vehicle_history"
    history_id = Column(BigInteger, primary_key=True)
    vehicle_id = Column(BigInteger, ForeignKey('vehicles.vehicle_id'), nullable=False)
    event_date = Column(Date)
    event_kind = Column(Text)
    event_desc = Column(Text)
    event_link = Column(Text)
    raw_json = Column(JSONB)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class DataQualityMetric(Base):
    __tablename__ = "data_quality_metrics"
    metric_id = Column(BigInteger, primary_key=True)
    entity_type = Column(Text)
    entity_id = Column(BigInteger)
    field_name = Column(Text)
    completeness = Column(Numeric)
    validity = Column(Numeric)
    consistency = Column(Numeric)
    measured_at = Column(DateTime(timezone=True), server_default=func.now())

class GCSFile(Base):
    __tablename__ = "gcs_files"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    bucket_name = Column(Text, nullable=False)
    object_name = Column(Text, nullable=False)
    size = Column(BigInteger)
    content_type = Column(Text)
    md5_hash = Column(Text)
    gcs_updated_at = Column(DateTime(timezone=True))
    metadata = Column(JSONB, nullable=False, default={})
    project_id = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    synced_at = Column(DateTime(timezone=True), server_default=func.now())

class SiteSetting(Base):
    __tablename__ = "site_settings"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    cv_file_url = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

class AboutMe(Base):
    __tablename__ = "about_me"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(Text)
    subtitle = Column(Text)
    intro = Column(Text)
    full_text = Column(Text)
    profile_image_url = Column(Text)
    job_title = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

class Article(Base):
    __tablename__ = "articles"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(Text, nullable=False)
    content = Column(Text)
    published = Column(Boolean, nullable=False, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

class Project(Base):
    __tablename__ = "projects"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(Text, nullable=False)
    description = Column(Text)
    active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

class VehicleRegistry(Base):
    __tablename__ = "vehicle_registry"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    reg_plate = Column(Text)
    brand = Column(Text)
    model = Column(Text)
    year = Column(Integer)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

class PageView(Base):
    __tablename__ = "page_views"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    page_path = Column(Text, nullable=False)
    viewed_at = Column(DateTime(timezone=True), server_default=func.now())

class Profile(Base):
    __tablename__ = "profiles"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('auth.users.id', ondelete='CASCADE'))
    tenant_id = Column(UUID(as_uuid=True), ForeignKey('auth.users.id', ondelete='CASCADE'), nullable=False) # New column
    email = Column(Text, nullable=False)
    full_name = Column(Text)
    company = Column(Text)
    phone = Column(Text)
    avatar_url = Column(Text)
    bio = Column(Text)
    preferences = Column(JSONB, default={})
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

class Subscriber(Base):
    __tablename__ = "subscribers"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('auth.users.id', ondelete='CASCADE'))
    email = Column(Text, nullable=False)
    stripe_customer_id = Column(Text)
    subscribed = Column(Boolean, nullable=False, default=False)
    subscription_tier = Column(Text)
    subscription_end = Column(DateTime(timezone=True))
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class UserAPIKey(Base):
    __tablename__ = "user_api_keys"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('auth.users.id', ondelete='CASCADE'))
    tenant_id = Column(UUID(as_uuid=True), ForeignKey('auth.users.id', ondelete='CASCADE'), nullable=False) # New column
    key_name = Column(Text, nullable=False)
    api_key_hash = Column(Text, nullable=False)
    permissions = Column(JSONB, default=[])
    last_used_at = Column(DateTime(timezone=True))
    expires_at = Column(DateTime(timezone=True))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class UserDataset(Base):
    __tablename__ = "user_datasets"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('auth.users.id', ondelete='CASCADE'))
    name = Column(Text, nullable=False)
    description = Column(Text)
    data_source = Column(Text)
    size_mb = Column(Numeric)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    access_level = Column(Text, default='private')

class UserDashboard(Base):
    __tablename__ = "user_dashboards"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('auth.users.id', ondelete='CASCADE'))
    name = Column(Text, nullable=False)
    description = Column(Text)
    dashboard_config = Column(JSONB)
    is_shared = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

class UserCredit(Base):
    __tablename__ = "user_credits"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('auth.users.id', ondelete='CASCADE'))
    balance = Column(Integer, nullable=False, default=0)
    total_earned = Column(Integer, nullable=False, default=0)
    total_spent = Column(Integer, nullable=False, default=0)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

class CreditTransaction(Base):
    __tablename__ = "credit_transactions"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('auth.users.id', ondelete='CASCADE'))
    amount = Column(Integer, nullable=False)
    transaction_type = Column(Text, nullable=False)
    description = Column(Text)
    reference_id = Column(UUID(as_uuid=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Team(Base):
    __tablename__ = "teams"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(Text, nullable=False)
    description = Column(Text)
    created_by = Column(UUID(as_uuid=True), ForeignKey('auth.users.id', ondelete='SET NULL'))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

class TeamMember(Base):
    __tablename__ = "team_members"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    team_id = Column(UUID(as_uuid=True), ForeignKey('teams.id', ondelete='CASCADE'))
    user_id = Column(UUID(as_uuid=True), ForeignKey('auth.users.id', ondelete='CASCADE'))
    role = Column(Text, nullable=False)
    joined_at = Column(DateTime(timezone=True), server_default=func.now())

class ExportHistory(Base):
    __tablename__ = "export_history"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('auth.users.id', ondelete='CASCADE'))
    export_type = Column(Text, nullable=False) # e.g., 'person', 'company', 'vehicle'
    file_name = Column(Text, nullable=False)
    file_size_mb = Column(Numeric)
    credits_used = Column(Integer, nullable=False, default=0)
    status = Column(Text, nullable=False, default='processing')
    download_url = Column(Text) # Added download_url
    expires_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    filters_json = Column(JSONB) # Added filters_json to store export criteria

class Referral(Base):
    __tablename__ = "referrals"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    referrer_id = Column(UUID(as_uuid=True), ForeignKey('auth.users.id', ondelete='CASCADE'))
    referred_email = Column(Text, nullable=False)
    referred_user_id = Column(UUID(as_uuid=True), ForeignKey('auth.users.id', ondelete='SET NULL'))
    status = Column(Text, nullable=False, default='pending')
    credits_earned = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    activated_at = Column(DateTime(timezone=True))

class Course(Base):
    __tablename__ = "courses"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(Text, nullable=False)
    description = Column(Text)
    content = Column(JSONB)
    difficulty_level = Column(Text, default='beginner')
    estimated_duration = Column(Integer)
    is_published = Column(Boolean, default=False)
    order_index = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

class UserCourseProgress(Base):
    __tablename__ = "user_course_progress"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('auth.users.id', ondelete='CASCADE'), nullable=False)
    course_id = Column(UUID(as_uuid=True), ForeignKey('courses.id', ondelete='CASCADE'), nullable=False)
    progress_percentage = Column(Integer, default=0)
    completed_modules = Column(JSONB, default=[])
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True))
    last_accessed = Column(DateTime(timezone=True), server_default=func.now())

class News(Base):
    __tablename__ = "news"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(Text, nullable=False)
    content = Column(Text)
    excerpt = Column(Text)
    author_id = Column(UUID(as_uuid=True), ForeignKey('auth.users.id', ondelete='SET NULL'))
    featured_image_url = Column(Text)
    is_published = Column(Boolean, default=False)
    published_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

class SubscriptionPlan(Base):
    __tablename__ = "subscription_plans"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(Text, nullable=False)
    description = Column(Text)
    price_monthly = Column(Numeric)
    price_yearly = Column(Numeric)
    features = Column(JSONB, default=[])
    max_team_members = Column(Integer, default=1)
    credits_per_month = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

class UserSetting(Base):
    __tablename__ = "user_settings"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('auth.users.id', ondelete='CASCADE'), nullable=False)
    notification_preferences = Column(JSONB, default={'push': True, 'email': True, 'marketing': False})
    privacy_settings = Column(JSONB, default={'data_sharing': False, 'profile_public': False})
    language_preference = Column(Text, default='sv')
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

class UserDevice(Base):
    __tablename__ = "user_devices"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('auth.users.id', ondelete='CASCADE'), nullable=False)
    device_name = Column(Text, nullable=False)
    device_type = Column(Text, nullable=False)
    browser = Column(Text)
    operating_system = Column(Text)
    last_login = Column(DateTime(timezone=True), server_default=func.now())
    is_current_device = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class BillingInfo(Base):
    __tablename__ = "billing_info"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('auth.users.id', ondelete='CASCADE'), nullable=False)
    company_name = Column(Text)
    org_number = Column(Text)
    billing_address = Column(Text)
    billing_city = Column(Text)
    billing_postal_code = Column(Text)
    billing_country = Column(Text, default='Sweden')
    vat_number = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

class Transaction(Base):
    __tablename__ = "transactions"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('auth.users.id', ondelete='CASCADE'), nullable=False)
    amount = Column(Numeric, nullable=False)
    currency = Column(Text, default='SEK')
    transaction_type = Column(Text, nullable=False)
    status = Column(Text, default='completed')
    description = Column(Text)
    stripe_payment_id = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class UserRole(Base):
    __tablename__ = "user_roles"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('auth.users.id', ondelete='CASCADE'), nullable=False)
    role = Column(Text, nullable=False, default='user')
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

class UserSubscription(Base):
    __tablename__ = "user_subscriptions"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('auth.users.id', ondelete='CASCADE'), nullable=False)
    subscription_tier = Column(Text, nullable=False, default='free')
    subscribed = Column(Boolean, nullable=False, default=False)
    subscription_start = Column(Date)
    subscription_end = Column(Date)
    stripe_customer_id = Column(Text)
    stripe_subscription_id = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

class ContactMessage(Base):
    __tablename__ = "contact_messages"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(Text, nullable=False)
    email = Column(Text, nullable=False)
    subject = Column(Text, nullable=False)
    message = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Template(Base):
    __tablename__ = "templates"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey('auth.users.id', ondelete='CASCADE'), nullable=False) # New column
    name = Column(String, nullable=False, unique=True)
    dsl = Column(JSONB, nullable=False)
    version = Column(Integer, nullable=False, default=1)
    created_by = Column(UUID(as_uuid=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class ProvenanceRecord(Base):
    __tablename__ = "provenance_records"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    entity_table = Column(Text, nullable=False)
    entity_id = Column(UUID(as_uuid=True), nullable=False)
    source_url = Column(Text)
    job_id = Column(UUID(as_uuid=True))
    template_id = Column(UUID(as_uuid=True))
    template_version = Column(Integer)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class ErasureTombstone(Base):
    __tablename__ = "erasure_tombstones"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    entity_table = Column(Text, nullable=False)
    entity_id = Column(UUID(as_uuid=True), nullable=False)
    erasure_reason = Column(Text)
    requested_by = Column(UUID(as_uuid=True))
    erased_at = Column(DateTime(timezone=True), server_default=func.now())

class Page(Base):
    __tablename__ = "pages"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    url = Column(Text, nullable=False)
    canonical_url = Column(Text)
    host = Column(Text, nullable=False)
    depth = Column(Integer)
    http_status = Column(Integer)
    last_fetch_at = Column(DateTime(timezone=True))
    etag = Column(Text)
    last_modified = Column(Text)
    template_guess = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Link(Base):
    __tablename__ = "links"
    id = Column(BigInteger, primary_key=True)
    source_page_id = Column(UUID(as_uuid=True), ForeignKey('pages.id', ondelete='CASCADE'), nullable=False)
    destination_url = Column(Text, nullable=False)
    rel_attr = Column(Text)
    anchor_text = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Fetch(Base):
    __tablename__ = "fetches"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    page_id = Column(UUID(as_uuid=True), ForeignKey('pages.id', ondelete='CASCADE'), nullable=False)
    started_at = Column(DateTime(timezone=True), nullable=False)
    duration_ms = Column(Integer)
    http_status = Column(Integer)
    proxy_id = Column(Text)
    bytes_downloaded = Column(BigInteger)
    error_message = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class ScrapingJob(Base):
    __tablename__ = "scraping_jobs"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey('auth.users.id', ondelete='CASCADE'), nullable=False) # New column
    job_type = Column(String, nullable=False)
    status = Column(String, default=JobStatus.PENDING.value, nullable=False)
    domain = Column(Text)
    template_id = Column(BigInteger) # Assuming this links to a template table
    params_json = Column(JSONB)
    started_at = Column(DateTime(timezone=True))
    finished_at = Column(DateTime(timezone=True))
    error_text = Column(Text)
    result_location = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

# --- Operational Models (Existing, updated with tenant_id) ---

class Job(Base):
    __tablename__ = "scraping_jobs" # Re-using scraping_jobs table for Job model
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey('auth.users.id', ondelete='CASCADE'), nullable=False)
    job_type = Column(String, nullable=False)
    start_url = Column(String, nullable=False)
    status = Column(String, default=JobStatus.PENDING.value, nullable=False)
    params = Column(JSONB)
    result = Column(JSONB)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    started_at = Column(DateTime(timezone=True))
    finished_at = Column(DateTime(timezone=True))
    # Added fields for job status enrichment
    progress_queued = Column(Integer, default=0)
    progress_in_flight = Column(Integer, default=0)
    progress_completed = Column(Integer, default=0)
    progress_failed = Column(Integer, default=0)
    metrics_throughput_per_min = Column(Numeric)
    metrics_p95_latency_ms = Column(Numeric)
    metrics_goodput_ratio = Column(Numeric)
    metrics_ban_rate = Column(Numeric)
    export_status = Column(Text)
    export_artifacts = Column(JSONB) # List of dicts for artifacts
    logs_stdout_url = Column(Text)
    logs_errors_url = Column(Text)


class OAuthClient(Base):
    __tablename__ = "oauth_clients"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    client_id = Column(Text, nullable=False, unique=True)
    client_secret_hash = Column(Text, nullable=False)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey('auth.users.id', ondelete='CASCADE'), nullable=False)
    scopes = Column(JSONB, default=[])
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

class RolePermission(Base):
    __tablename__ = "role_permissions"
    role_name = Column(Text, primary_key=True)
    scope = Column(Text, primary_key=True)

class IdempotencyKey(Base):
    __tablename__ = "idempotency_keys"
    key = Column(Text, primary_key=True)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey('auth.users.id', ondelete='CASCADE'), nullable=False)
    path = Column(Text, nullable=False)
    method = Column(Text, nullable=False)
    response_status = Column(Integer)
    response_body = Column(JSONB)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class UserQuota(Base):
    __tablename__ = "user_quotas"
    tenant_id = Column(UUID(as_uuid=True), ForeignKey('auth.users.id', ondelete='CASCADE'), primary_key=True)
    quota_type = Column(Text, primary_key=True) # e.g., 'http_requests', 'browser_requests', 'data_exports_mb'
    current_usage = Column(Numeric, nullable=False, default=0)
    limit = Column(Numeric, nullable=False)
    period_start = Column(DateTime(timezone=True), server_default=func.now())
    period_end = Column(DateTime(timezone=True))
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

# New SQLAlchemy models for Webhooks
class WebhookEndpoint(Base):
    __tablename__ = "webhook_endpoints"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey('auth.users.id', ondelete='CASCADE'), nullable=False)
    url = Column(Text, nullable=False)
    secret = Column(Text, nullable=False)
    event_types = Column(JSONB, nullable=False) # Store as JSONB array of strings
    description = Column(Text)
    active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

class WebhookDelivery(Base):
    __tablename__ = "webhook_deliveries"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    endpoint_id = Column(UUID(as_uuid=True), ForeignKey('webhook_endpoints.id', ondelete='CASCADE'), nullable=False)
    event_id = Column(Text, nullable=False) # Corresponds to WebhookEvent.event_id
    status_code = Column(Integer)
    attempt_count = Column(Integer, default=0)
    last_attempt_at = Column(DateTime(timezone=True))
    next_attempt_at = Column(DateTime(timezone=True))
    error_message = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    tenant_id = Column(UUID(as_uuid=True), ForeignKey('auth.users.id', ondelete='CASCADE'), nullable=False) # New field


# --- Pydantic Models for API ---

# OAuth2 Models
class TokenRequest(BaseModel):
    grant_type: str
    client_id: str
    client_secret: str
    scope: Optional[str] = None

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "Bearer"
    expires_in: int
    scope: str

# API Key Models
class APIKeyCreate(BaseModel):
    key_name: str
    scopes: List[str] = Field(default_factory=list)
    expires_in_days: Optional[int] = None

class APIKeyRead(BaseModel):
    id: uuid.UUID
    key_name: str
    scopes: List[str]
    last_used_at: Optional[datetime.datetime]
    expires_at: Optional[datetime.datetime]
    is_active: bool
    created_at: datetime.datetime
    tenant_id: uuid.UUID # Include tenant_id in read model

    class Config:
        orm_mode = True

class APIKeySecret(APIKeyRead):
    secret: str # Only returned on creation

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
    type: Literal["internal_staging", "s3_presigned", "gcs_signed", "supabase_storage"] = "internal_staging" # Added supabase_storage
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

# New Pydantic models for Export API
class ExportCreate(BaseModel):
    export_type: str # e.g., 'person', 'company', 'vehicle'
    filters: Dict[str, Any] = Field(default_factory=dict) # Filters for the data to export
    format: Literal["json", "csv", "ndjson"] = "csv"
    compress: Literal["none", "gzip"] = "gzip"
    destination: ExportDestination = Field(default_factory=ExportDestination)
    file_name_prefix: Optional[str] = None

class ExportRead(BaseModel):
    id: uuid.UUID
    user_id: Optional[uuid.UUID]
    export_type: str
    file_name: str
    file_size_mb: Optional[float]
    credits_used: int
    status: str
    download_url: Optional[str]
    expires_at: Optional[datetime.datetime]
    created_at: datetime.datetime
    filters_json: Optional[Dict[str, Any]]

    class Config:
        orm_mode = True

# General Job Models
class JobProgress(BaseModel):
    queued: int = 0
    in_flight: int = 0
    completed: int = 0
    failed: int = 0

class JobMetrics(BaseModel):
    throughput_per_min: Optional[float] = None
    p95_latency_ms: Optional[float] = None
    goodput_ratio: Optional[float] = None
    ban_rate: Optional[float] = None

class JobExportArtifact(BaseModel):
    name: str
    size_bytes: Optional[int] = None
    download_url: Optional[str] = None
    expires_at: Optional[datetime.datetime] = None

class JobExport(BaseModel):
    status: str
    artifacts: List[JobExportArtifact] = Field(default_factory=list)

class JobLogs(BaseModel):
    stdout: Optional[str] = None
    errors: Optional[str] = None

class JobLinks(BaseModel):
    self: str
    cancel: Optional[str] = None

class JobRead(BaseModel):
    id: uuid.UUID
    tenant_id: uuid.UUID
    job_type: JobType
    start_url: str
    status: JobStatus
    params: Optional[Dict[str, Any]] = None
    result: Optional[Dict[str, Any]] = None
    created_at: datetime.datetime
    started_at: Optional[datetime.datetime] = None
    finished_at: Optional[datetime.datetime] = None
    
    # New fields for enriched status
    progress: JobProgress = Field(default_factory=JobProgress)
    metrics: JobMetrics = Field(default_factory=JobMetrics)
    export: Optional[JobExport] = None # Only for scrape/export jobs that produce artifacts
    logs: JobLogs = Field(default_factory=JobLogs)
    links: JobLinks # Updated to use JobLinks model

    class Config:
        orm_mode = True
        # Allow population by field name for SQLAlchemy ORM objects
        from_attributes = True 

    @model_validator(mode='before')
    @classmethod
    def populate_nested_fields_from_orm(cls, data: Any) -> Any:
        if isinstance(data, dict):
            return data
        
        # Assume data is an SQLAlchemy ORM object
        # Manually map ORM attributes to Pydantic nested models
        if hasattr(data, 'progress_queued'):
            data.progress = JobProgress(
                queued=data.progress_queued,
                in_flight=data.progress_in_flight,
                completed=data.progress_completed,
                failed=data.progress_failed
            )
        if hasattr(data, 'metrics_throughput_per_min'):
            data.metrics = JobMetrics(
                throughput_per_min=data.metrics_throughput_per_min,
                p95_latency_ms=data.metrics_p95_latency_ms,
                goodput_ratio=data.metrics_goodput_ratio,
                ban_rate=data.metrics_ban_rate
            )
        if hasattr(data, 'export_status'):
            data.export = JobExport(
                status=data.export_status,
                artifacts=data.export_artifacts if data.export_artifacts else []
            )
        if hasattr(data, 'logs_stdout_url'):
            data.logs = JobLogs(
                stdout=data.logs_stdout_url,
                errors=data.logs_errors_url
            )
        
        # Construct links
        job_id_str = str(data.id)
        data.links = JobLinks(
            self=f"/v1/jobs/{job_id_str}",
            cancel=f"/v1/jobs/{job_id_str}/cancel" if data.status in [JobStatus.QUEUED.value, JobStatus.RUNNING.value] else None
        )
        return data


# Template Models
class TemplateBase(BaseModel):
    name: str = Field(..., pattern=r"^[a-zA-Z0-9_.-]+$")
    dsl: Dict[str, Any]

class TemplateCreate(TemplateBase):
    message: Optional[str] = Field(None, description="Commit message for the template change.")
    validate_only: bool = Field(False, description="If true, only validate the template without saving.")

class TemplateUpdate(TemplateBase):
    message: Optional[str] = Field(None, description="Commit message for the template change.")
    validate_only: bool = Field(False, description="If true, only validate the template without saving.")

class TemplateRead(TemplateBase):
    id: uuid.UUID
    tenant_id: uuid.UUID # New column
    version: int
    created_at: datetime.datetime
    updated_at: Optional[datetime.datetime] = None
    etag: Optional[str] = None # For optimistic concurrency
    status: str = Field("stored", description="Current status of the template (e.g., stored, active, draft).")
    links: Dict[str, str] = Field(default_factory=dict) # Links to versions, validation endpoint etc.

    class Config:
        orm_mode = True