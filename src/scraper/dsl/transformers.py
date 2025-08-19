import re
from decimal import Decimal, InvalidOperation
from typing import Any, Dict

def strip(value: str, args: Dict) -> str:
    return value.strip() if isinstance(value, str) else value

def normalize_whitespace(value: str, args: Dict) -> str:
    return re.sub(r'\s+', ' ', value).strip() if isinstance(value, str) else value

def only_digits(value: str, args: Dict) -> str:
    return re.sub(r'\D', '', value) if isinstance(value, str) else ''

def parse_int(value: Any, args: Dict) -> int:
    if isinstance(value, int): return value
    if not isinstance(value, str): return 0
    cleaned = re.sub(r'[^\d-]', '', value.split(',')[0].split('.')[0])
    try: return int(cleaned)
    except (ValueError): return 0

def parse_decimal(value: Any, args: Dict) -> Decimal:
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
    # Placeholder for a robust implementation using dateutil.parser
    # from dateutil import parser
    # try: return parser.parse(value).isoformat()
    # except: return None
    return value

def to_upper(value: str, args: Dict) -> str:
    return value.upper() if isinstance(value, str) else value

def to_lower(value: str, args: Dict) -> str:
    return value.lower() if isinstance(value, str) else value

def title_case(value: str, args: Dict) -> str:
    return value.title() if isinstance(value, str) else value

def regex_sub(value: str, args: Dict) -> str:
    pattern = args.get("pattern")
    repl = args.get("repl", "")
    return re.sub(pattern, repl, value) if isinstance(value, str) and pattern else value

def map_value(value: Any, args: Dict) -> Any:
    mapping = args.get("map", {})
    return mapping.get(value, value)

TRANSFORMER_REGISTRY = {
    "strip": strip,
    "normalize_whitespace": normalize_whitespace,
    "only_digits": only_digits,
    "parse_int": parse_int,
    "parse_decimal": parse_decimal,
    "parse_date": parse_date,
    "to_upper": to_upper,
    "to_lower": to_lower,
    "title_case": title_case,
    "regex_sub": regex_sub,
    "map_value": map_value,
}