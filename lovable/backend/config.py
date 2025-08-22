"""
Lovable Backend Configuration

Configuration management and environment-specific settings.
"""

import os
from typing import List, Optional, Dict, Any
from pydantic import BaseSettings, Field, validator
from functools import lru_cache


class DatabaseSettings(BaseSettings):
    """Database configuration."""
    
    url: str = Field(
        default="sqlite:///./lovable.db",
        env="DATABASE_URL",
        description="Database connection URL"
    )
    echo: bool = Field(
        default=False,
        env="DATABASE_ECHO",
        description="Echo SQL queries"
    )
    pool_size: int = Field(
        default=10,
        env="DATABASE_POOL_SIZE",
        description="Connection pool size"
    )
    max_overflow: int = Field(
        default=20,
        env="DATABASE_MAX_OVERFLOW",
        description="Max connection overflow"
    )
    pool_timeout: int = Field(
        default=30,
        env="DATABASE_POOL_TIMEOUT",
        description="Pool timeout in seconds"
    )
    pool_recycle: int = Field(
        default=3600,
        env="DATABASE_POOL_RECYCLE",
        description="Pool recycle time in seconds"
    )
    
    class Config:
        env_prefix = "DATABASE_"


class RedisSettings(BaseSettings):
    """Redis configuration."""
    
    url: str = Field(
        default="redis://localhost:6379/0",
        env="REDIS_URL",
        description="Redis connection URL"
    )
    max_connections: int = Field(
        default=20,
        env="REDIS_MAX_CONNECTIONS",
        description="Maximum Redis connections"
    )
    socket_timeout: int = Field(
        default=30,
        env="REDIS_SOCKET_TIMEOUT",
        description="Redis socket timeout"
    )
    
    class Config:
        env_prefix = "REDIS_"


class JWTSettings(BaseSettings):
    """JWT configuration."""
    
    secret_key: str = Field(
        default="your-secret-key-here",
        env="JWT_SECRET_KEY",
        description="JWT secret key"
    )
    algorithm: str = Field(
        default="HS256",
        env="JWT_ALGORITHM",
        description="JWT algorithm"
    )
    access_token_expire_minutes: int = Field(
        default=30,
        env="JWT_ACCESS_TOKEN_EXPIRE_MINUTES",
        description="Access token expiration in minutes"
    )
    refresh_token_expire_days: int = Field(
        default=7,
        env="JWT_REFRESH_TOKEN_EXPIRE_DAYS",
        description="Refresh token expiration in days"
    )
    
    @validator("secret_key")
    def validate_secret_key(cls, v):
        if len(v) < 32:
            raise ValueError("JWT secret key must be at least 32 characters long")
        return v
    
    class Config:
        env_prefix = "JWT_"


class SecuritySettings(BaseSettings):
    """Security configuration."""
    
    bcrypt_rounds: int = Field(
        default=12,
        env="BCRYPT_ROUNDS",
        description="Bcrypt hashing rounds"
    )
    password_min_length: int = Field(
        default=8,
        env="PASSWORD_MIN_LENGTH",
        description="Minimum password length"
    )
    max_login_attempts: int = Field(
        default=5,
        env="MAX_LOGIN_ATTEMPTS",
        description="Maximum login attempts before lockout"
    )
    login_attempt_timeout: int = Field(
        default=900,  # 15 minutes
        env="LOGIN_ATTEMPT_TIMEOUT",
        description="Login attempt timeout in seconds"
    )
    
    class Config:
        env_prefix = "SECURITY_"


class CORSSettings(BaseSettings):
    """CORS configuration."""
    
    allow_origins: List[str] = Field(
        default=["http://localhost:3000", "http://localhost:5173"],
        env="CORS_ALLOW_ORIGINS",
        description="Allowed CORS origins"
    )
    allow_methods: List[str] = Field(
        default=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        env="CORS_ALLOW_METHODS",
        description="Allowed CORS methods"
    )
    allow_headers: List[str] = Field(
        default=["*"],
        env="CORS_ALLOW_HEADERS",
        description="Allowed CORS headers"
    )
    allow_credentials: bool = Field(
        default=True,
        env="CORS_ALLOW_CREDENTIALS",
        description="Allow CORS credentials"
    )
    
    @validator("allow_origins", pre=True)
    def parse_origins(cls, v):
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v
    
    @validator("allow_methods", pre=True)
    def parse_methods(cls, v):
        if isinstance(v, str):
            return [method.strip().upper() for method in v.split(",")]
        return v
    
    @validator("allow_headers", pre=True)
    def parse_headers(cls, v):
        if isinstance(v, str):
            return [header.strip() for header in v.split(",")]
        return v
    
    class Config:
        env_prefix = "CORS_"


