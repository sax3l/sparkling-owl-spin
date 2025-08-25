from pydantic_settings import BaseSettings
from pydantic import Field
from functools import lru_cache
from typing import Optional, List

class Settings(BaseSettings):
    # Application settings
    APP_ENV: str = "development"
    LOG_LEVEL: str = "INFO"
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8080

    # Database settings
    DB_URL: str

    # Core crawling settings
    CRAWL_MAX_CONCURRENCY: int = 5
    CRAWL_DEFAULT_DELAY_MS: int = 1000
    CRAWL_RESPECT_ROBOTS: bool = True
    CRAWL_USER_AGENT: str = "SOS-Crawler/2.0"
    CRAWL_TIMEOUT_SECONDS: int = 30
    CRAWL_MAX_RETRIES: int = 3

    # Enhanced crawler settings
    ENHANCED_CRAWLER_ENABLED: bool = True
    MIDDLEWARE_PIPELINE: List[str] = [
        "stealth_headers",
        "proxy_rotation", 
        "rate_limiting",
        "retry_middleware"
    ]

    # Stealth browser settings  
    STEALTH_BROWSER_ENABLED: bool = True
    BROWSER_HEADLESS: bool = True
    BROWSER_POOL_SIZE: int = 3
    FINGERPRINT_POOL_SIZE: int = 50

    # Anti-detection settings
    ANTI_DETECTION_ENABLED: bool = True
    PROXY_ROTATION_ENABLED: bool = True
    CAPTCHA_SOLVER_ENABLED: bool = False
    BEHAVIOR_MIMICKING_ENABLED: bool = True

    # Distributed crawling settings
    DISTRIBUTED_ENABLED: bool = False
    REDIS_URL: Optional[str] = "redis://localhost:6379"
    NODE_ROLE: str = "crawler"  # coordinator, crawler, parser, storage
    MAX_CONCURRENT_TASKS: int = 10
    HEARTBEAT_INTERVAL: int = 30

    # Proxy settings
    PROXY_URLS: str = ""  # comma-separated
    PROXY_HEALTH_CHECK_ENABLED: bool = True
    PROXY_HEALTH_CHECK_INTERVAL: int = 300  # seconds

    # Export settings
    EXPORT_DIR: str = "data/exports"
    EXPORT_FORMATS: List[str] = ["json", "csv"]
    BQ_DATASET: Optional[str] = None
    BQ_TABLE: Optional[str] = None
    GCS_BUCKET: Optional[str] = None

    # Cloud settings
    GOOGLE_APPLICATION_CREDENTIALS: Optional[str] = None
    SUPABASE_URL: Optional[str] = None
    SUPABASE_ANON_KEY: Optional[str] = None

    # Advanced settings
    ENABLE_TELEMETRY: bool = True
    ENABLE_METRICS: bool = True
    METRICS_PORT: int = 9090
    
    # Security settings
    API_KEY: Optional[str] = None
    RATE_LIMIT_REQUESTS: int = 100
    RATE_LIMIT_WINDOW: int = 60

    class Config:
        env_file = ".env"
        extra = "ignore"

@lru_cache
def get_settings() -> Settings:
    return Settings()  # type: ignore
