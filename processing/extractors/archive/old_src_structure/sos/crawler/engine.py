import asyncio
import logging
from collections import deque
from urllib.parse import urlparse
from typing import Any, Callable
from .template_dsl import TemplateModel
from .robots import is_allowed
from .politeness import HostPoliteness
from .fetcher import Fetcher
from .extractors import extract_fields
from .utils import find_links
from ..core.config import get_settings
from ..db import crud
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)

class CrawlStats:
    def __init__(self):
        self.pages = 0
        self.items = 0

async def crawl_job(db: AsyncSession, job_id: int, template: TemplateModel, fetcher: Fetcher):
    """BFS crawl engine baserat på template DSL"""
    settings = get_settings()
    politeness = HostPoliteness(template.delay_ms or settings.CRAWL_DEFAULT_DELAY_MS)
    seen: set[str] = set()
    q = deque([(u, 0) for u in template.start_urls])  # (url, depth)
    stats = CrawlStats()

    try:
        await crud.update_job_status(db, job_id, status="running")
        
        while q and stats.pages < template.limits.max_pages:
            url, depth = q.popleft()
            
            if url in seen or depth > template.limits.max_depth:
                continue
                
            if template.respect_robots and not is_allowed(url):
                logger.info(f"Robots.txt disallowed: {url}")
                continue
                
            seen.add(url)
            
            try:
                # Politeness - wait between requests
                await politeness.wait_for_host(url)
                
                # Fetch page
                if template.render.enabled:
                    html = await fetcher.fetch_rendered(url, template.actions)
                else:
                    html = await fetcher.fetch_http(url)
                
                stats.pages += 1
                logger.info(f"Crawled [{stats.pages}]: {url}")
                
                # Extract data
                if template.extract:
                    data = extract_fields(html, template.extract)
                    if any(data.values()):  # Only save if we extracted something
                        await crud.add_result(db, job_id, url, data)
                        stats.items += 1
                
                # Find new links to follow
                if depth < template.limits.max_depth:
                    for rule in template.follow:
                        new_links = find_links(html, url, rule.selector)
                        for link in new_links:
                            if link not in seen:
                                q.append((link, depth + 1))
                
            except Exception as e:
                logger.error(f"Error crawling {url}: {e}")
                continue
        
        await crud.update_job_status(
            db, job_id, 
            status="done", 
            total_pages=stats.pages, 
            total_items=stats.items
        )
        logger.info(f"Job {job_id} completed: {stats.pages} pages, {stats.items} items")
        
    except Exception as e:
        logger.error(f"Job {job_id} failed: {e}")
        await crud.update_job_status(db, job_id, status="failed", error=str(e))
        raise
