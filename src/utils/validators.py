import re
from typing import Any, Dict

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