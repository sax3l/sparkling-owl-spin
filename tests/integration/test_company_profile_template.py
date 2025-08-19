import pytest
from src.scraper.template_runtime import run_template
from src.scraper.dsl.schema import ScrapingTemplate

@pytest.mark.integration
def test_company_profile_template(load_template, load_html, load_json):
    """
    Validates the comprehensive company_profile_v1 template against a
    sample HTML file and a golden JSON record.
    """
    template_data = load_template("company_profile_v1")
    template = ScrapingTemplate.model_validate(template_data)
    html = load_html("company_profile_example")
    expected_record = load_json("expected_company_profile")
    
    record, dq, lineage = run_template(html, template)

    # Convert Decimal to float for comparison
    for fin in record.get("financials", []):
        if "turnover" in fin:
            fin["turnover"] = float(fin["turnover"])

    assert record == expected_record
    assert dq["dq_score"] == 1.0
    assert lineage["name"]["raw"] == "MegaCorp AB"
    assert lineage["financials"][0]["year"]["raw"] == "2023"