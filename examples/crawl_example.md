# Basic Crawling Example

This example demonstrates how to perform basic crawling operations.

## Prerequisites

- Python 3.11+
- Scraping platform installed and running

## Basic Crawl

```python
from src.crawler import SitemapGenerator, LinkExtractor
from src.scraper import HTTPScraper

# Initialize components
sitemap_gen = SitemapGenerator()
link_extractor = LinkExtractor()
scraper = HTTPScraper()

# Generate sitemap
urls = sitemap_gen.generate_from_domain("example.com")

# Extract links
for url in urls:
    links = link_extractor.extract_links(url)
    print(f"Found {len(links)} links on {url}")
    
    # Scrape data
    for link in links:
        data = scraper.scrape(link)
        print(f"Scraped data: {data}")
```

## Configuration

Create a configuration file:

```yaml
crawler:
  max_depth: 3
  delay: 1.0
  respect_robots_txt: true
  
scraper:
  timeout: 30
  retries: 3
  user_agent: "MyBot/1.0"
```

## Running

```bash
python scripts/run_crawler.py --config config.yml --domain example.com
```
