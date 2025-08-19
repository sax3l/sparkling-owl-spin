import pytest
import yaml
from src.scraper.template_runtime import extract_fields_from_html
from src.scraper.dsl.schema import ScrapingTemplate

@pytest.mark.integration
def test_template_runtime_golden_set(load_template, load_html, load_json):
    """
    Tests the new DSL runtime against a golden set of data.
    """
    template_data = load_template("vehicle_detail_v3")
    template = ScrapingTemplate.model_validate(template_data)
    html = load_html("vehicle_detail_example")
    expected_record = load_json("expected_vehicle_detail")
    
    record = extract_fields_from_html(html, template)
    
    # Remove metadata for comparison
    record.pop("_extracted_at", None)
    record.pop("_template_id", None)
    record.pop("_template_version", None)
    
    assert record == expected_record