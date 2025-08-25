import re
import json
from decimal import Decimal, InvalidOperation
from typing import Any, Dict, List

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

def regex_extract(text: str, config: dict = None) -> str:
    """Extract text using a regex pattern."""
    if not isinstance(text, str):
        return ""
    
    config = config or {}
    pattern = config.get("pattern", "")
    if not pattern:
        return text
    
    match = re.search(pattern, text)
    if match:
        # Return the first capturing group or the whole match
        result = match.group(1) if match.groups() else match.group(0)
        return result.strip()  # Strip to handle trailing spaces
    return ""


def to_decimal(text: str, config: dict = None) -> Decimal:
    """Convert text to decimal handling various number formats."""
    config = config or {}
    
    if isinstance(text, (Decimal, int, float)):
        return Decimal(str(text))
    
    if not isinstance(text, str):
        raise ValueError(f"Cannot convert {type(text)} to Decimal")
    
    # Clean the input
    cleaned = text.strip()
    
    # Handle European format (1.234,56) vs American format (1,234.56)
    # Check if we have both comma and dot
    if ',' in cleaned and '.' in cleaned:
        # Determine which is the decimal separator by position
        comma_pos = cleaned.rfind(',')
        dot_pos = cleaned.rfind('.')
        
        if comma_pos > dot_pos:
            # European format: 1.234,56
            cleaned = cleaned.replace('.', '').replace(',', '.')
        else:
            # American format: 1,234.56
            cleaned = cleaned.replace(',', '')
    elif ',' in cleaned:
        # Could be decimal separator (12,34) or thousands (1,234)
        parts = cleaned.split(',')
        if len(parts) == 2 and len(parts[1]) <= 3 and parts[1].isdigit():
            # Likely decimal separator
            cleaned = cleaned.replace(',', '.')
        elif len(parts) > 2 or (len(parts) == 2 and len(parts[1]) > 3):
            # Likely thousands separator
            cleaned = cleaned.replace(',', '')
    
    # Remove spaces and other non-numeric characters except dot and minus
    cleaned = re.sub(r'[^\d.-]', '', cleaned)
    
    if not cleaned or cleaned == '-':
        if text.strip() == '':
            return Decimal("0")
        raise ValueError(f"Cannot convert '{text}' to Decimal")
    
    try:
        return Decimal(cleaned)
    except (InvalidOperation, ValueError) as e:
        raise ValueError(f"Cannot convert '{text}' to Decimal") from e


def date_parse(text: str, config: dict = None) -> str:
    """Parse date from text."""
    # Placeholder implementation
    return text if isinstance(text, str) else ""


def map_values(text: str, config: dict = None) -> str:
    """Map values using a mapping dictionary."""
    config = config or {}
    mapping = config.get('mapping', {})
    return mapping.get(text, text)


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
    # Add missing functions
    "regex_extract": regex_extract,
    "to_decimal": to_decimal,
    "date_parse": date_parse,
    "map_values": map_values,
}


class FieldTransformer:
    """Field transformation pipeline for processing scraped data."""
    
    def __init__(self, transforms=None):
        self.transforms = transforms or []
    
    def apply(self, value: Any) -> Any:
        """Apply all transforms in order to the input value."""
        result = value
        for transform in self.transforms:
            if isinstance(transform, dict):
                transform_type = transform.get("type")
                if transform_type in TRANSFORMER_REGISTRY:
                    transformer_func = TRANSFORMER_REGISTRY[transform_type]
                    try:
                        result = transformer_func(result, transform)
                    except Exception as e:
                        # Log error but continue processing
                        print(f"Transform {transform_type} failed: {e}")
                        continue
            elif callable(transform):
                try:
                    result = transform(result)
                except Exception as e:
                    print(f"Transform function failed: {e}")
                    continue
        return result
    
    def add_transform(self, transform):
        """Add a transform to the pipeline."""
        self.transforms.append(transform)


class TransformationPipeline:
    """Pipeline for applying multiple field transformations."""
    
    def __init__(self):
        self.transformers = {}
    
    def add_field_transformer(self, field_name: str, transformer: FieldTransformer):
        """Add a transformer for a specific field."""
        self.transformers[field_name] = transformer
    
    def transform_data(self, data: dict) -> dict:
        """Apply all field transformers to input data."""
        result = data.copy()
        for field_name, transformer in self.transformers.items():
            if field_name in result:
                result[field_name] = transformer.apply(result[field_name])
        return result


def apply_transformation(value: Any, transform_config: Dict[str, Any]) -> Any:
    """Apply a single transformation to a value based on configuration."""
    transform_type = transform_config.get("type")
    if transform_type in TRANSFORMER_REGISTRY:
        transformer_func = TRANSFORMER_REGISTRY[transform_type]
        return transformer_func(value, transform_config)
    else:
        raise ValueError(f"Unknown transformation type: {transform_type}")


def apply_transformations(value: Any, transformations: List[Dict[str, Any]]) -> Any:
    """Apply a list of transformations to a value in order."""
    result = value
    for transform in transformations:
        result = apply_transformation(result, transform)
    return result