"""
Utils Module - Shared utilities and helpers.

Provides common functionality used across the platform including:
- Logging and telemetry
- Authentication utilities
- Validation and data processing
- Rate limiting and quota management
- Idempotency handling
- Error handling and models
- URL and request utilities
- Metrics and performance monitoring

Main Components:
- Logger: Centralized logging functionality
- AuthUtils: Authentication helpers
- Validators: Data validation utilities
- RateLimiter: Request rate limiting
- QuotaManager: Resource quota management
- IdempotencyHandler: Request idempotency
- PatternDetector: Data pattern recognition
- URLUtils: URL processing helpers
- TelemetryCollector: Performance telemetry
"""

from .logger import get_logger, configure_logging
from .auth_utils import (
    verify_password, 
    get_password_hash, 
    create_access_token, 
    decode_access_token, 
    has_scope,
    get_user_scopes
)
from .validators import (
    BaseValidator, 
    URLValidator, 
    EmailValidator, 
    ValidationResult, 
    ValidationLevel
)
from .rate_limiter import TokenBucket, RateLimitMiddleware
from .quota_manager import QuotaManager
from .idempotency import IdempotencyHandler
from .pattern_detector import PatternDetector
from .url_utils import URLUtils, URLNormalizer
from .telemetry import TelemetryCollector
from .metrics import MetricsHelper
from .error_models import ErrorHandler, CustomException
from .contracts import APIContract, DataContract
from .user_agent_rotator import UserAgentRotator
from .request_id_middleware import RequestIDMiddleware
from .export_utils import ExportHelper
from .deprecation import DeprecationWarning

__all__ = [
    "get_logger",
    "configure_logging", 
    "AuthUtils",
    "TokenManager",
    "DataValidator",
    "SchemaValidator",
    "RateLimiter", 
    "RateLimitMiddleware",
    "QuotaManager",
    "IdempotencyHandler",
    "PatternDetector",
    "URLUtils",
    "URLNormalizer",
    "TelemetryCollector",
    "MetricsHelper", 
    "ErrorHandler",
    "CustomException",
    "APIContract",
    "DataContract",
    "UserAgentRotator",
    "RequestIDMiddleware",
    "ExportHelper",
    "DeprecationWarning"
]