import pytest
from src.scraper.template_runtime import run_template
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
    
    record, dq, lineage = run_template(html, template)

    # Convert Decimal to float/int for comparison
    if "tech_specs" in record and record["tech_specs"]:
        if "engine_power" in record["tech_specs"][0] and "value" in record["tech_specs"][0]["engine_power"]:
            record["tech_specs"][0]["engine_power"]["value"] = int(record["tech_specs"][0]["engine_power"]["value"])

    assert record == expected_record
    assert dq["dq_score"] == 1.0
    assert lineage["vin"]["raw"] == "YS3FB55E681234567"
    assert lineage["history"][0]["event_description"]["raw"] == "Besiktning"