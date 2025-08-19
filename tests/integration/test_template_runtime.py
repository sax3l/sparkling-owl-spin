import pytest
from src.scraper.template_runtime import run_template

@pytest.mark.integration
def test_template_runtime(load_template, load_html):
    tpl = load_template("vehicle_detail_v3")
    html = load_html("vehicle_detail_example")
    
    # This is a placeholder test as run_template is a stub
    record, dq = run_template(html, tpl)
    
    assert "title" in record
    assert dq["completeness"] > 0