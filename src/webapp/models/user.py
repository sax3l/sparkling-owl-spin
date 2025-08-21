"""
User model for authentication and user management.
"""

from datetime import datetime, timedelta
from typing import Optional, List

from sqlalchemy import Column, String, Boolean, DateTime, Text, Integer
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from passlib.context import CryptContext
import jwt

from .base import BaseModel

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class User(BaseModel):
    """User model for authentication and user management."""
    
    __tablename__ = "users"
    
    # Basic user information
    username = Column(String(100), unique=True, index=True, nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=True)
    
    # User status and permissions
    is_active = Column(Boolean, default=True, nullable=False)
    is_superuser = Column(Boolean, default=False, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)
    
    # Profile information
    avatar_url = Column(String(500), nullable=True)
    bio = Column(Text, nullable=True)
    timezone = Column(String(50), default="UTC", nullable=False)
    locale = Column(String(10), default="en-US", nullable=False)
    
    # Security and access tracking
    last_login = Column(DateTime(timezone=True), nullable=True)
    login_count = Column(Integer, default=0, nullable=False)
    failed_login_attempts = Column(Integer, default=0, nullable=False)
    locked_until = Column(DateTime(timezone=True), nullable=True)
    
    # Password reset
    password_reset_token = Column(String(255), nullable=True)
    password_reset_expires = Column(DateTime(timezone=True), nullable=True)
    
    # Email verification
    email_verification_token = Column(String(255), nullable=True)
    email_verification_expires = Column(DateTime(timezone=True), nullable=True)
    
    # Two-factor authentication
    totp_secret = Column(String(32), nullable=True)
    backup_codes = Column(Text, nullable=True)  # JSON array of backup codes
    
    # API access
    api_keys = relationship("APIKey", back_populates="user", cascade="all, delete-orphan")
    
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verify a plain password against its hash."""
        return pwd_context.verify(plain_password, hashed_password)
    
    @staticmethod
    def hash_password(password: str) -> str:
        """Hash a password for storing."""
        return pwd_context.hash(password)
    
    def set_password(self, password: str) -> None:
        """Set user password (hashes automatically)."""
        self.hashed_password = self.hash_password(password)
    
    def check_password(self, password: str) -> bool:
        """Check if provided password is correct."""
        return self.verify_password(password, self.hashed_password)
    
    def is_locked(self) -> bool:
        """Check if user account is locked."""
        if self.locked_until is None:
            return False
        return datetime.utcnow() < self.locked_until
    
    def lock_account(self, minutes: int = 30) -> None:
        """Lock user account for specified minutes."""
        self.locked_until = datetime.utcnow() + timedelta(minutes=minutes)
        
    def unlock_account(self) -> None:
        """Unlock user account."""
        self.locked_until = None
        self.failed_login_attempts = 0
    
    def increment_login_attempts(self) -> None:
        """Increment failed login attempts."""
        self.failed_login_attempts += 1
        
        # Lock account after 5 failed attempts
        if self.failed_login_attempts >= 5:
            self.lock_account()
    
    def successful_login(self) -> None:
        """Record successful login."""
        self.last_login = datetime.utcnow()
        self.login_count += 1
        self.failed_login_attempts = 0
        self.locked_until = None
    
    def create_access_token(self, secret_key: str, expire_minutes: int = 30) -> str:
        """Create JWT access token for user."""
        expire = datetime.utcnow() + timedelta(minutes=expire_minutes)
        to_encode = {
            "sub": str(self.id),
            "username": self.username,
            "exp": expire,
            "type": "access"
        }
        return jwt.encode(to_encode, secret_key, algorithm="HS256")
    
    def create_refresh_token(self, secret_key: str, expire_days: int = 7) -> str:
        """Create JWT refresh token for user."""
        expire = datetime.utcnow() + timedelta(days=expire_days)
        to_encode = {
            "sub": str(self.id),
            "username": self.username,
            "exp": expire,
            "type": "refresh"
        }
        return jwt.encode(to_encode, secret_key, algorithm="HS256")
    
    def generate_password_reset_token(self, secret_key: str, expire_hours: int = 1) -> str:
        """Generate password reset token."""
        expire = datetime.utcnow() + timedelta(hours=expire_hours)
        self.password_reset_expires = expire
        
        to_encode = {
            "sub": str(self.id),
            "email": self.email,
            "exp": expire,
            "type": "password_reset"
        }
        token = jwt.encode(to_encode, secret_key, algorithm="HS256")
        self.password_reset_token = token
        return token
    
    def verify_password_reset_token(self, token: str, secret_key: str) -> bool:
        """Verify password reset token."""
        try:
            if self.password_reset_token != token:
                return False
                
            if self.password_reset_expires and datetime.utcnow() > self.password_reset_expires:
                return False
                
            payload = jwt.decode(token, secret_key, algorithms=["HS256"])
            return payload.get("sub") == str(self.id) and payload.get("type") == "password_reset"
        except jwt.PyJWTError:
            return False
    
    def clear_password_reset_token(self) -> None:
        """Clear password reset token after use."""
        self.password_reset_token = None
        self.password_reset_expires = None
    
    def can_access_admin(self) -> bool:
        """Check if user can access admin features."""
        return self.is_superuser and self.is_active and self.is_verified
    
    def get_permissions(self) -> List[str]:
        """Get list of user permissions."""
        permissions = ["read:own_profile", "update:own_profile"]
        
        if self.is_verified:
            permissions.extend([
                "create:api_keys", 
                "read:api_keys",
                "delete:api_keys"
            ])
        
        if self.is_superuser:
            permissions.extend([
                "read:all_users",
                "create:users", 
                "update:users",
                "delete:users",
                "read:system_stats",
                "manage:webhooks"
            ])
            
        return permissions
    
    def to_dict(self, include_sensitive: bool = False) -> dict:
        """Convert user to dictionary, optionally excluding sensitive fields."""
        exclude_fields = []
        if not include_sensitive:
            exclude_fields = [
                "hashed_password", 
                "password_reset_token",
                "email_verification_token",
                "totp_secret",
                "backup_codes"
            ]
        
        return super().to_dict(exclude_fields=exclude_fields)
