import pytest
from src.scraper.dsl.schema import ScrapingTemplate

@pytest.mark.unit
def test_load_template_pydantic(load_template):
    template_data = load_template("vehicle_detail_v3")
    t = ScrapingTemplate.model_validate(template_data)
    assert t.id == "vehicle_detail_v3"
    assert any(f.name == "registration_number" for f in t.fields)