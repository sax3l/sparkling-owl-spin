import re
from decimal import Decimal, InvalidOperation

def strip(value: str, args: dict) -> str:
    """Removes leading/trailing whitespace."""
    return value.strip()

def regex_extract(value: str, args: dict) -> str:
    """Extracts a value using a regex pattern."""
    pattern = args.get("pattern")
    if not pattern or not isinstance(value, str):
        return value
    match = re.search(pattern, value)
    return match.group(1) if match and match.groups() else ""

def to_decimal(value: str, args: dict) -> Decimal:
    """Converts a string to a decimal, removing currency symbols and handling commas."""
    if not isinstance(value, str):
        return Decimal(value)
    # Remove thousands separators and replace comma decimal separator with a period
    cleaned_value = re.sub(r"[^\d,.-]", "", value).replace(",", ".")
    try:
        return Decimal(cleaned_value)
    except (InvalidOperation, ValueError):
        return Decimal("0")

def date_parse(value: str, args: dict) -> str:
    """Parses a date string into ISO format. Placeholder for a more robust implementation."""
    # TODO: Implement robust date parsing using a library like dateutil.parser
    # For now, this is a simple pass-through.
    return value

def map_values(value: str, args: dict) -> Any:
    """Maps a value to another based on a provided dictionary."""
    mapping = args.get("map", {})
    return mapping.get(value, value)

TRANSFORMER_REGISTRY = {
    "strip": strip,
    "regex_extract": regex_extract,
    "to_decimal": to_decimal,
    "date_parse": date_parse,
    "map_values": map_values,
}