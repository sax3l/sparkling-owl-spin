"""Comprehensive validation utilities for the crawler system."""

import re
import ipaddress
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Union, Tuple
from urllib.parse import urlparse
from dataclasses import dataclass
from enum import Enum
import logging

logger = logging.getLogger(__name__)

# Legacy validators for backward compatibility
def not_empty(value: Any, args: Dict) -> bool:
    """Checks if a value is not None or an empty string."""
    return value is not None and value != ""

def length_range(value: str, args: Dict) -> bool:
    """Checks if a string's length is within a given range."""
    if not isinstance(value, str): return False
    return args.get("min", 0) <= len(value) <= args.get("max", float('inf'))

def regex(value: str, args: Dict) -> bool:
    """Checks if a string matches a regex pattern."""
    pattern = args.get("pattern")
    return bool(re.match(pattern, value)) if isinstance(value, str) and pattern else False

def enum(value: Any, args: Dict) -> bool:
    """Checks if a value is within a list of allowed values."""
    return value in args.get("values", [])

def in_range(value: Any, args: Dict) -> bool:
    """Checks if a numeric value is within a given range."""
    if not isinstance(value, (int, float)): return False
    return args.get("min", float('-inf')) <= value <= args.get("max", float('inf'))

def year_reasonable(value: Any, args: Dict) -> bool:
    """Checks if a year is within a reasonable range."""
    if not isinstance(value, int): return False
    return args.get("min", 1900) <= value <= args.get("max", 2100)

def postal_code_sv(value: str, args: Dict) -> bool:
    """Validates Swedish postal code format."""
    return regex(value, {"pattern": r"^\d{5}$"})

def orgnr_sv(value: str, args: Dict) -> bool:
    """Validates Swedish organization number format."""
    return regex(value, {"pattern": r"^\d{6}-?\d{4}$"})

def personnummer_sv(value: str, args: Dict) -> bool:
    """Validates Swedish personal identity number format (basic)."""
    # This is a basic format check. A full implementation would include checksum validation.
    pattern = r"^(19|20)?\d{6}[-+]?\d{4}$"
    return regex(value, {"pattern": pattern})

def vin_like(value: str, args: Dict) -> bool:
    """Validates that a string looks like a Vehicle Identification Number (VIN)."""
    if not isinstance(value, str): return False
    # Must be 17 characters long, alphanumeric, and not contain I, O, or Q.
    return len(value) == 17 and bool(re.match(r"^[A-HJ-NPR-Z0-9]{17}$", value.upper()))


# Modern validation framework
class ValidationLevel(Enum):
    """Validation strictness levels."""
    STRICT = "strict"
    NORMAL = "normal"
    LENIENT = "lenient"


@dataclass
class ValidationResult:
    """Result of a validation operation."""
    is_valid: bool
    errors: List[str]
    warnings: List[str] = None
    
    def __post_init__(self):
        if self.warnings is None:
            self.warnings = []


class BaseValidator:
    """Base class for all validators."""
    
    def __init__(self, level: ValidationLevel = ValidationLevel.NORMAL):
        self.level = level
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
    
    def _add_error(self, errors: List[str], message: str) -> None:
        """Add error message to list."""
        errors.append(message)
        self.logger.warning(f"Validation error: {message}")
    
    def _add_warning(self, warnings: List[str], message: str) -> None:
        """Add warning message to list."""
        warnings.append(message)
        self.logger.info(f"Validation warning: {message}")


class URLValidator(BaseValidator):
    """Validate URLs and web addresses."""
    
    def __init__(
        self,
        allowed_schemes: List[str] = None,
        allowed_domains: List[str] = None,
        blocked_domains: List[str] = None,
        level: ValidationLevel = ValidationLevel.NORMAL
    ):
        super().__init__(level)
        self.allowed_schemes = allowed_schemes or ["http", "https"]
        self.allowed_domains = allowed_domains or []
        self.blocked_domains = blocked_domains or []
        
        # Common dangerous schemes to block
        self.dangerous_schemes = [
            "javascript", "data", "file", "ftp", "mailto"
        ]
    
    def is_valid(self, url: str) -> bool:
        """Check if URL is valid and safe."""
        if not url or not isinstance(url, str):
            return False
        
        try:
            parsed = urlparse(url.strip())
            
            # Check scheme
            if parsed.scheme not in self.allowed_schemes:
                return False
            
            if parsed.scheme in self.dangerous_schemes:
                return False
            
            # Check domain restrictions
            if self.allowed_domains:
                domain = parsed.netloc.lower()
                # Remove port if present
                domain = domain.split(':')[0]
                
                # Check if domain or any parent domain is allowed
                allowed = False
                for allowed_domain in self.allowed_domains:
                    if domain == allowed_domain or domain.endswith(f'.{allowed_domain}'):
                        allowed = True
                        break
                
                if not allowed:
                    return False
            
            # Check blocked domains
            if self.blocked_domains:
                domain = parsed.netloc.lower()
                domain = domain.split(':')[0]
                
                for blocked_domain in self.blocked_domains:
                    if domain == blocked_domain or domain.endswith(f'.{blocked_domain}'):
                        return False
            
            # Basic format validation
            if not parsed.netloc:
                return False
            
            return True
            
        except Exception as e:
            self.logger.warning(f"URL validation error: {e}")
            return False
    
    def validate_batch(self, urls: List[str]) -> Dict[str, bool]:
        """Validate multiple URLs."""
        return {url: self.is_valid(url) for url in urls}


