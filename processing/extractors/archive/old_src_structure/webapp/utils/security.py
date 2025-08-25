"""
Security utilities for the webapp.
"""

import hashlib
import hmac
import secrets
import string
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from urllib.parse import urlparse

import bcrypt
from jose import jwt, JWTError
from passlib.context import CryptContext

# Import comprehensive validators instead of duplicating
from src.utils.validators import URLValidator, EmailValidator


"""
Security utilities for the webapp.
"""

import hashlib
import hmac
import secrets
import string
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from urllib.parse import urlparse

import bcrypt
from jose import jwt, JWTError
from passlib.context import CryptContext

# Import comprehensive validators instead of duplicating
from src.utils.validators import URLValidator, EmailValidator


class SecurityConfig:
    """Security configuration constants."""
    
    # Password policy
    MIN_PASSWORD_LENGTH = 8
    MAX_PASSWORD_LENGTH = 128
    PASSWORD_COMPLEXITY_REQUIRED = True
    
    # Token settings
    ACCESS_TOKEN_EXPIRE_MINUTES = 30
    REFRESH_TOKEN_EXPIRE_DAYS = 30
    API_KEY_LENGTH = 32
    
    # Rate limiting
    DEFAULT_RATE_LIMIT = 100  # requests per hour
    BURST_RATE_LIMIT = 10     # requests per minute
    
    # Security headers
    SECURITY_HEADERS = {
        'X-Content-Type-Options': 'nosniff',
        'X-Frame-Options': 'DENY',
        'X-XSS-Protection': '1; mode=block',
        'Strict-Transport-Security': 'max-age=31536000; includeSubDomains',
        'Content-Security-Policy': "default-src 'self'",
        'Referrer-Policy': 'strict-origin-when-cross-origin'
    }


