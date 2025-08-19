import pytest
from src.scraper.template_runtime import run_template
from src.scraper.dsl.schema import ScrapingTemplate

@pytest.mark.integration
def test_template_runtime_golden_set(load_template, load_html, load_json):
    """
    This is a selector regression test. It runs a 'golden' template against
    a 'golden' HTML file and asserts that the output matches the 'golden'
    expected data exactly. It also validates the lineage information.
    """
    template_data = load_template("vehicle_detail_v3")
    template = ScrapingTemplate.model_validate(template_data)
    html = load_html("vehicle_detail_example")
    expected_record = load_json("expected_vehicle_detail")
    
    record, dq, lineage = run_template(html, template)
    
    assert record == expected_record
    assert dq["completeness"] == 1.0
    assert dq["dq_score"] > 0.95
    
    # Assert on lineage
    assert lineage["registration_number"]["selector_used"] == "dd"
    assert lineage["registration_number"]["raw_value"] == "ABC123"
    assert lineage["model_year"]["selector_used"] == "[data-spec=modelYear]"