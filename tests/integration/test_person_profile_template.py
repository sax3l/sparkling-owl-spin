import pytest
from src.scraper.template_runtime import extract_fields_from_html
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
    
    record = extract_fields_from_html(html, template)
    
    # Remove metadata for comparison
    record.pop("_extracted_at", None)
    record.pop("_template_id", None)
    record.pop("_template_version", None)
    
    assert record == expected_record