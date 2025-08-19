import pytest
from src.scraper.template_runtime import run_template
from src.scraper.dsl.schema import ScrapingTemplate

@pytest.mark.integration
def test_person_profile_template(load_template, load_html, load_json):
    """
    Validates the comprehensive person_profile_v1 template against a
    sample HTML file and a golden JSON record.
    """
    template_data = load_template("person_profile_v1")
    template = ScrapingTemplate.model_validate(template_data)
    html = load_html("person_profile_example")
    expected_record = load_json("expected_person_profile")
    
    record, dq, lineage = run_template(html, template)
    
    assert record == expected_record
    assert dq["dq_score"] == 1.0
    assert lineage["first_name"]["selector"] == "h1.person .first"
    assert lineage["addresses"][0]["city"]["raw"] == "Ankeborg"