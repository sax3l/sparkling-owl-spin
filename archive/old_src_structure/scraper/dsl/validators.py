from typing import Any, Dict, List, Optional, Union
import re
from decimal import Decimal
from datetime import datetime


class ValidationRule:
    """Base class for field validation rules."""
    
    def __init__(self, name: str, error_message: str = None):
        self.name = name
        self.error_message = error_message or f"Validation failed for rule: {name}"
    
    def validate(self, value: Any, context: Dict[str, Any] = None) -> bool:
        """Validate a value. Override in subclasses."""
        return True
    
    def get_error_message(self, value: Any) -> str:
        """Get error message for validation failure."""
        return self.error_message


class RequiredRule(ValidationRule):
    """Validates that a field is not empty or None."""
    
    def __init__(self, error_message: str = None):
        super().__init__("required", error_message or "Field is required")
    
    def validate(self, value: Any, context: Dict[str, Any] = None) -> bool:
        if value is None:
            return False
        if isinstance(value, str) and not value.strip():
            return False
        if isinstance(value, (list, dict)) and len(value) == 0:
            return False
        return True


class RegexRule(ValidationRule):
    """Validates that a field matches a regex pattern."""
    
    def __init__(self, pattern: str, error_message: str = None):
        self.pattern = pattern
        self.regex = re.compile(pattern)
        super().__init__("regex", error_message or f"Value must match pattern: {pattern}")
    
    def validate(self, value: Any, context: Dict[str, Any] = None) -> bool:
        if value is None:
            return True  # Required rule handles None values
        str_value = str(value)
        return bool(self.regex.match(str_value))


class LengthRangeRule(ValidationRule):
    """Validates that a field length is within a specified range."""
    
    def __init__(self, min_length: Optional[int] = None, max_length: Optional[int] = None, 
                 error_message: str = None):
        self.min_length = min_length
        self.max_length = max_length
        super().__init__("length_range", error_message or self._build_error_message())
    
    def _build_error_message(self) -> str:
        if self.min_length is not None and self.max_length is not None:
            return f"Length must be between {self.min_length} and {self.max_length}"
        elif self.min_length is not None:
            return f"Length must be at least {self.min_length}"
        elif self.max_length is not None:
            return f"Length must be at most {self.max_length}"
        return "Invalid length"
    
    def validate(self, value: Any, context: Dict[str, Any] = None) -> bool:
        if value is None:
            return True  # Required rule handles None values
        
        length = len(str(value))
        if self.min_length is not None and length < self.min_length:
            return False
        if self.max_length is not None and length > self.max_length:
            return False
        return True


class NumericRangeRule(ValidationRule):
    """Validates that a numeric field is within a specified range."""
    
    def __init__(self, min_value: Optional[float] = None, max_value: Optional[float] = None,
                 error_message: str = None):
        self.min_value = min_value
        self.max_value = max_value
        super().__init__("numeric_range", error_message or self._build_error_message())
    
    def _build_error_message(self) -> str:
        if self.min_value is not None and self.max_value is not None:
            return f"Value must be between {self.min_value} and {self.max_value}"
        elif self.min_value is not None:
            return f"Value must be at least {self.min_value}"
        elif self.max_value is not None:
            return f"Value must be at most {self.max_value}"
        return "Invalid numeric value"
    
    def validate(self, value: Any, context: Dict[str, Any] = None) -> bool:
        if value is None:
            return True  # Required rule handles None values
        
        try:
            numeric_value = float(value)
            if self.min_value is not None and numeric_value < self.min_value:
                return False
            if self.max_value is not None and numeric_value > self.max_value:
                return False
            return True
        except (ValueError, TypeError):
            return False


class EnumRule(ValidationRule):
    """Validates that a field value is in a list of allowed values."""
    
    def __init__(self, allowed_values: List[str], error_message: str = None):
        self.allowed_values = allowed_values
        super().__init__("enum", error_message or f"Value must be one of: {', '.join(allowed_values)}")
    
    def validate(self, value: Any, context: Dict[str, Any] = None) -> bool:
        if value is None:
            return True  # Required rule handles None values
        return str(value) in self.allowed_values


class CrossFieldValidator:
    """Validator for cross-field validation rules."""
    
    def __init__(self, name: str):
        self.name = name
        self.rules = []
    
    def add_rule(self, rule: ValidationRule):
        """Add a validation rule."""
        self.rules.append(rule)
    
    def validate(self, data: Dict[str, Any]) -> List[str]:
        """Validate data against all rules. Returns list of error messages."""
        errors = []
        for rule in self.rules:
            for field_name, field_value in data.items():
                if not rule.validate(field_value, data):
                    errors.append(f"{field_name}: {rule.get_error_message(field_value)}")
        return errors


# Factory functions for easy rule creation
def required(error_message: str = None) -> RequiredRule:
    return RequiredRule(error_message)

def regex(pattern: str, error_message: str = None) -> RegexRule:
    return RegexRule(pattern, error_message)

def length_range(min_length: Optional[int] = None, max_length: Optional[int] = None, 
                error_message: str = None) -> LengthRangeRule:
    return LengthRangeRule(min_length, max_length, error_message)

def numeric_range(min_value: Optional[float] = None, max_value: Optional[float] = None,
                 error_message: str = None) -> NumericRangeRule:
    return NumericRangeRule(min_value, max_value, error_message)

def enum(allowed_values: List[str], error_message: str = None) -> EnumRule:
    return EnumRule(allowed_values, error_message)
