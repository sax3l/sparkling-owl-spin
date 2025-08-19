import yaml
import pytest
from src.scraper.dsl.schema import ScrapingTemplate as TemplateDefinition
from src.scraper.template_runtime import extract_fields_from_html, ValidationError

TEMPLATE = """
template_id: vehicle_detail_v1
version: 1.0.0
fields:
  - name: registration_number
    selector: "h1 span.reg"
    selector_type: css
    attr: text
    required: true
"""

HTML_OK = "<h1>Fordon <span class='reg'>ABC123</span></h1>"
HTML_DRIFT = "<h1>Fordon <span class='registration'>ABC123</span></h1>"

def test_drift_detects_selector_break():
    tpl = TemplateDefinition.model_validate(yaml.safe_load(TEMPLATE))
    # fungerar
    row = extract_fields_from_html(HTML_OK, tpl)
    assert row["registration_number"] == "ABC123"
    # driftscenario – selector faller ifrån → ValidationError pga required
    with pytest.raises(ValidationError):
        extract_fields_from_html(HTML_DRIFT, tpl)