from pydantic import BaseModel, Field
from typing import List, Optional
from uuid import UUID, uuid4
from enum import Enum

class JobType(str, Enum):
    CRAWL = "crawl"
    SCRAPE = "scrape"

class JobStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"

class ScrapeTask(BaseModel):
    start_url: str
    job_type: JobType
    # Add other parameters like max_depth, template_id etc. later

class Job(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    task: ScrapeTask
    status: JobStatus = JobStatus.PENDING