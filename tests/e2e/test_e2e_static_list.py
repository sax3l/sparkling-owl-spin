import pytest
from src.crawler.sitemap_generator import crawl_site
# Placeholder for http_scraper
async def scrape_url(url, template):
    return {"registration_number": "ABC123"}

@pytest.mark.e2e
@pytest.mark.asyncio
async def test_static_list_end_to_end(synthetic_hosts, test_config, redis_client):
    urls = crawl_site(f"{synthetic_hosts['static']}/list")
    detail_urls = [u for u in urls if "/item/" in u]
    assert len(detail_urls) >= 5
    rec = await scrape_url(detail_urls[0], template="vehicle_detail_v3")
    assert rec["registration_number"]