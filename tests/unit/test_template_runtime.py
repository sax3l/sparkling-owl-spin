import pytest
from src.scraper.template_runtime import run_template

@pytest.mark.integration
def test_template_runtime(load_template, load_html, load_json):
    tpl = load_template("vehicle_detail_v3")
    html = load_html("vehicle_detail_example")
    record, dq = run_template(html, tpl)
    exp = load_json("expected_vehicle_detail")
    
    # Convert record values for comparison
    record['model_year'] = int(record['model_year'])
    record['co2_wltp'] = float(record['co2_wltp'])

    assert record["registration_number"] == exp["registration_number"]
    assert record["model_year"] == exp["model_year"]
    assert pytest.approx(record["co2_wltp"]) == exp["co2_wltp"]
    assert dq["completeness"] >= 0.9