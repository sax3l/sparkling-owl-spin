import re
from typing import Any, Dict

def not_empty(value: Any, args: Dict) -> bool:
    return value is not None and value != ""

def length_range(value: str, args: Dict) -> bool:
    if not isinstance(value, str): return False
    return args.get("min", 0) <= len(value) <= args.get("max", float('inf'))

def regex(value: str, args: Dict) -> bool:
    pattern = args.get("pattern")
    return bool(re.match(pattern, value)) if isinstance(value, str) and pattern else False

def orgnr_sv(value: str, args: Dict) -> bool:
    # Basic format check, not checksum validation
    return regex(value, {"pattern": r"^\d{6}-?\d{4}$"})

def postal_code_sv(value: str, args: Dict) -> bool:
    return regex(value, {"pattern": r"^\d{5}$"})

VALIDATOR_REGISTRY = {
    "not_empty": not_empty,
    "length_range": length_range,
    "regex": regex,
    "orgnr_sv": orgnr_sv,
    "postal_code_sv": postal_code_sv,
}