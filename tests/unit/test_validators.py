import pytest
# Stubs for validators, assuming they will be created in src/utils/validators.py
def matches(value, pattern):
    import re
    return bool(re.match(pattern, value))

def in_range(value, min_val, max_val):
    return min_val <= value <= max_val

class CrossField:
    def __init__(self, rule): self.rule = rule
    def check(self, record):
        if "model_year" in record and record["model_year"]:
            return bool(record.get("make")) and bool(record.get("model"))
        return True

@pytest.mark.unit
def test_matches_regnr():
    assert matches("ABC123", r"^[A-ZÅÄÖ0-9-]{3,10}$")
    assert not matches("??", r"^[A-ZÅÄÖ0-9-]{3,10}$")

@pytest.mark.unit
def test_in_range_year():
    assert in_range(2022, 1900, 2035)
    assert not in_range(1500, 1900, 2035)

@pytest.mark.unit
def test_cross_field_rule():
    rule = CrossField("if model_year then make and model must exist")
    rec_ok  = {"model_year": 2020, "make": "Volvo", "model": "XC60"}
    rec_bad = {"model_year": 2020, "make": "", "model": None}
    assert rule.check(rec_ok)
    assert not rule.check(rec_bad)