"""
Configuration management for the web application.
"""
import os
from typing import Optional, List, Dict, Any
from pydantic import BaseSettings, Field
from functools import lru_cache

class DatabaseSettings(BaseSettings):
    """Database configuration."""
    url: str = Field(default="postgresql://user:pass@localhost/crawler", env="DATABASE_URL")
    pool_size: int = Field(default=10, env="DB_POOL_SIZE")
    max_overflow: int = Field(default=20, env="DB_MAX_OVERFLOW")
    pool_timeout: int = Field(default=30, env="DB_POOL_TIMEOUT")
    pool_recycle: int = Field(default=3600, env="DB_POOL_RECYCLE")
    echo: bool = Field(default=False, env="DB_ECHO")

class RedisSettings(BaseSettings):
    """Redis configuration."""
    url: str = Field(default="redis://localhost:6379/0", env="REDIS_URL")
    max_connections: int = Field(default=20, env="REDIS_MAX_CONNECTIONS")
    retry_on_timeout: bool = Field(default=True, env="REDIS_RETRY_ON_TIMEOUT")
    health_check_interval: int = Field(default=30, env="REDIS_HEALTH_CHECK_INTERVAL")

class SecuritySettings(BaseSettings):
    """Security configuration."""
    secret_key: str = Field(env="SECRET_KEY")
    allowed_hosts: Optional[List[str]] = Field(default=None, env="ALLOWED_HOSTS")
    allowed_ips: Optional[List[str]] = Field(default=None, env="ALLOWED_IPS")
    blocked_ips: Optional[List[str]] = Field(default=None, env="BLOCKED_IPS")
    cors_origins: List[str] = Field(default=["*"], env="CORS_ORIGINS")
    csrf_enabled: bool = Field(default=True, env="CSRF_ENABLED")
    
    class Config:
        env_prefix = "SECURITY_"

class RateLimitingSettings(BaseSettings):
    """Rate limiting configuration."""
    enabled: bool = Field(default=True, env="RATE_LIMITING_ENABLED")
    default_limit: str = Field(default="100/hour", env="RATE_LIMIT_DEFAULT")
    default_window: int = Field(default=3600, env="RATE_LIMIT_WINDOW")
    redis_key_prefix: str = Field(default="rate_limit:", env="RATE_LIMIT_PREFIX")
    
    class Config:
        env_prefix = "RATE_LIMIT_"

class LoggingSettings(BaseSettings):
    """Logging configuration."""
    enabled: bool = Field(default=True, env="LOGGING_ENABLED")
    level: str = Field(default="INFO", env="LOG_LEVEL")
    format: str = Field(default="json", env="LOG_FORMAT")
    request_logging: bool = Field(default=True, env="LOG_REQUESTS")
    response_logging: bool = Field(default=False, env="LOG_RESPONSES")
    
    class Config:
        env_prefix = "LOGGING_"

class ObservabilitySettings(BaseSettings):
    """Observability configuration."""
    enabled: bool = Field(default=False, env="OBSERVABILITY_ENABLED")
    tracing_enabled: bool = Field(default=False, env="TRACING_ENABLED")
    metrics_enabled: bool = Field(default=False, env="METRICS_ENABLED")
    jaeger_endpoint: Optional[str] = Field(default=None, env="JAEGER_ENDPOINT")
    prometheus_enabled: bool = Field(default=False, env="PROMETHEUS_ENABLED")
    
    class Config:
        env_prefix = "OBSERVABILITY_"

class SchedulerSettings(BaseSettings):
    """Scheduler configuration."""
    enabled: bool = Field(default=True, env="SCHEDULER_ENABLED")
    max_workers: int = Field(default=4, env="SCHEDULER_MAX_WORKERS")
    timezone: str = Field(default="UTC", env="SCHEDULER_TIMEZONE")
    
    class Config:
        env_prefix = "SCHEDULER_"

class ProxyPoolSettings(BaseSettings):
    """Proxy pool configuration."""
    enabled: bool = Field(default=False, env="PROXY_POOL_ENABLED")
    max_proxies: int = Field(default=100, env="PROXY_POOL_MAX_PROXIES")
    health_check_interval: int = Field(default=300, env="PROXY_HEALTH_CHECK_INTERVAL")
    
    class Config:
        env_prefix = "PROXY_POOL_"

