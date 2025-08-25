"""
Lovable Backend Models

Pydantic models for request/response validation and data structures.
"""

from datetime import datetime
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, EmailStr, Field


# User models
class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    full_name: Optional[str] = Field(None, max_length=100)


class UserCreate(UserBase):
    password: str = Field(..., min_length=8)


class UserUpdate(BaseModel):
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    email: Optional[EmailStr] = None
    full_name: Optional[str] = Field(None, max_length=100)
    password: Optional[str] = Field(None, min_length=8)
    is_active: Optional[bool] = None


class UserInDB(UserBase):
    id: int
    is_active: bool = True
    is_admin: bool = False
    hashed_password: str
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True


class UserResponse(UserBase):
    id: int
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True


# Project models
class ProjectBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    status: str = Field(default="active")
    config: Optional[Dict[str, Any]] = None


class ProjectCreate(ProjectBase):
    template_id: Optional[int] = None


class ProjectUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    status: Optional[str] = None
    config: Optional[Dict[str, Any]] = None


class ProjectInDB(ProjectBase):
    id: int
    owner_id: int
    template_id: Optional[int] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True


class ProjectResponse(ProjectBase):
    id: int
    owner_id: int
    template_id: Optional[int] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True


# Template models
class TemplateBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    category: Optional[str] = Field(None, max_length=50)
    config: Dict[str, Any]
    is_public: bool = True


class TemplateCreate(TemplateBase):
    pass


class TemplateUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    category: Optional[str] = Field(None, max_length=50)
    config: Optional[Dict[str, Any]] = None
    is_public: Optional[bool] = None


class TemplateInDB(TemplateBase):
    id: int
    creator_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True


class TemplateResponse(TemplateBase):
    id: int
    creator_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True


# Job models
class JobBase(BaseModel):
    name: Optional[str] = Field(None, max_length=100)
    type: str = Field(..., max_length=50)
    config: Optional[Dict[str, Any]] = None


class JobCreate(JobBase):
    project_id: Optional[int] = None


class JobUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=100)
    status: Optional[str] = None
    config: Optional[Dict[str, Any]] = None
    result: Optional[Dict[str, Any]] = None


class JobInDB(JobBase):
    id: int
    status: str = "pending"
    result: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    progress: int = 0
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    user_id: int
    project_id: Optional[int] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True


class JobResponse(JobBase):
    id: int
    status: str
    result: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    progress: int
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    project_id: Optional[int] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True


# Authentication models
class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Optional[str] = None


class LoginRequest(BaseModel):
    username: str  # Can be username or email
    password: str


# API Response models
class APIResponse(BaseModel):
    success: bool
    message: str
    data: Optional[Any] = None


class ErrorResponse(BaseModel):
    error: str
    detail: Optional[str] = None
    code: Optional[str] = None
