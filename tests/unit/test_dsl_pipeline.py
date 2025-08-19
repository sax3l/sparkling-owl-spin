import pytest
import yaml
from src.scraper.dsl.schema import ScrapingTemplate as TemplateDefinition
from src.scraper.template_runtime import extract_fields_from_html, ValidationError

# This template defines a complex field that requires multiple steps to process correctly.
COMPLEX_FIELD_TEMPLATE = """
template_id: complex_field_v1
version: 1.0.0
fields:
  - name: co2_emission
    selector: "#data"
    selector_type: css
    attr: text
    required: true
    transforms:
      - type: regex_extract
        pattern: 'CO2-utsläpp: ([0-9,]+) g/km'
        group: 1
      - type: regex_sub
        pattern: ','
        repl: '.'
      - type: to_float
    validators:
      - type: numeric_range
        min: 50
        max: 500
"""

@pytest.mark.unit
def test_complex_transform_validation_pipeline():
    """
    Tests a full pipeline for a single field:
    1. Regex Extract: Pulls the numeric value from a string.
    2. Regex Sub: Replaces comma decimal separator with a period.
    3. To Float: Converts the string to a float.
    4. Numeric Range: Validates the final float value.
    """
    tpl = TemplateDefinition.model_validate(yaml.safe_load(COMPLEX_FIELD_TEMPLATE))
    
    # Case 1: Valid HTML
    html_ok = "<div id='data'>Fordonsdata. CO2-utsläpp: 148,5 g/km. Bränsle: Bensin.</div>"
    row = extract_fields_from_html(html_ok, tpl)
    assert row["co2_emission"] == 148.5

    # Case 2: Value out of range
    html_out_of_range = "<div id='data'>CO2-utsläpp: 25,0 g/km.</div>"
    with pytest.raises(ValidationError) as e:
        extract_fields_from_html(html_out_of_range, tpl)
    assert "value < 50" in str(e.value)

    # Case 3: Regex does not match
    html_no_match = "<div id='data'>Utsläppsdata saknas.</div>"
    with pytest.raises(ValidationError) as e:
        extract_fields_from_html(html_no_match, tpl)
    assert "required field missing" in str(e.value)