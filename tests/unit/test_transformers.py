import pytest
from decimal import Decimal
from src.scraper.dsl.transformers import strip, regex_extract, to_decimal, date_parse, map_values

@pytest.mark.unit
def test_strip():
    assert strip("  Hej  ", {}) == "Hej"

@pytest.mark.unit
@pytest.mark.parametrize("text,pattern,expected", [
    ("Pris: 12 345 kr", r"(\d[\d\s]+)", "12 345"),
    ("CO2: 132,5 g/km", r"(\d+[,\.\d]+)", "132,5"),
])
def test_regex_extract(text, pattern, expected):
    assert regex_extract(text, {"pattern": pattern}) == expected

@pytest.mark.unit
@pytest.mark.parametrize("raw,expected", [
    ("12,34", Decimal("12.34")),
    ("12.34", Decimal("12.34")),
    ("  1 234,50 ", Decimal("1234.50")),
])
def test_to_decimal(raw, expected):
    assert to_decimal(raw, {}) == expected

@pytest.mark.unit
def test_date_parse_stub():
    # This is a placeholder as date_parse is not fully implemented
    assert date_parse("2024-03-15", {}) == "2024-03-15"

@pytest.mark.unit
def test_map_values():
    assert map_values("Ja", {"map": {"Ja": True, "Nej": False}}) is True