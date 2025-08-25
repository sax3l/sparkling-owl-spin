"""
Pydantic schemas for API request/response validation.
"""

from .auth import (
    UserCreate, UserUpdate, UserResponse, UserProfile,
    Token, TokenData, PasswordReset, PasswordChange,
    APIKeyCreate, APIKeyResponse
)
from .webhooks import (
    WebhookCreate, WebhookUpdate, WebhookResponse,
    WebhookDeliveryResponse, WebhookTest
)
from .jobs import (
    CrawlJobCreate, CrawlJobUpdate, CrawlJobResponse,
    ScrapeJobCreate, ScrapeJobUpdate, ScrapeJobResponse,
    JobSummary
)
from .common import (
    HealthResponse, ErrorResponse, PaginatedResponse,
    StatusResponse
)

__all__ = [
    # Auth schemas
    "UserCreate", "UserUpdate", "UserResponse", "UserProfile",
    "Token", "TokenData", "PasswordReset", "PasswordChange",
    "APIKeyCreate", "APIKeyResponse",
    
    # Webhook schemas
    "WebhookCreate", "WebhookUpdate", "WebhookResponse",
    "WebhookDeliveryResponse", "WebhookTest",
    
    # Job schemas
    "CrawlJobCreate", "CrawlJobUpdate", "CrawlJobResponse",
    "ScrapeJobCreate", "ScrapeJobUpdate", "ScrapeJobResponse",
    "JobSummary",
    
    # Common schemas
    "HealthResponse", "ErrorResponse", "PaginatedResponse",
    "StatusResponse"
]
