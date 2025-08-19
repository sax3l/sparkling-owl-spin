import time
import logging
from urllib.parse import urlparse
from src.crawler.url_frontier import URLFrontier
from src.crawler.robots_parser import RobotsParser
from src.crawler.link_extractor import extract_links
from src.crawler.template_detector import TemplateDetector
from src.anti_bot.policy_manager import PolicyManager
from src.scraper.transport import TransportManager

logger = logging.getLogger(__name__)

class Crawler:
    def __init__(
        self, 
        frontier: URLFrontier, 
        robots_parser: RobotsParser, 
        policy_manager: PolicyManager, 
        transport_manager: TransportManager,
        template_detector: TemplateDetector
    ):
        self.frontier = frontier
        self.robots_parser = robots_parser
        self.policy_manager = policy_manager
        self.transport_manager = transport_manager
        self.template_detector = template_detector

    def crawl_domain(self, start_url: str, max_urls: int = 1000):
        """
        Performs a crawl of a domain starting from a seed URL, respecting all policies.
        """
        self.frontier.clear()
        self.frontier.add_url(start_url)
        crawled_count = 0
        
        while crawled_count < max_urls:
            url_to_crawl = self.frontier.get_next_url()
            if not url_to_crawl:
                logger.info("Frontier is empty. Crawl finished.")
                break

            domain = urlparse(url_to_crawl).netloc
            policy = self.policy_manager.get_policy(domain)
            user_agent = "ECaDP/0.1 (Ethical Crawler; +http://example.com/bot)"

            if not self.robots_parser.can_fetch(url_to_crawl, user_agent):
                logger.info(f"Skipping {url_to_crawl} due to robots.txt")
                self.frontier.mark_as_visited(url_to_crawl)
                continue

            if time.time() < policy.backoff_until:
                logger.warning(f"Domain {domain} is in backoff. Re-queueing {url_to_crawl}")
                self.frontier.add_url(url_to_crawl)
                time.sleep(1) # Avoid a tight loop
                continue

            logger.info(f"Crawling: {url_to_crawl} with delay {policy.current_delay_seconds:.2f}s")
            time.sleep(policy.current_delay_seconds)

            html_content, status_code = self.transport_manager.fetch(url_to_crawl, policy)
            self.frontier.mark_as_visited(url_to_crawl)
            crawled_count += 1

            if status_code == 200:
                self.policy_manager.update_on_success(domain)
                
                template_type = self.template_detector.classify(url_to_crawl)
                logger.info(f"URL classified as template: {template_type or 'None'}")
                # TODO: Write to sitemap database layer here

                new_links = extract_links(url_to_crawl, html_content)
                for link in new_links:
                    # Only add links within the same domain for this simple crawler
                    if urlparse(link).netloc == domain:
                        self.frontier.add_url(link)
                logger.info(f"Found {len(new_links)} new links on {url_to_crawl}")
            else:
                self.policy_manager.update_on_failure(domain, status_code)
                logger.error(f"Failed to fetch {url_to_crawl} with status code {status_code}")