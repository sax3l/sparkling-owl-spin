"""
Revolutionary Scraping System - Main Entry Point
Usage example and demonstration of world's most advanced scraping capabilities
"""

import asyncio
import logging
from revolutionary_scraper.core.revolutionary_system import (
    RevolutionaryScrapingSystem,
    ScrapingTask,
    create_revolutionary_config
)

async def main():
    """
    Main demonstration of revolutionary scraping capabilities
    """
    # Setup logging
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    logger = logging.getLogger(__name__)
    
    logger.info("🚀 Starting Revolutionary Scraping System Demonstration")
    
    # Create comprehensive configuration
    config = create_revolutionary_config()
    
    # Initialize the revolutionary system
    system = RevolutionaryScrapingSystem(config)
    
    try:
        # Initialize all components
        await system.initialize()
        
        # Create example scraping tasks
        tasks = [
            ScrapingTask(
                name="ecommerce_product_scrape",
                start_urls=[
                    "https://quotes.toscrape.com/",  # Safe test site
                    "https://books.toscrape.com/",   # Safe test site
                ],
                crawl_method="intelligent",
                max_pages=100,
                max_depth=3,
                target_patterns=["quote", "book", "product"],
                avoid_patterns=["login", "register"],
                stealth_level="maximum",
                proxy_rotation=False,  # Disabled for demo
                session_management=True,
                captcha_solving=False,  # Disabled for demo
                output_format="json",
                output_path="demo_results"
            ),
            ScrapingTask(
                name="news_article_scrape",
                start_urls=[
                    "https://httpbin.org/",  # Safe test site
                ],
                crawl_method="bfs",
                max_pages=50,
                max_depth=2,
                target_patterns=["article", "news", "story"],
                avoid_patterns=["advertisement", "popup"],
                stealth_level="advanced",
                proxy_rotation=False,
                session_management=True,
                captcha_solving=False,
                output_format="json",
                output_path="demo_results"
            )
        ]
        
        logger.info(f"📋 Created {len(tasks)} scraping tasks for demonstration")
        
        # Execute single task demonstration
        logger.info("🎯 Executing single task demonstration...")
        result = await system.execute_scraping_task(tasks[0])
        
        if result['success']:
            logger.info(f"✅ Single task completed successfully!")
            logger.info(f"   📊 Pages scraped: {result['pages_scraped']}")
            logger.info(f"   ⏱️ Execution time: {result['execution_time']:.2f}s")
            logger.info(f"   💾 Results saved to: {result['results_path']}")
        else:
            logger.error(f"❌ Single task failed: {result['error']}")
        
        # Get system status
        status = system.get_system_status()
        logger.info("📈 System Status:")
        logger.info(f"   🔄 Uptime: {status['uptime']:.1f}s")
        logger.info(f"   📊 Tasks completed: {status['system_stats']['tasks_completed']}")
        
        if 'session_status' in status:
            session_stats = status['session_status']
            logger.info(f"   🔗 Active sessions: {session_stats['active_sessions']}")
            logger.info(f"   ✅ Success rate: {session_stats['overall_success_rate']:.2%}")
        
        # Execute multiple tasks concurrently (commented out for demo)
        # logger.info("🚀 Executing multiple tasks concurrently...")
        # results = await system.run_continuous_scraping(tasks, concurrent_tasks=2)
        
        logger.info("🎉 Revolutionary Scraping System demonstration completed successfully!")
        
    except Exception as e:
        logger.error(f"💥 Demonstration failed: {e}")
    finally:
        # Graceful shutdown
        await system.shutdown()

if __name__ == "__main__":
    asyncio.run(main())
