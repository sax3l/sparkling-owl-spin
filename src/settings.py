"""
ECaDP Backend Settings

Comprehensive configuration management according to Backend overview specification.
Supports PostgreSQL & MySQL with read/write routing, feature flags, and environment-specific overrides.
"""

import os
import yaml
from typing import List, Optional, Dict, Any, Union
from pathlib import Path
from pydantic import BaseSettings, Field, validator
from functools import lru_cache


def load_yaml_config(config_path: str) -> Dict[str, Any]:
    """Load YAML configuration file."""
    if os.path.exists(config_path):
        with open(config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f) or {}
    return {}


class DatabaseSettings(BaseSettings):
    """Database configuration with MySQL/PostgreSQL vendor support."""
    
    # Primary database connection (required)
    DB_DSN_PRIMARY: str = Field(
        env="DB_DSN_PRIMARY",
        description="Primary database DSN (writes go here)"
    )
    
    # Optional read replica connection
    DB_DSN_READREPLICA: Optional[str] = Field(
        default=None,
        env="DB_DSN_READREPLICA", 
        description="Read replica DSN (optional)"
    )
    
    # Database vendor: postgres or mysql
    DB_VENDOR: str = Field(
        default="postgres",
        env="DB_VENDOR",
        description="Database vendor: postgres or mysql"
    )
    
    # Connection pool settings
    DB_POOL_SIZE: int = Field(default=10, env="DB_POOL_SIZE")
    DB_MAX_OVERFLOW: int = Field(default=20, env="DB_MAX_OVERFLOW")
    DB_POOL_TIMEOUT: int = Field(default=30, env="DB_POOL_TIMEOUT")
    DB_POOL_RECYCLE: int = Field(default=3600, env="DB_POOL_RECYCLE")
    DB_ECHO: bool = Field(default=False, env="DB_ECHO")
    
    @validator('DB_VENDOR')
    def validate_vendor(cls, v):
        if v not in ['postgres', 'mysql']:
            raise ValueError('DB_VENDOR must be either "postgres" or "mysql"')
        return v

    class Config:
        env_prefix = "DB_"


class RedisSettings(BaseSettings):
    """Redis configuration for queues and caching."""
    
    REDIS_URL: str = Field(
        default="redis://localhost:6379/0",
        env="REDIS_URL",
        description="Redis connection URL"
    )
    
    REDIS_MAX_CONNECTIONS: int = Field(default=20, env="REDIS_MAX_CONNECTIONS")
    REDIS_SOCKET_TIMEOUT: int = Field(default=30, env="REDIS_SOCKET_TIMEOUT")
    REDIS_RETRY_ON_TIMEOUT: bool = Field(default=True, env="REDIS_RETRY_ON_TIMEOUT")
    
    class Config:
        env_prefix = "REDIS_"


class StorageSettings(BaseSettings):
    """Storage configuration for local and S3-compatible storage."""
    
    STORAGE_ROOT: str = Field(
        default="./data",
        env="STORAGE_ROOT",
        description="Local storage root directory"
    )
    
    # S3-compatible storage settings
    S3_ENDPOINT_URL: Optional[str] = Field(default=None, env="S3_ENDPOINT_URL")
    S3_BUCKET: Optional[str] = Field(default=None, env="S3_BUCKET")
    S3_ACCESS_KEY: Optional[str] = Field(default=None, env="S3_ACCESS_KEY")
    S3_SECRET_KEY: Optional[str] = Field(default=None, env="S3_SECRET_KEY")
    S3_REGION: Optional[str] = Field(default="us-east-1", env="S3_REGION")
    
    class Config:
        env_prefix = "STORAGE_"


class SecuritySettings(BaseSettings):
    """Security and authentication configuration."""
    
    # API HMAC secret for webhook signatures
    API_HMAC_SECRET: str = Field(
        env="API_HMAC_SECRET",
        description="HMAC secret for API webhook signatures"
    )
    
    # OAuth2 settings
    OAUTH2_ISSUER: str = Field(
        default="ecadp-backend",
        env="OAUTH2_ISSUER",
        description="OAuth2 token issuer"
    )
    
    # JWT settings
    JWT_SECRET_KEY: str = Field(
        env="JWT_SECRET_KEY",
        description="JWT signing key"
    )
    JWT_ALGORITHM: str = Field(default="HS256", env="JWT_ALGORITHM")
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=30, env="JWT_ACCESS_TOKEN_EXPIRE_MINUTES")
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = Field(default=7, env="JWT_REFRESH_TOKEN_EXPIRE_DAYS")
    
    # CORS settings
    CORS_ORIGINS: List[str] = Field(
        default=["http://localhost:3000", "http://127.0.0.1:3000"],
        env="CORS_ORIGINS"
    )
    CORS_ALLOW_CREDENTIALS: bool = Field(default=True, env="CORS_ALLOW_CREDENTIALS")
    CORS_ALLOW_METHODS: List[str] = Field(
        default=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        env="CORS_ALLOW_METHODS"
    )
    
    # Rate limiting
    RATE_LIMIT_REQUESTS_PER_MINUTE: int = Field(default=60, env="RATE_LIMIT_REQUESTS_PER_MINUTE")
    RATE_LIMIT_BURST: int = Field(default=100, env="RATE_LIMIT_BURST")
    
    class Config:
        env_prefix = "SECURITY_"


