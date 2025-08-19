import re
import json
from decimal import Decimal, InvalidOperation
from typing import Any, Dict

def strip(value: str, args: Dict) -> str:
    """Removes leading and trailing whitespace."""
    return value.strip() if isinstance(value, str) else value

def normalize_whitespace(value: str, args: Dict) -> str:
    """Collapses multiple whitespace characters into a single space."""
    return re.sub(r'\s+', ' ', value).strip() if isinstance(value, str) else value

def to_upper(value: str, args: Dict) -> str:
    """Converts string to uppercase."""
    return value.upper() if isinstance(value, str) else value

def to_lower(value: str, args: Dict) -> str:
    """Converts string to lowercase."""
    return value.lower() if isinstance(value, str) else value

def title_case(value: str, args: Dict) -> str:
    """Converts string to title case."""
    return value.title() if isinstance(value, str) else value

def only_digits(value: str, args: Dict) -> str:
    """Removes all non-digit characters from a string."""
    return re.sub(r'\D', '', value) if isinstance(value, str) else ''

def regex_sub(value: str, args: Dict) -> str:
    """Performs a regex substitution."""
    pattern = args.get("pattern")
    repl = args.get("repl", "")
    return re.sub(pattern, repl, value) if isinstance(value, str) and pattern else value

def parse_int(value: Any, args: Dict) -> int:
    """Parses a string into an integer, removing non-digit characters."""
    if isinstance(value, int): return value
    if not isinstance(value, str): return 0
    cleaned = re.sub(r'[^\d-]', '', value.split(',')[0].split('.')[0])
    try: return int(cleaned)
    except (ValueError): return 0

def parse_decimal(value: Any, args: Dict) -> Decimal:
    """Parses a string into a Decimal, handling custom separators."""
    if isinstance(value, (Decimal, int, float)): return Decimal(value)
    if not isinstance(value, str): return Decimal("0")
    
    decimal_sep = args.get("decimal_sep", ".")
    thousands_sep = args.get("thousands_sep", "")
    
    cleaned = value.strip()
    if thousands_sep:
        cleaned = cleaned.replace(thousands_sep, "")
    if decimal_sep != ".":
        cleaned = cleaned.replace(decimal_sep, ".")
        
    cleaned = re.sub(r"[^\d.-]", "", cleaned)
    try: return Decimal(cleaned)
    except (InvalidOperation, ValueError): return Decimal("0")

def parse_date(value: str, args: Dict) -> str:
    """Placeholder for a robust date parsing implementation."""
    # In a real scenario, this would use a library like dateutil.parser
    # from dateutil import parser
    # try: return parser.parse(value).isoformat()
    # except: return None
    return value

def currency_normalize(value: str, args: Dict) -> Decimal:
    """Normalizes a currency string into a Decimal."""
    if not isinstance(value, str): return Decimal("0")
    
    temp_val = value
    for symbol in args.get("drop_symbols", ["kr", "SEK", "$", "€"]):
        temp_val = temp_val.replace(symbol, "")
        
    return parse_decimal(temp_val, args)

def unit_extract(value: str, args: Dict) -> Dict:
    """Extracts a numeric value and a normalized unit from a string."""
    if not isinstance(value, str): return {}
    
    value_regex = args.get("value_regex", r"([0-9]+(?:[.,][0-9]+)?)")
    unit_map = args.get("unit_map", {})
    
    match = re.search(value_regex, value)
    if not match:
        return {}
        
    numeric_part = match.group(1)
    unit_part = value.replace(numeric_part, "").strip()
    
    normalized_unit = unit_map.get(unit_part, unit_part)
    
    return {
        "value": parse_decimal(numeric_part, args),
        "unit": normalized_unit
    }

def map_value(value: Any, args: Dict) -> Any:
    """Maps a value to another based on a provided dictionary."""
    mapping = args.get("map", {})
    return mapping.get(value, value)

def json_parse(value: str, args: Dict) -> Any:
    """Parses a JSON string into a Python object."""
    if not isinstance(value, str): return None
    try:
        return json.loads(value)
    except json.JSONDecodeError:
        return None

TRANSFORMER_REGISTRY = {
    "strip": strip,
    "normalize_whitespace": normalize_whitespace,
    "to_upper": to_upper,
    "to_lower": to_lower,
    "title_case": title_case,
    "only_digits": only_digits,
    "regex_sub": regex_sub,
    "parse_int": parse_int,
    "parse_decimal": parse_decimal,
    "parse_date": parse_date,
    "currency_normalize": currency_normalize,
    "unit_extract": unit_extract,
    "map_value": map_value,
    "json_parse": json_parse,
}