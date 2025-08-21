"""
API Key model for API authentication.
"""

import secrets
import hashlib
from datetime import datetime, timedelta
from typing import Optional, List

from sqlalchemy import Column, String, Boolean, DateTime, Text, Integer, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID

from .base import BaseModel


class APIKey(BaseModel):
    """API Key model for API authentication."""
    
    __tablename__ = "api_keys"
    
    # API key identification
    name = Column(String(255), nullable=False)  # Human-readable name
    key_prefix = Column(String(10), nullable=False, index=True)  # First 8 chars of key for identification
    key_hash = Column(String(64), nullable=False, unique=True, index=True)  # SHA256 hash of full key
    
    # Owner and permissions
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    user = relationship("User", back_populates="api_keys")
    
    # Status and configuration
    is_active = Column(Boolean, default=True, nullable=False)
    is_read_only = Column(Boolean, default=False, nullable=False)
    
    # Expiration and security
    expires_at = Column(DateTime(timezone=True), nullable=True)
    last_used = Column(DateTime(timezone=True), nullable=True)
    usage_count = Column(Integer, default=0, nullable=False)
    
    # Rate limiting
    rate_limit_per_minute = Column(Integer, default=100, nullable=False)
    rate_limit_per_hour = Column(Integer, default=1000, nullable=False)
    rate_limit_per_day = Column(Integer, default=10000, nullable=False)
    
    # Access control
    allowed_ips = Column(Text, nullable=True)  # Comma-separated IP addresses/ranges
    allowed_domains = Column(Text, nullable=True)  # Comma-separated domains
    scopes = Column(Text, nullable=True)  # Comma-separated permission scopes
    
    # Usage tracking
    notes = Column(Text, nullable=True)  # User notes about this key
    
    @staticmethod
    def generate_key() -> str:
        """Generate a new API key."""
        # Generate 32 bytes of random data and encode as hex
        return secrets.token_hex(32)
    
    @staticmethod
    def hash_key(key: str) -> str:
        """Hash an API key for storage."""
        return hashlib.sha256(key.encode()).hexdigest()
    
    @staticmethod
    def get_key_prefix(key: str) -> str:
        """Get the prefix (first 8 chars) of an API key."""
        return key[:8]
    
    @classmethod
    def create_key(
        cls,
        user_id: str,
        name: str,
        expires_days: Optional[int] = None,
        is_read_only: bool = False,
        scopes: Optional[List[str]] = None,
        rate_limit_per_minute: int = 100,
        notes: Optional[str] = None
    ) -> tuple["APIKey", str]:
        """Create a new API key and return the instance and the raw key."""
        raw_key = cls.generate_key()
        key_hash = cls.hash_key(raw_key)
        key_prefix = cls.get_key_prefix(raw_key)
        
        expires_at = None
        if expires_days:
            expires_at = datetime.utcnow() + timedelta(days=expires_days)
        
        api_key = cls(
            name=name,
            key_prefix=key_prefix,
            key_hash=key_hash,
            user_id=user_id,
            is_read_only=is_read_only,
            expires_at=expires_at,
            scopes=",".join(scopes) if scopes else None,
            rate_limit_per_minute=rate_limit_per_minute,
            notes=notes
        )
        
        return api_key, raw_key
    
    def verify_key(self, raw_key: str) -> bool:
        """Verify a raw key against this API key."""
        if not self.is_active:
            return False
            
        if self.is_expired():
            return False
            
        return self.key_hash == self.hash_key(raw_key)
    
    def is_expired(self) -> bool:
        """Check if the API key is expired."""
        if self.expires_at is None:
            return False
        return datetime.utcnow() > self.expires_at
    
    def record_usage(self) -> None:
        """Record that this API key was used."""
        self.last_used = datetime.utcnow()
        self.usage_count += 1
    
    def get_scopes(self) -> List[str]:
        """Get list of scopes for this API key."""
        if not self.scopes:
            return []
        return [scope.strip() for scope in self.scopes.split(",")]
    
    def has_scope(self, scope: str) -> bool:
        """Check if API key has a specific scope."""
        return scope in self.get_scopes()
    
    def get_allowed_ips(self) -> List[str]:
        """Get list of allowed IP addresses."""
        if not self.allowed_ips:
            return []
        return [ip.strip() for ip in self.allowed_ips.split(",")]
    
    def is_ip_allowed(self, ip_address: str) -> bool:
        """Check if an IP address is allowed to use this key."""
        allowed_ips = self.get_allowed_ips()
        if not allowed_ips:
            return True  # No restrictions
            
        # Simple IP matching (could be enhanced with subnet support)
        return ip_address in allowed_ips
    
    def get_allowed_domains(self) -> List[str]:
        """Get list of allowed domains."""
        if not self.allowed_domains:
            return []
        return [domain.strip() for domain in self.allowed_domains.split(",")]
    
    def is_domain_allowed(self, domain: str) -> bool:
        """Check if a domain is allowed to use this key."""
        allowed_domains = self.get_allowed_domains()
        if not allowed_domains:
            return True  # No restrictions
            
        return domain in allowed_domains
    
    def can_read(self) -> bool:
        """Check if key can perform read operations."""
        return self.is_active and not self.is_expired()
    
    def can_write(self) -> bool:
        """Check if key can perform write operations."""
        return self.can_read() and not self.is_read_only
    
    def get_rate_limits(self) -> dict:
        """Get rate limit configuration."""
        return {
            "per_minute": self.rate_limit_per_minute,
            "per_hour": self.rate_limit_per_hour,
            "per_day": self.rate_limit_per_day
        }
    
    def revoke(self) -> None:
        """Revoke this API key."""
        self.is_active = False
    
    def extend_expiration(self, days: int) -> None:
        """Extend the expiration date by specified days."""
        if self.expires_at:
            self.expires_at += timedelta(days=days)
        else:
            self.expires_at = datetime.utcnow() + timedelta(days=days)
    
    def to_dict(self, include_hash: bool = False) -> dict:
        """Convert API key to dictionary."""
        exclude_fields = []
        if not include_hash:
            exclude_fields.append("key_hash")
            
        data = super().to_dict(exclude_fields=exclude_fields)
        
        # Add computed fields
        data["scopes_list"] = self.get_scopes()
        data["allowed_ips_list"] = self.get_allowed_ips()
        data["allowed_domains_list"] = self.get_allowed_domains()
        data["is_expired"] = self.is_expired()
        data["can_read"] = self.can_read()
        data["can_write"] = self.can_write()
        data["rate_limits"] = self.get_rate_limits()
        
        return data
    
    def __repr__(self) -> str:
        """String representation of the API key."""
        return f"<APIKey(name='{self.name}', prefix='{self.key_prefix}', user_id='{self.user_id}')>"