class EmailValidator(BaseValidator):
    """Validate email addresses."""
    
    EMAIL_PATTERN = re.compile(
        r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    )
    
    def is_valid(self, email: str) -> bool:
        """Check if email address is valid."""
        if not email or not isinstance(email, str):
            return False
        
        email = email.strip().lower()
        
        # Basic pattern matching
        if not self.EMAIL_PATTERN.match(email):
            return False
        
        # Additional checks
        if '..' in email:  # Double dots not allowed
            return False
        
        if email.startswith('.') or email.endswith('.'):
            return False
        
        return True


class PhoneValidator(BaseValidator):
    """Validate phone numbers."""
    
    def __init__(self, country: str = "SE", level: ValidationLevel = ValidationLevel.NORMAL):
        super().__init__(level)
        self.country = country
    
    def is_valid(self, phone: str) -> bool:
        """Check if phone number is valid."""
        if not phone or not isinstance(phone, str):
            return False
        
        try:
            # Basic Swedish phone number validation
            if self.country == "SE":
                # Remove spaces, hyphens, and plus signs
                cleaned = re.sub(r'[-\s+]', '', phone)
                
                # Check patterns
                patterns = [
                    r'^46\d{8,9}$',      # +46 followed by 8-9 digits
                    r'^0\d{8,9}$',       # 0 followed by 8-9 digits
                    r'^\d{8,9}$',        # 8-9 digits
                ]
                
                for pattern in patterns:
                    if re.match(pattern, cleaned):
                        return True
            
            return False
            
        except Exception as e:
            self.logger.warning(f"Phone validation error: {e}")
            return False


class PersonalNumberValidator(BaseValidator):
    """Validate Swedish personal numbers (personnummer)."""
    
    PERSONAL_NUMBER_PATTERN = re.compile(
        r'^(\d{2})?(\d{2})(\d{2})(\d{2})-?(\d{4})$'
    )
    
    def is_valid_format(self, personal_number: str) -> bool:
        """Check if personal number format is valid."""
        if not personal_number or not isinstance(personal_number, str):
            return False
        
        # Remove spaces and hyphens
        cleaned = re.sub(r'[-\s]', '', personal_number)
        
        # Check pattern
        match = self.PERSONAL_NUMBER_PATTERN.match(personal_number)
        if not match:
            return False
        
        # Basic date validation
        century, year, month, day, _ = match.groups()
        
        try:
            year_int = int(year)
            month_int = int(month)
            day_int = int(day)
            
            # Check month
            if not 1 <= month_int <= 12:
                return False
            
            # Check day (basic check)
            if not 1 <= day_int <= 31:
                return False
            
            return True
            
        except ValueError:
            return False


class CompanyNumberValidator(BaseValidator):
    """Validate Swedish company numbers (organisationsnummer)."""
    
    COMPANY_NUMBER_PATTERN = re.compile(r'^(\d{2})(\d{2})(\d{2})-?(\d{4})$')
    
    def is_valid(self, company_number: str) -> bool:
        """Check if company number is valid."""
        if not company_number or not isinstance(company_number, str):
            return False
        
        match = self.COMPANY_NUMBER_PATTERN.match(company_number)
        if not match:
            return False
        
        # Swedish company numbers start with specific prefixes
        first_two = match.group(1)
        valid_prefixes = ["16", "18", "19", "20", "21", "22", "23", "24", "25", "26", "27", "28", "29"]
        
        if first_two not in valid_prefixes:
            return False
        
        return True