class NotificationSettings(BaseSettings):
    """Notification and webhook configuration."""
    
    # SMTP settings
    SMTP_HOST: Optional[str] = Field(default=None, env="SMTP_HOST")
    SMTP_PORT: Optional[int] = Field(default=587, env="SMTP_PORT")
    SMTP_USERNAME: Optional[str] = Field(default=None, env="SMTP_USERNAME")
    SMTP_PASSWORD: Optional[str] = Field(default=None, env="SMTP_PASSWORD")
    SMTP_TLS: bool = Field(default=True, env="SMTP_TLS")
    
    # Slack webhook
    SLACK_WEBHOOK_URL: Optional[str] = Field(default=None, env="SLACK_WEBHOOK_URL")
    
    # Generic webhook settings
    WEBHOOK_TIMEOUT: int = Field(default=30, env="WEBHOOK_TIMEOUT")
    WEBHOOK_MAX_RETRIES: int = Field(default=3, env="WEBHOOK_MAX_RETRIES")
    
    class Config:
        env_prefix = "NOTIFICATION_"


class ProxySettings(BaseSettings):
    """Proxy pool configuration."""
    
    # Proxy provider API keys (JSON string)
    PROXY_PROVIDER_KEYS: Optional[str] = Field(default=None, env="PROXY_PROVIDER_KEYS")
    
    # Proxy pool settings
    PROXY_POOL_SIZE: int = Field(default=100, env="PROXY_POOL_SIZE")
    PROXY_HEALTH_CHECK_INTERVAL: int = Field(default=300, env="PROXY_HEALTH_CHECK_INTERVAL")
    PROXY_ROTATION_INTERVAL: int = Field(default=900, env="PROXY_ROTATION_INTERVAL")
    
    class Config:
        env_prefix = "PROXY_"


class BrowserSettings(BaseSettings):
    """Browser and Playwright configuration."""
    
    PLAYWRIGHT_OPTS: Dict[str, Any] = Field(
        default_factory=lambda: {
            "headless": True,
            "timeout": 30000,
            "viewport": {"width": 1920, "height": 1080}
        },
        env="PLAYWRIGHT_OPTS"
    )
    
    BROWSER_POOL_SIZE: int = Field(default=5, env="BROWSER_POOL_SIZE")
    BROWSER_TIMEOUT: int = Field(default=60, env="BROWSER_TIMEOUT")
    
    class Config:
        env_prefix = "BROWSER_"


class Settings(BaseSettings):
    """Main application settings with comprehensive configuration support."""
    
    model_config = {
        "extra": "ignore",
        "env_file": ".env",
        "env_file_encoding": "utf-8"
    }
    
    # Environment and application info
    ENVIRONMENT: str = Field(default="development", env="ENVIRONMENT")
    DEBUG: bool = Field(default=False, env="DEBUG")
    LOG_LEVEL: str = Field(default="INFO", env="LOG_LEVEL")
    
    # Server configuration
    HOST: str = Field(default="0.0.0.0", env="HOST")
    PORT: int = Field(default=8000, env="PORT")
    API_PREFIX: str = Field(default="/api/v1", env="API_PREFIX")
    
    # Feature flags (loaded from config/feature_flags.yml)
    FEATURE_FLAGS: Dict[str, Any] = Field(default_factory=dict)
    
    # Component configurations
    database: DatabaseSettings = Field(default_factory=DatabaseSettings)
    redis: RedisSettings = Field(default_factory=RedisSettings)
    storage: StorageSettings = Field(default_factory=StorageSettings)
    security: SecuritySettings = Field(default_factory=SecuritySettings)
    notifications: NotificationSettings = Field(default_factory=NotificationSettings)
    proxy: ProxySettings = Field(default_factory=ProxySettings)
    browser: BrowserSettings = Field(default_factory=BrowserSettings)
    
    def __init__(self, **data):
        super().__init__(**data)
        # Load additional configuration from YAML files
        self._load_yaml_configs()
    
    def _load_yaml_configs(self):
        """Load configuration from YAML files with environment-specific overrides."""
        config_dir = Path("config")
        
        # Load main app config
        app_config = load_yaml_config(config_dir / "app_config.yml")
        
        # Load environment-specific config
        env_config_path = config_dir / "env" / f"{self.ENVIRONMENT}.yml"
        env_config = load_yaml_config(str(env_config_path))
        
        # Load feature flags
        feature_flags = load_yaml_config(config_dir / "feature_flags.yml")
        self.FEATURE_FLAGS = feature_flags.get("features", {})
        
        # Merge configurations (env overrides app)
        merged_config = {**app_config, **env_config}
        
        # Apply merged config to settings
        for key, value in merged_config.items():
            if hasattr(self, key.upper()):
                setattr(self, key.upper(), value)
    
    @validator('LOG_LEVEL')
    def validate_log_level(cls, v):
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if v.upper() not in valid_levels:
            raise ValueError(f"LOG_LEVEL must be one of {valid_levels}")
        return v.upper()
    
    @property
    def is_development(self) -> bool:
        return self.ENVIRONMENT.lower() == "development"
    
    @property
    def is_production(self) -> bool:
        return self.ENVIRONMENT.lower() == "production"
    
    @property
    def is_testing(self) -> bool:
        return self.ENVIRONMENT.lower() == "testing"


@lru_cache()
def get_settings() -> Settings:
    """Get cached application settings instance."""
    return Settings()


# Convenience functions
def get_database_dsn(read_only: bool = False) -> str:
    """Get appropriate database DSN based on read/write preference."""
    settings = get_settings()
    if read_only and settings.database.DB_DSN_READREPLICA:
        return settings.database.DB_DSN_READREPLICA
    return settings.database.DB_DSN_PRIMARY


# Global settings instance
_settings = None


def get_settings() -> Settings:
    """Get application settings singleton."""
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings
