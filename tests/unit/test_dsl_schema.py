import pytest
from src.scraper.dsl.schema import ScrapingTemplate

@pytest.mark.unit
def test_load_template_pydantic(load_template):
    template_data = load_template("vehicle_detail_v3")
    # Add missing fields for validation
    template_data['id'] = 'test-id'
    template_data['entity_type'] = 'vehicle'
    
    t = ScrapingTemplate.model_validate(template_data)
    assert t.id == "test-id"
    assert any(f.name == "registration_number" for f in t.fields)