class RateLimitSettings(BaseSettings):
    """Rate limiting configuration."""
    
    enabled: bool = Field(
        default=True,
        env="RATE_LIMIT_ENABLED",
        description="Enable rate limiting"
    )
    requests_per_minute: int = Field(
        default=100,
        env="RATE_LIMIT_REQUESTS_PER_MINUTE",
        description="Requests per minute limit"
    )
    burst_requests: int = Field(
        default=20,
        env="RATE_LIMIT_BURST_REQUESTS",
        description="Burst requests limit"
    )
    
    class Config:
        env_prefix = "RATE_LIMIT_"


class LoggingSettings(BaseSettings):
    """Logging configuration."""
    
    level: str = Field(
        default="INFO",
        env="LOG_LEVEL",
        description="Logging level"
    )
    format: str = Field(
        default="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        env="LOG_FORMAT",
        description="Log format"
    )
    file: Optional[str] = Field(
        default=None,
        env="LOG_FILE",
        description="Log file path"
    )
    max_bytes: int = Field(
        default=10_000_000,  # 10MB
        env="LOG_MAX_BYTES",
        description="Maximum log file size in bytes"
    )
    backup_count: int = Field(
        default=5,
        env="LOG_BACKUP_COUNT",
        description="Number of backup log files"
    )
    
    @validator("level")
    def validate_level(cls, v):
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if v.upper() not in valid_levels:
            raise ValueError(f"Log level must be one of {valid_levels}")
        return v.upper()
    
    class Config:
        env_prefix = "LOG_"


class AppSettings(BaseSettings):
    """Main application configuration."""
    
    # App info
    name: str = Field(default="Lovable Backend", description="Application name")
    version: str = Field(default="1.0.0", description="Application version")
    description: str = Field(default="Lovable Backend API", description="Application description")
    
    # Environment
    environment: str = Field(
        default="development",
        env="ENVIRONMENT",
        description="Application environment"
    )
    debug: bool = Field(
        default=False,
        env="DEBUG",
        description="Debug mode"
    )
    
    # Server
    host: str = Field(
        default="0.0.0.0",
        env="HOST",
        description="Server host"
    )
    port: int = Field(
        default=8000,
        env="PORT",
        description="Server port"
    )
    reload: bool = Field(
        default=False,
        env="RELOAD",
        description="Auto-reload server"
    )
    
    # API
    api_v1_prefix: str = Field(
        default="/api/v1",
        env="API_V1_PREFIX",
        description="API v1 prefix"
    )
    docs_url: Optional[str] = Field(
        default="/docs",
        env="DOCS_URL",
        description="API docs URL"
    )
    redoc_url: Optional[str] = Field(
        default="/redoc",
        env="REDOC_URL",
        description="ReDoc URL"
    )
    
    # Sub-configurations
    database: DatabaseSettings = DatabaseSettings()
    redis: RedisSettings = RedisSettings()
    jwt: JWTSettings = JWTSettings()
    security: SecuritySettings = SecuritySettings()
    cors: CORSSettings = CORSSettings()
    rate_limit: RateLimitSettings = RateLimitSettings()
    logging: LoggingSettings = LoggingSettings()
    
    @validator("environment")
    def validate_environment(cls, v):
        valid_envs = ["development", "testing", "staging", "production"]
        if v.lower() not in valid_envs:
            raise ValueError(f"Environment must be one of {valid_envs}")
        return v.lower()
    
    @property
    def is_development(self) -> bool:
        return self.environment == "development"
    
    @property
    def is_production(self) -> bool:
        return self.environment == "production"
    
    @property
    def is_testing(self) -> bool:
        return self.environment == "testing"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


@lru_cache()
def get_settings() -> AppSettings:
    """Get application settings (cached)."""
    return AppSettings()


def get_config() -> AppSettings:
    """Get application configuration."""
    return get_settings()