class VehicleRegistrationValidator(BaseValidator):
    """Validate vehicle registration numbers."""
    
    def __init__(self, country: str = "SE", level: ValidationLevel = ValidationLevel.NORMAL):
        super().__init__(level)
        self.country = country
        
        # Swedish patterns
        if country == "SE":
            self.patterns = [
                re.compile(r'^[A-Z]{3}\s?\d{2}[A-Z]$'),  # ABC12D
                re.compile(r'^[A-Z]{3}\s?\d{3}$'),       # ABC123
                re.compile(r'^[A-Z]{2}\s?\d{3}[A-Z]$'),  # AB123C
            ]
    
    def is_valid(self, registration: str) -> bool:
        """Check if vehicle registration is valid."""
        if not registration or not isinstance(registration, str):
            return False
        
        registration = registration.upper().strip()
        
        for pattern in self.patterns:
            if pattern.match(registration):
                return True
        
        return False


class DataTypeValidator(BaseValidator):
    """Validate data types and structures."""
    
    def validate_type(self, value: Any, expected_type: type) -> bool:
        """Check if value matches expected type."""
        return isinstance(value, expected_type)
    
    def validate_structure(self, data: Dict[str, Any], schema: Dict[str, Any]) -> ValidationResult:
        """Validate data structure against schema."""
        errors = []
        warnings = []
        
        # Check required fields
        required_fields = schema.get('required', [])
        for field in required_fields:
            if field not in data:
                self._add_error(errors, f"Missing required field: {field}")
        
        # Check field types
        for field, field_schema in schema.get('properties', {}).items():
            if field in data:
                expected_type = field_schema.get('type')
                if expected_type and not self._check_field_type(data[field], expected_type):
                    self._add_error(errors, f"Field '{field}' has incorrect type")
        
        return ValidationResult(is_valid=len(errors) == 0, errors=errors, warnings=warnings)
    
    def _check_field_type(self, value: Any, expected_type: str) -> bool:
        """Check if value matches expected type string."""
        type_mapping = {
            'string': str,
            'integer': int,
            'float': float,
            'boolean': bool,
            'list': list,
            'dict': dict
        }
        
        python_type = type_mapping.get(expected_type)
        if python_type:
            return isinstance(value, python_type)
        
        return True  # Unknown type, assume valid


class TemplateValidator(BaseValidator):
    """Validate scraping templates."""
    
    def validate(self, template: Dict[str, Any]) -> ValidationResult:
        """Validate template structure and content."""
        errors = []
        warnings = []
        
        # Check required top-level fields
        required_fields = ['name', 'selectors']
        for field in required_fields:
            if not template.get(field):
                self._add_error(errors, f"Missing or empty required field: {field}")
        
        # Validate selectors
        selectors = template.get('selectors', {})
        if isinstance(selectors, dict):
            for field_name, selector in selectors.items():
                self._validate_selector(field_name, selector, errors, warnings)
        
        # Validate transformations
        transformations = template.get('transformations', {})
        if transformations:
            self._validate_transformations(transformations, errors, warnings)
        
        return ValidationResult(is_valid=len(errors) == 0, errors=errors, warnings=warnings)
    
    def _validate_selector(self, field_name: str, selector: Dict[str, Any], errors: List[str], warnings: List[str]) -> None:
        """Validate individual selector."""
        if not isinstance(selector, dict):
            self._add_error(errors, f"Selector '{field_name}' must be a dictionary")
            return
        
        # Must have either xpath or css selector
        if not selector.get('xpath') and not selector.get('css'):
            self._add_error(errors, f"Selector '{field_name}' must have either 'xpath' or 'css' selector")
        
        # Validate XPath safety
        xpath = selector.get('xpath')
        if xpath and not self._is_safe_xpath(xpath):
            self._add_warning(warnings, f"Potentially unsafe XPath in '{field_name}': {xpath}")
    
    def _validate_transformations(self, transformations: Dict[str, List[str]], errors: List[str], warnings: List[str]) -> None:
        """Validate transformation definitions."""
        valid_transformations = [
            'strip', 'lower', 'upper', 'title_case', 'to_int', 'to_float',
            'extract_numbers', 'extract_text', 'normalize_whitespace'
        ]
        
        for field, transforms in transformations.items():
            if not isinstance(transforms, list):
                self._add_error(errors, f"Transformations for '{field}' must be a list")
                continue
            
            for transform in transforms:
                if transform not in valid_transformations:
                    self._add_warning(warnings, f"Unknown transformation '{transform}' for field '{field}'")
    
    def _is_safe_xpath(self, xpath: str) -> bool:
        """Check if XPath expression is safe."""
        dangerous_patterns = [
            'script', 'javascript:', 'eval(', 'innerHTML', 'document.cookie'
        ]
        
        xpath_lower = xpath.lower()
        for pattern in dangerous_patterns:
            if pattern in xpath_lower:
                return False
        
        return True


