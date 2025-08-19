import pytest
from src.scraper.template_runtime import extract_fields_from_html
from src.scraper.dsl.schema import ScrapingTemplate
from decimal import Decimal

@pytest.mark.integration
def test_vehicle_detail_template(load_template, load_html, load_json):
    """
    Validates the comprehensive vehicle_detail_v1 template against a
    sample HTML file and a golden JSON record.
    """
    template_data = load_template("vehicle_detail_v1")
    template = ScrapingTemplate.model_validate(template_data)
    html = load_html("vehicle_detail_page")
    expected_record = load_json("expected_vehicle_detail")
    
    record = extract_fields_from_html(html, template)

    # Remove metadata for comparison
    record.pop("_extracted_at", None)
    record.pop("_template_id", None)
    record.pop("_template_version", None)

    # The new runtime correctly returns lists for multi-fields, even if empty.
    # Adjusting expected data if it's missing empty lists.
    if "tech_specs" not in expected_record: expected_record["tech_specs"] = []
    if "ownership" not in expected_record: expected_record["ownership"] = []
    if "history" not in expected_record: expected_record["history"] = []

    assert record == expected_record