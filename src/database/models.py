from sqlalchemy import create_engine, Column, String, DateTime, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import declarative_base
from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum
import uuid
import datetime

Base = declarative_base()

class JobType(str, Enum):
    CRAWL = "crawl"
    SCRAPE = "scrape"

class JobStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"

class Job(Base):
    __tablename__ = "scraping_jobs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    job_type = Column(String, nullable=False)
    status = Column(String, nullable=False, default=JobStatus.PENDING)
    start_url = Column(String, nullable=False)
    params = Column(JSON)
    result = Column(JSON)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    started_at = Column(DateTime, nullable=True)
    finished_at = Column(DateTime, nullable=True)

# Pydantic models for API validation
class JobCreate(BaseModel):
    start_url: str
    job_type: JobType
    params: Optional[dict] = None

class JobRead(BaseModel):
    id: uuid.UUID
    start_url: str
    job_type: JobType
    status: JobStatus
    created_at: datetime.datetime
    updated_at: datetime.datetime
    
    class Config:
        orm_mode = True