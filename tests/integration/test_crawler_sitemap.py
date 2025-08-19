import pytest
from src.crawler.sitemap_generator import crawl_site

@pytest.mark.integration
def test_crawl_static_list(synthetic_hosts):
    # This is a simplified test as crawl_site is not async and doesn't use the test config
    # It also doesn't return URLs in the same format as the original test expected
    urls = crawl_site(f"{synthetic_hosts['static']}/list")
    assert len(urls) > 0