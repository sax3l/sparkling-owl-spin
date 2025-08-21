"""
Authentication and user management Pydantic schemas.
"""

from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, EmailStr, Field, validator
import re


class UserCreate(BaseModel):
    """Schema for creating a new user."""
    username: str = Field(..., min_length=3, max_length=50, description="Username")
    email: EmailStr = Field(..., description="Email address")
    password: str = Field(..., min_length=8, description="Password")
    full_name: Optional[str] = Field(None, max_length=255, description="Full name")
    timezone: str = Field("UTC", description="User timezone")
    locale: str = Field("en-US", description="User locale")
    
    @validator('username')
    def validate_username(cls, v):
        if not re.match(r'^[a-zA-Z0-9_-]+$', v):
            raise ValueError('Username can only contain letters, numbers, hyphens, and underscores')
        return v
    
    @validator('password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if not re.search(r'[A-Z]', v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not re.search(r'[a-z]', v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not re.search(r'\d', v):
            raise ValueError('Password must contain at least one number')
        return v


class UserUpdate(BaseModel):
    """Schema for updating user information."""
    email: Optional[EmailStr] = Field(None, description="Email address")
    full_name: Optional[str] = Field(None, max_length=255, description="Full name")
    bio: Optional[str] = Field(None, max_length=1000, description="User bio")
    avatar_url: Optional[str] = Field(None, max_length=500, description="Avatar URL")
    timezone: Optional[str] = Field(None, description="User timezone")
    locale: Optional[str] = Field(None, description="User locale")


class UserResponse(BaseModel):
    """Schema for user data in responses."""
    id: str = Field(..., description="User ID")
    username: str = Field(..., description="Username")
    email: str = Field(..., description="Email address")
    full_name: Optional[str] = Field(None, description="Full name")
    bio: Optional[str] = Field(None, description="User bio")
    avatar_url: Optional[str] = Field(None, description="Avatar URL")
    timezone: str = Field(..., description="User timezone")
    locale: str = Field(..., description="User locale")
    is_active: bool = Field(..., description="Whether user is active")
    is_verified: bool = Field(..., description="Whether user is verified")
    is_superuser: bool = Field(..., description="Whether user is superuser")
    created_at: datetime = Field(..., description="User creation timestamp")
    last_login: Optional[datetime] = Field(None, description="Last login timestamp")
    login_count: int = Field(..., description="Total login count")

    class Config:
        from_attributes = True


class UserProfile(BaseModel):
    """Schema for user profile (limited information)."""
    id: str = Field(..., description="User ID")
    username: str = Field(..., description="Username")
    full_name: Optional[str] = Field(None, description="Full name")
    bio: Optional[str] = Field(None, description="User bio")
    avatar_url: Optional[str] = Field(None, description="Avatar URL")
    created_at: datetime = Field(..., description="User creation timestamp")
    
    class Config:
        from_attributes = True


class Token(BaseModel):
    """Schema for authentication tokens."""
    access_token: str = Field(..., description="JWT access token")
    refresh_token: Optional[str] = Field(None, description="JWT refresh token")
    token_type: str = Field("bearer", description="Token type")
    expires_in: int = Field(..., description="Token expiration time in seconds")


class TokenData(BaseModel):
    """Schema for token payload data."""
    user_id: str = Field(..., description="User ID")
    username: str = Field(..., description="Username")
    scopes: List[str] = Field(default_factory=list, description="Token scopes")


class PasswordReset(BaseModel):
    """Schema for password reset request."""
    email: EmailStr = Field(..., description="Email address")


class PasswordChange(BaseModel):
    """Schema for password change."""
    current_password: str = Field(..., description="Current password")
    new_password: str = Field(..., min_length=8, description="New password")
    
    @validator('new_password')
    def validate_new_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if not re.search(r'[A-Z]', v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not re.search(r'[a-z]', v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not re.search(r'\d', v):
            raise ValueError('Password must contain at least one number')
        return v


class PasswordResetConfirm(BaseModel):
    """Schema for password reset confirmation."""
    token: str = Field(..., description="Password reset token")
    new_password: str = Field(..., min_length=8, description="New password")
    
    @validator('new_password')
    def validate_new_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if not re.search(r'[A-Z]', v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not re.search(r'[a-z]', v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not re.search(r'\d', v):
            raise ValueError('Password must contain at least one number')
        return v


class EmailVerification(BaseModel):
    """Schema for email verification."""
    token: str = Field(..., description="Email verification token")


class APIKeyCreate(BaseModel):
    """Schema for creating API keys."""
    name: str = Field(..., min_length=1, max_length=255, description="API key name")
    expires_days: Optional[int] = Field(None, gt=0, le=365, description="Expiration in days")
    is_read_only: bool = Field(False, description="Read-only access")
    scopes: Optional[List[str]] = Field(None, description="API key scopes")
    rate_limit_per_minute: int = Field(100, gt=0, le=10000, description="Rate limit per minute")
    allowed_ips: Optional[List[str]] = Field(None, description="Allowed IP addresses")
    allowed_domains: Optional[List[str]] = Field(None, description="Allowed domains")
    notes: Optional[str] = Field(None, max_length=1000, description="Notes about this key")


class APIKeyUpdate(BaseModel):
    """Schema for updating API keys."""
    name: Optional[str] = Field(None, min_length=1, max_length=255, description="API key name")
    is_read_only: Optional[bool] = Field(None, description="Read-only access")
    rate_limit_per_minute: Optional[int] = Field(None, gt=0, le=10000, description="Rate limit per minute")
    allowed_ips: Optional[List[str]] = Field(None, description="Allowed IP addresses")
    allowed_domains: Optional[List[str]] = Field(None, description="Allowed domains")
    notes: Optional[str] = Field(None, max_length=1000, description="Notes about this key")


class APIKeyResponse(BaseModel):
    """Schema for API key responses."""
    id: str = Field(..., description="API key ID")
    name: str = Field(..., description="API key name")
    key_prefix: str = Field(..., description="API key prefix")
    is_active: bool = Field(..., description="Whether key is active")
    is_read_only: bool = Field(..., description="Read-only access")
    expires_at: Optional[datetime] = Field(None, description="Expiration timestamp")
    last_used: Optional[datetime] = Field(None, description="Last used timestamp")
    usage_count: int = Field(..., description="Usage count")
    scopes: Optional[List[str]] = Field(None, description="API key scopes")
    rate_limit_per_minute: int = Field(..., description="Rate limit per minute")
    allowed_ips: Optional[List[str]] = Field(None, description="Allowed IP addresses")
    allowed_domains: Optional[List[str]] = Field(None, description="Allowed domains")
    notes: Optional[str] = Field(None, description="Notes about this key")
    created_at: datetime = Field(..., description="Creation timestamp")
    is_expired: bool = Field(..., description="Whether key is expired")
    can_read: bool = Field(..., description="Can perform read operations")
    can_write: bool = Field(..., description="Can perform write operations")
    
    class Config:
        from_attributes = True


class APIKeyCreateResponse(BaseModel):
    """Schema for API key creation response (includes the actual key)."""
    api_key: APIKeyResponse = Field(..., description="API key information")
    key: str = Field(..., description="The actual API key (only shown once)")


class LoginRequest(BaseModel):
    """Schema for login requests."""
    username: str = Field(..., description="Username or email")
    password: str = Field(..., description="Password")
    remember_me: bool = Field(False, description="Remember login session")


class RefreshTokenRequest(BaseModel):
    """Schema for refresh token requests."""
    refresh_token: str = Field(..., description="Refresh token")


class UserStats(BaseModel):
    """Schema for user statistics."""
    total_api_keys: int = Field(..., description="Total number of API keys")
    active_api_keys: int = Field(..., description="Number of active API keys")
    total_jobs: int = Field(..., description="Total number of jobs created")
    active_jobs: int = Field(..., description="Number of active jobs")
    data_usage_mb: float = Field(..., description="Total data usage in MB")
    api_calls_today: int = Field(..., description="API calls made today")


class TwoFactorSetup(BaseModel):
    """Schema for two-factor authentication setup."""
    secret: str = Field(..., description="TOTP secret")
    qr_code_url: str = Field(..., description="QR code URL for setup")
    backup_codes: List[str] = Field(..., description="Backup codes")


class TwoFactorVerify(BaseModel):
    """Schema for two-factor authentication verification."""
    code: str = Field(..., min_length=6, max_length=6, description="TOTP code")


class AdminUserUpdate(BaseModel):
    """Schema for admin user updates."""
    is_active: Optional[bool] = Field(None, description="Whether user is active")
    is_verified: Optional[bool] = Field(None, description="Whether user is verified")
    is_superuser: Optional[bool] = Field(None, description="Whether user is superuser")
    unlock_account: Optional[bool] = Field(None, description="Unlock user account")
    reset_failed_attempts: Optional[bool] = Field(None, description="Reset failed login attempts")