class WebhookSettings(BaseSettings):
    """Webhook configuration."""
    enabled: bool = Field(default=True, env="WEBHOOKS_ENABLED")
    max_retries: int = Field(default=3, env="WEBHOOK_MAX_RETRIES")
    timeout: int = Field(default=30, env="WEBHOOK_TIMEOUT")
    
    class Config:
        env_prefix = "WEBHOOK_"

class Settings(BaseSettings):
    """Main application settings."""
    
    # Environment
    environment: str = Field(default="development", env="ENVIRONMENT")
    debug: bool = Field(default=False, env="DEBUG")
    testing: bool = Field(default=False, env="TESTING")
    
    # Application
    app_name: str = Field(default="Web Crawler Platform", env="APP_NAME")
    app_version: str = Field(default="1.0.0", env="APP_VERSION")
    api_prefix: str = Field(default="/api/v1", env="API_PREFIX")
    
    # Server
    host: str = Field(default="0.0.0.0", env="HOST")
    port: int = Field(default=8000, env="PORT")
    workers: int = Field(default=1, env="WORKERS")
    
    # Component settings
    database: DatabaseSettings = Field(default_factory=DatabaseSettings)
    redis: RedisSettings = Field(default_factory=RedisSettings)
    security: SecuritySettings = Field(default_factory=SecuritySettings)
    rate_limiting: RateLimitingSettings = Field(default_factory=RateLimitingSettings)
    logging: LoggingSettings = Field(default_factory=LoggingSettings)
    observability: ObservabilitySettings = Field(default_factory=ObservabilitySettings)
    scheduler: SchedulerSettings = Field(default_factory=SchedulerSettings)
    proxy_pool: ProxyPoolSettings = Field(default_factory=ProxyPoolSettings)
    webhooks: WebhookSettings = Field(default_factory=WebhookSettings)
    
    class Config:
        env_file = ".env"
        env_nested_delimiter = "__"
        case_sensitive = False

    @property
    def is_production(self) -> bool:
        """Check if running in production."""
        return self.environment.lower() == "production"
    
    @property
    def is_development(self) -> bool:
        """Check if running in development."""
        return self.environment.lower() == "development"
    
    @property
    def is_testing(self) -> bool:
        """Check if running in testing mode."""
        return self.testing or self.environment.lower() == "testing"

@lru_cache()
def get_settings() -> Settings:
    """Get cached application settings."""
    return Settings()

# Convenience function for accessing settings
def get_database_url() -> str:
    """Get database URL."""
    return get_settings().database.url

def get_redis_url() -> str:
    """Get Redis URL."""
    return get_settings().redis.url

def get_secret_key() -> str:
    """Get secret key."""
    return get_settings().security.secret_key

def get_cors_origins() -> List[str]:
    """Get CORS origins."""
    return get_settings().security.cors_origins

def is_debug_mode() -> bool:
    """Check if debug mode is enabled."""
    return get_settings().debug

def is_production() -> bool:
    """Check if running in production."""
    return get_settings().is_production

# Environment-specific configurations
class DevelopmentSettings(Settings):
    """Development environment settings."""
    debug: bool = True
    environment: str = "development"
    
    class Config:
        env_file = ".env.development"

class StagingSettings(Settings):
    """Staging environment settings."""
    debug: bool = False
    environment: str = "staging"
    
    class Config:
        env_file = ".env.staging"

class ProductionSettings(Settings):
    """Production environment settings."""
    debug: bool = False
    environment: str = "production"
    
    class Config:
        env_file = ".env.production"

class TestingSettings(Settings):
    """Testing environment settings."""
    debug: bool = True
    environment: str = "testing"
    testing: bool = True
    
    class Config:
        env_file = ".env.testing"

def get_settings_for_environment(env: str) -> Settings:
    """Get settings for specific environment."""
    env = env.lower()
    
    if env == "development":
        return DevelopmentSettings()
    elif env == "staging":
        return StagingSettings()
    elif env == "production":
        return ProductionSettings()
    elif env == "testing":
        return TestingSettings()
    else:
        return Settings()

# Default settings instance
settings = get_settings()