class PasswordValidator:
    """Password validation and security utilities."""
    
    def __init__(self):
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    
    def validate_password_strength(self, password: str) -> tuple[bool, List[str]]:
        """
        Validate password strength.
        
        Args:
            password: Password to validate
            
        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors = []
        
        if not password:
            errors.append("Password cannot be empty")
            return False, errors
        
        if len(password) < SecurityConfig.MIN_PASSWORD_LENGTH:
            errors.append(f"Password must be at least {SecurityConfig.MIN_PASSWORD_LENGTH} characters")
        
        if len(password) > SecurityConfig.MAX_PASSWORD_LENGTH:
            errors.append(f"Password cannot exceed {SecurityConfig.MAX_PASSWORD_LENGTH} characters")
        
        if SecurityConfig.PASSWORD_COMPLEXITY_REQUIRED:
            has_upper = any(c.isupper() for c in password)
            has_lower = any(c.islower() for c in password)
            has_digit = any(c.isdigit() for c in password)
            has_special = any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password)
            
            if not has_upper:
                errors.append("Password must contain at least one uppercase letter")
            if not has_lower:
                errors.append("Password must contain at least one lowercase letter")
            if not has_digit:
                errors.append("Password must contain at least one digit")
            if not has_special:
                errors.append("Password must contain at least one special character")
        
        # Check for common weak patterns
        weak_patterns = [
            password.lower() in ['password', '123456', 'admin', 'root'],
            len(set(password)) < 4,  # Too few unique characters
            password.isdigit(),       # All digits
            password.isalpha(),       # All letters
        ]
        
        if any(weak_patterns):
            errors.append("Password is too weak or common")
        
        return len(errors) == 0, errors
    
    def hash_password(self, password: str) -> str:
        """
        Hash a password using bcrypt.
        
        Args:
            password: Plain text password
            
        Returns:
            Hashed password
        """
        return self.pwd_context.hash(password)
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """
        Verify a password against its hash.
        
        Args:
            plain_password: Plain text password
            hashed_password: Hashed password
            
        Returns:
            True if password matches
        """
        return self.pwd_context.verify(plain_password, hashed_password)
    
    def needs_update(self, hashed_password: str) -> bool:
        """
        Check if password hash needs updating.
        
        Args:
            hashed_password: Hashed password
            
        Returns:
            True if hash needs updating
        """
        return self.pwd_context.needs_update(hashed_password)


class TokenManager:
    """JWT token management utilities."""
    
    def __init__(self, secret_key: str, algorithm: str = "HS256"):
        self.secret_key = secret_key
        self.algorithm = algorithm
    
    def create_access_token(
        self, 
        data: Dict[str, Any], 
        expires_delta: Optional[timedelta] = None
    ) -> str:
        """
        Create a JWT access token.
        
        Args:
            data: Token payload data
            expires_delta: Token expiration time
            
        Returns:
            JWT token string
        """
        to_encode = data.copy()
        
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(
                minutes=SecurityConfig.ACCESS_TOKEN_EXPIRE_MINUTES
            )
        
        to_encode.update({"exp": expire, "iat": datetime.utcnow()})
        
        return jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
    
    def create_refresh_token(self, user_id: str) -> str:
        """
        Create a refresh token.
        
        Args:
            user_id: User identifier
            
        Returns:
            Refresh token string
        """
        expire = datetime.utcnow() + timedelta(days=SecurityConfig.REFRESH_TOKEN_EXPIRE_DAYS)
        
        to_encode = {
            "sub": user_id,
            "type": "refresh",
            "exp": expire,
            "iat": datetime.utcnow()
        }
        
        return jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
    
    def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """
        Verify and decode a JWT token.
        
        Args:
            token: JWT token string
            
        Returns:
            Token payload if valid, None otherwise
        """
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        except JWTError:
            return None
    
    def is_token_expired(self, token: str) -> bool:
        """
        Check if a token is expired.
        
        Args:
            token: JWT token string
            
        Returns:
            True if token is expired
        """
        try:
            payload = jwt.decode(
                token, 
                self.secret_key, 
                algorithms=[self.algorithm],
                options={"verify_exp": False}
            )
            exp = payload.get("exp")
            if exp:
                return datetime.fromtimestamp(exp) < datetime.utcnow()
            return True
        except JWTError:
            return True


class APIKeyGenerator:
    """API key generation and validation utilities."""
    
    @staticmethod
    def generate_api_key() -> str:
        """
        Generate a secure API key.
        
        Returns:
            API key string
        """
        alphabet = string.ascii_letters + string.digits
        return ''.join(secrets.choice(alphabet) for _ in range(SecurityConfig.API_KEY_LENGTH))
    
    @staticmethod
    def generate_api_key_with_prefix(prefix: str = "dyad") -> str:
        """
        Generate an API key with a prefix.
        
        Args:
            prefix: API key prefix
            
        Returns:
            API key string with prefix
        """
        key = APIKeyGenerator.generate_api_key()
        return f"{prefix}_{key}"
    
    @staticmethod
    def hash_api_key(api_key: str) -> str:
        """
        Hash an API key for storage.
        
        Args:
            api_key: Plain text API key
            
        Returns:
            Hashed API key
        """
        return hashlib.sha256(api_key.encode()).hexdigest()
    
    @staticmethod
    def verify_api_key(api_key: str, hashed_key: str) -> bool:
        """
        Verify an API key against its hash.
        
        Args:
            api_key: Plain text API key
            hashed_key: Hashed API key
            
        Returns:
            True if API key matches
        """
        return hashlib.sha256(api_key.encode()).hexdigest() == hashed_key


class WebhookSecurity:
    """Webhook security utilities."""
    
    @staticmethod
    def generate_webhook_secret() -> str:
        """
        Generate a webhook secret.
        
        Returns:
            Webhook secret string
        """
        return secrets.token_urlsafe(32)
    
    @staticmethod
    def create_signature(payload: bytes, secret: str) -> str:
        """
        Create a webhook signature.
        
        Args:
            payload: Webhook payload bytes
            secret: Webhook secret
            
        Returns:
            HMAC signature
        """
        return hmac.new(
            secret.encode(),
            payload,
            hashlib.sha256
        ).hexdigest()
    
    @staticmethod
    def verify_signature(payload: bytes, signature: str, secret: str) -> bool:
        """
        Verify a webhook signature.
        
        Args:
            payload: Webhook payload bytes
            signature: Provided signature
            secret: Webhook secret
            
        Returns:
            True if signature is valid
        """
        expected_signature = WebhookSecurity.create_signature(payload, secret)
        return hmac.compare_digest(signature, expected_signature)


def is_safe_url(url: str, allowed_hosts: Optional[List[str]] = None) -> bool:
    """
    Check if URL is safe to access.
    
    Args:
        url: URL to validate
        allowed_hosts: List of allowed hostnames
        
    Returns:
        True if URL is safe
    """
    validator = URLValidator(
        allowed_schemes=['http', 'https'],
        allowed_domains=allowed_hosts if allowed_hosts else [],
        blocked_domains=['localhost', '127.0.0.1', '::1']
    )
    
    if not validator.is_valid(url):
        return False
    
    parsed = urlparse(url)
    hostname = parsed.hostname
    
    if hostname:
        # Block private IP ranges (basic check)
        if hostname.startswith(('10.', '172.', '192.168.')):
            return False
    
    return True


class InputSanitizer:
    """Input sanitization utilities."""
    
    @staticmethod
    def sanitize_string(value: str, max_length: int = 1000) -> str:
        """
        Sanitize string input.
        
        Args:
            value: String to sanitize
            max_length: Maximum allowed length
            
        Returns:
            Sanitized string
        """
        if not isinstance(value, str):
            return ""
        
        # Truncate to max length
        value = value[:max_length]
        
        # Remove null bytes
        value = value.replace('\x00', '')
        
        # Strip whitespace
        value = value.strip()
        
        return value
    
    @staticmethod
    def sanitize_html(value: str) -> str:
        """
        Basic HTML sanitization (removes common dangerous tags).
        
        Args:
            value: HTML string to sanitize
            
        Returns:
            Sanitized HTML string
        """
        if not isinstance(value, str):
            return ""
        
        # Remove dangerous tags
        dangerous_tags = [
            '<script', '</script>',
            '<iframe', '</iframe>',
            '<object', '</object>',
            '<embed', '</embed>',
            '<link', '</link>',
            '<meta', '</meta>',
            '<style', '</style>',
        ]
        
        value_lower = value.lower()
        for tag in dangerous_tags:
            while tag in value_lower:
                start = value_lower.find(tag)
                if start == -1:
                    break
                
                # Find the end of the tag
                end = value_lower.find('>', start)
                if end == -1:
                    # Malformed tag, remove everything from start
                    value = value[:start]
                    value_lower = value_lower[:start]
                    break
                
                # Remove the tag
                value = value[:start] + value[end + 1:]
                value_lower = value_lower[:start] + value_lower[end + 1:]
        
        return value
    
def validate_email(email: str) -> bool:
    """
    Basic email validation.
    
    Args:
        email: Email address to validate
        
    Returns:
        True if email appears valid
    """
    validator = EmailValidator()
    return validator.is_valid(email)


def generate_csrf_token() -> str:
    """
    Generate a CSRF token.
    
    Returns:
        CSRF token string
    """
    return secrets.token_urlsafe(32)


def constant_time_compare(a: str, b: str) -> bool:
    """
    Constant time string comparison to prevent timing attacks.
    
    Args:
        a: First string
        b: Second string
        
    Returns:
        True if strings are equal
    """
    return hmac.compare_digest(a, b)


def get_client_ip(headers: Dict[str, str]) -> str:
    """
    Extract client IP from request headers.
    
    Args:
        headers: Request headers dictionary
        
    Returns:
        Client IP address
    """
    # Check for forwarded headers
    forwarded_headers = [
        'X-Forwarded-For',
        'X-Real-IP',
        'CF-Connecting-IP',  # Cloudflare
        'X-Client-IP',
    ]
    
    for header in forwarded_headers:
        if header in headers:
            # Take the first IP if multiple are present
            ip = headers[header].split(',')[0].strip()
            if ip:
                return ip
    
    # Fallback to unknown
    return "unknown"