class ConfigurationValidator(BaseValidator):
    """Validate system configurations."""
    
    def validate_crawler_config(self, config: Dict[str, Any]) -> ValidationResult:
        """Validate crawler configuration."""
        errors = []
        warnings = []
        
        crawler_config = config.get('crawler', {})
        
        # Validate max_depth
        max_depth = crawler_config.get('max_depth')
        if max_depth is not None:
            if not isinstance(max_depth, int) or max_depth < 0:
                self._add_error(errors, "max_depth must be a non-negative integer")
        
        # Validate delay_range
        delay_range = crawler_config.get('delay_range')
        if delay_range is not None:
            if not isinstance(delay_range, list) or len(delay_range) != 2:
                self._add_error(errors, "delay_range must be a list of two numbers")
            elif delay_range[0] > delay_range[1]:
                self._add_error(errors, "delay_range minimum must be less than maximum")
        
        # Validate user_agent
        user_agent = crawler_config.get('user_agent')
        if user_agent is not None and not user_agent.strip():
            self._add_error(errors, "user_agent cannot be empty")
        
        return ValidationResult(is_valid=len(errors) == 0, errors=errors, warnings=warnings)


class RateLimitValidator(BaseValidator):
    """Validate rate limiting configurations and compliance."""
    
    def check_rate_limit(
        self,
        request_times: List[datetime],
        max_requests: int,
        window_seconds: int
    ) -> bool:
        """Check if requests are within rate limit."""
        if not request_times:
            return True
        
        now = datetime.now()
        cutoff = now - timedelta(seconds=window_seconds)
        
        # Count requests within time window
        recent_requests = [t for t in request_times if t >= cutoff]
        
        return len(recent_requests) <= max_requests


class ProxyValidator(BaseValidator):
    """Validate proxy configurations."""
    
    SUPPORTED_SCHEMES = ['http', 'https', 'socks4', 'socks5']
    
    def is_valid_format(self, proxy_url: str) -> bool:
        """Check if proxy URL format is valid."""
        if not proxy_url or not isinstance(proxy_url, str):
            return False
        
        try:
            parsed = urlparse(proxy_url)
            
            # Check scheme
            if parsed.scheme not in self.SUPPORTED_SCHEMES:
                return False
            
            # Check host
            if not parsed.hostname:
                return False
            
            # Check port
            if parsed.port is None:
                return False
            
            if not 1 <= parsed.port <= 65535:
                return False
            
            return True
            
        except Exception:
            return False


class SecurityValidator(BaseValidator):
    """Validate security-related inputs and configurations."""
    
    def is_safe_xpath(self, xpath: str) -> bool:
        """Check if XPath expression is safe."""
        if not xpath or not isinstance(xpath, str):
            return False
        
        dangerous_patterns = [
            'script', 'javascript:', 'eval(', 'innerHTML',
            'document.cookie', 'window.', 'alert(', 'confirm('
        ]
        
        xpath_lower = xpath.lower()
        for pattern in dangerous_patterns:
            if pattern in xpath_lower:
                return False
        
        return True
    
    def sanitize_input(self, user_input: str) -> str:
        """Sanitize user input to prevent XSS and injection attacks."""
        if not isinstance(user_input, str):
            return str(user_input)
        
        # Remove potential script tags and dangerous content
        sanitized = re.sub(r'<script[^>]*>.*?</script>', '', user_input, flags=re.IGNORECASE | re.DOTALL)
        sanitized = re.sub(r'javascript:', '', sanitized, flags=re.IGNORECASE)
        sanitized = re.sub(r'on\w+\s*=', '', sanitized, flags=re.IGNORECASE)
        
        return sanitized.strip()


# Factory function for getting validators
def get_validator(validator_type: str, **kwargs) -> BaseValidator:
    """Factory function to get validator instances."""
    validators = {
        'url': URLValidator,
        'email': EmailValidator,
        'phone': PhoneValidator,
        'personal_number': PersonalNumberValidator,
        'company_number': CompanyNumberValidator,
        'vehicle_registration': VehicleRegistrationValidator,
        'data_type': DataTypeValidator,
        'template': TemplateValidator,
        'configuration': ConfigurationValidator,
        'rate_limit': RateLimitValidator,
        'proxy': ProxyValidator,
        'security': SecurityValidator,
    }
    
    validator_class = validators.get(validator_type)
    if not validator_class:
        raise ValueError(f"Unknown validator type: {validator_type}")
    
    return validator_class(**kwargs)

VALIDATOR_REGISTRY = {
    "not_empty": not_empty,
    "length_range": length_range,
    "regex": regex,
    "enum": enum,
    "in_range": in_range,
    "year_reasonable": year_reasonable,
    "postal_code_sv": postal_code_sv,
    "orgnr_sv": orgnr_sv,
    "personnummer_sv": personnummer_sv,
    "vin_like": vin_like,
}