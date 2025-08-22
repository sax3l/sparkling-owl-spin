"""
Lovable Backend Models

Data models and database schemas.
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr


class User(BaseModel):
    """User model."""
    id: int
    username: str
    email: str
    is_active: bool = True
    created_at: datetime
    updated_at: Optional[datetime] = None


class UserCreate(BaseModel):
    """User creation model."""
    username: str
    email: EmailStr
    password: str


class UserUpdate(BaseModel):
    """User update model."""
    email: Optional[EmailStr] = None
    is_active: Optional[bool] = None


class Project(BaseModel):
    """Project model."""
    id: int
    name: str
    description: Optional[str] = None
    user_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None


class ProjectCreate(BaseModel):
    """Project creation model."""
    name: str
    description: Optional[str] = None


class Template(BaseModel):
    """Template model."""
    id: int
    name: str
    description: Optional[str] = None
    content: dict
    user_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None


class TemplateCreate(BaseModel):
    """Template creation model."""
    name: str
    description: Optional[str] = None
    content: dict


class Job(BaseModel):
    """Job model."""
    id: int
    name: str
    status: str
    project_id: int
    template_id: Optional[int] = None
    user_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None


class JobCreate(BaseModel):
    """Job creation model."""
    name: str
    project_id: int
    template_id: Optional[int] = None
    config: Optional[dict] = None


class JobUpdate(BaseModel):
    """Job update model."""
    status: Optional[str] = None
    config: Optional[dict] = None
