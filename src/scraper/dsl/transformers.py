import re
from decimal import Decimal, InvalidOperation
from typing import Any

def strip(value: str, args: dict) -> str:
    """Removes leading/trailing whitespace."""
    return value.strip() if isinstance(value, str) else value

def regex_extract(value: str, args: dict) -> str:
    """Extracts a value using a regex pattern."""
    pattern = args.get("pattern")
    if not pattern or not isinstance(value, str):
        return value
    match = re.search(pattern, value)
    return match.group(1).strip() if match and match.groups() else ""

def to_decimal(value: Any, args: dict) -> Decimal:
    """Converts a string to a decimal, removing currency symbols and handling commas."""
    if isinstance(value, (Decimal, int, float)):
        return Decimal(value)
    if not isinstance(value, str):
        return Decimal("0")
    cleaned_value = re.sub(r"[^\d,.-]", "", value).replace(",", ".")
    try:
        return Decimal(cleaned_value)
    except (InvalidOperation, ValueError):
        return Decimal("0")

def to_int(value: Any, args: dict) -> int:
    """Converts a value to an integer, cleaning it first."""
    if isinstance(value, int):
        return value
    if not isinstance(value, str):
        return 0
    cleaned_value = re.sub(r"[^\d-]", "", value.split(',')[0].split('.')[0])
    try:
        return int(cleaned_value)
    except (ValueError):
        return 0

def date_parse(value: str, args: dict) -> str:
    """Parses a date string into ISO format. Placeholder for a more robust implementation."""
    # TODO: Implement robust date parsing using a library like dateutil.parser
    return value

def map_values(value: str, args: dict) -> Any:
    """Maps a value to another based on a provided dictionary."""
    mapping = args.get("map", {})
    return mapping.get(value, value)

def normalize_postal_code(value: str, args: dict) -> str:
    """Normalizes a Swedish postal code to 'NNN NN' format."""
    if not isinstance(value, str): return ""
    digits = re.sub(r"\D", "", value)
    if len(digits) == 5:
        return f"{digits[:3]} {digits[3:]}"
    return value

def normalize_reg_nr(value: str, args: dict) -> str:
    """Normalizes a vehicle registration number by uppercasing and removing spaces."""
    if not isinstance(value, str): return ""
    return re.sub(r"\s", "", value).upper()

def validate_org_nr(value: str, args: dict) -> str:
    """
    Validates and normalizes a Swedish organization number.
    Does not perform checksum validation at this stage.
    """
    if not isinstance(value, str): return ""
    cleaned = re.sub(r"\D", "", value)
    if len(cleaned) == 10:
        return f"{cleaned[:6]}-{cleaned[6:]}"
    return value

TRANSFORMER_REGISTRY = {
    "strip": strip,
    "regex_extract": regex_extract,
    "to_decimal": to_decimal,
    "to_int": to_int,
    "date_parse": date_parse,
    "map_values": map_values,
    "normalize_postal_code": normalize_postal_code,
    "normalize_reg_nr": normalize_reg_nr,
    "validate_org_nr": validate_org_nr,
}