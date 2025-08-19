import pytest
import yaml
from src.scraper.template_runtime import run_template
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
    
    record, dq, lineage = run_template(html, template)
    
    assert record == expected_record
    assert dq["dq_score"] == 1.0
    
    # Assert on lineage
    assert lineage["registration_number"]["selector"] == "dd"
    assert lineage["registration_number"]["raw"] == "ABC123"
    assert lineage["model_year"]["selector"] == "[data-spec=modelYear]"