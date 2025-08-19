import pytest
# Placeholder for http_scraper
async def scrape_url(url, template):
    return {"registration_number": "ABC123"}

@pytest.mark.integration
@pytest.mark.asyncio
async def test_http_scraper_basic(synthetic_hosts):
    url = f"{synthetic_hosts['static']}/item/1"
    data = await scrape_url(url, template="vehicle_detail_v3")
    assert data["registration_number"]