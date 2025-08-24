#!/usr/bin/env python3
"""
Advanced AI-Powered Scraping Integration
Combining ScrapeGraphAI with Ultimate Scraping System

This module integrates cutting-edge AI-powered scraping capabilities
with our existing high-performance scraping infrastructure.

Features:
- LLM-powered content understanding and extraction
- Graph-based scraping pipelines
- Multi-model AI support (OpenAI, Ollama, Anthropic)
- Intelligent data structuring and cleaning
- Swedish market-specific optimizations
"""

import asyncio
import json
import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Union, Any
import warnings

# Suppress warnings for cleaner output
warnings.filterwarnings("ignore", category=UserWarning)
warnings.filterwarnings("ignore", category=FutureWarning)

try:
    # ScrapeGraphAI imports
    from scrapegraphai.graphs import SmartScraperGraph, SearchGraph, OmniScraperGraph
    from scrapegraphai.models import OpenAI, Ollama, AzureOpenAI, Anthropic, Gemini
    SCRAPEGRAPH_AVAILABLE = True
    print("✅ ScrapeGraphAI successfully imported")
except ImportError as e:
    SCRAPEGRAPH_AVAILABLE = False
    print(f"⚠️  ScrapeGraphAI not available: {e}")

try:
    # Crawl4AI imports
    import crawl4ai
    from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig
    from crawl4ai.extraction_strategy import LLMExtractionStrategy, CosineStrategy
    from crawl4ai.chunking_strategy import RegexChunking, NlpSentenceChunking
    CRAWL4AI_AVAILABLE = True
    print("✅ Crawl4AI successfully imported")
except ImportError as e:
    CRAWL4AI_AVAILABLE = False
    print(f"⚠️  Crawl4AI not available: {e}")

# Standard imports
import requests
from bs4 import BeautifulSoup
import pandas as pd


class AdvancedAIScrapingSystem:
    """
    Next-generation AI-powered scraping system combining multiple AI frameworks
    with intelligent content understanding and Swedish market specialization.
    """
    
    def __init__(self, config: Optional[Dict] = None):
        """Initialize the advanced AI scraping system."""
        self.config = config or {}
        self.logger = self._setup_logging()
        
        # AI Model Configuration
        self.ai_models = {
            'openai': {
                'model': 'gpt-4',
                'api_key': self.config.get('openai_api_key', 'your-openai-key'),
                'temperature': 0.1
            },
            'ollama': {
                'model': 'llama3.2:8b',
                'base_url': 'http://localhost:11434',
                'temperature': 0.1
            },
            'anthropic': {
                'model': 'claude-3-haiku-20240307',
                'api_key': self.config.get('anthropic_api_key', 'your-anthropic-key'),
                'temperature': 0.1
            }
        }
        
        # Swedish Market Specialization
        self.swedish_prompts = {
            'company_info': """
            Extract Swedish company information including:
            - Företagsnamn (Company name)
            - Organisationsnummer (Organization number)  
            - Adress (Address)
            - Verksamhetsområde (Business area)
            - Kontaktinformation (Contact information)
            - VD/Företagsledning (CEO/Management)
            """,
            
            'financial_data': """
            Extract Swedish financial information:
            - Omsättning (Revenue)
            - Resultat (Profit/Loss)
            - Antal anställda (Number of employees)
            - Bransch (Industry sector)
            - Kreditbetyg (Credit rating)
            """,
            
            'market_analysis': """
            Analyze Swedish market data:
            - Marknadstrender (Market trends)
            - Konkurrentanalys (Competitor analysis)
            - Tillväxtmöjligheter (Growth opportunities)
            - Branschspecifik information (Industry-specific data)
            """
        }
        
        self.performance_metrics = {
            'total_extractions': 0,
            'successful_ai_extractions': 0,
            'failed_extractions': 0,
            'average_extraction_time': 0.0,
            'ai_model_usage': {},
            'swedish_content_detected': 0
        }
        
        print(f"🤖 Advanced AI Scraping System initialized")
        print(f"📊 ScrapeGraphAI Available: {SCRAPEGRAPH_AVAILABLE}")
        print(f"🕷️  Crawl4AI Available: {CRAWL4AI_AVAILABLE}")
    
    def _setup_logging(self) -> logging.Logger:
        """Set up comprehensive logging."""
        logger = logging.getLogger('AdvancedAIScraping')
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        
        return logger
    
    async def smart_extract_with_ai(
        self, 
        url: str, 
        prompt: str,
        ai_model: str = 'ollama',
        extraction_type: str = 'general'
    ) -> Dict[str, Any]:
        """
        Extract content using AI-powered understanding.
        
        Args:
            url: Target URL for extraction
            prompt: Natural language description of what to extract
            ai_model: AI model to use ('openai', 'ollama', 'anthropic')
            extraction_type: Type of extraction ('company', 'financial', 'market')
        
        Returns:
            Structured data extracted by AI
        """
        start_time = datetime.now()
        self.performance_metrics['total_extractions'] += 1
        
        try:
            # Use Swedish-specific prompts when applicable
            if extraction_type in self.swedish_prompts:
                prompt = f"{prompt}\n\n{self.swedish_prompts[extraction_type]}"
            
            result = await self._extract_with_scrapegraph(url, prompt, ai_model)
            
            if result:
                self.performance_metrics['successful_ai_extractions'] += 1
                self._update_model_usage(ai_model)
                
                # Detect Swedish content
                if self._is_swedish_content(str(result)):
                    self.performance_metrics['swedish_content_detected'] += 1
                
                extraction_time = (datetime.now() - start_time).total_seconds()
                self._update_average_time(extraction_time)
                
                return {
                    'success': True,
                    'data': result,
                    'extraction_time': extraction_time,
                    'ai_model': ai_model,
                    'swedish_content': self._is_swedish_content(str(result)),
                    'timestamp': datetime.now().isoformat()
                }
            else:
                raise Exception("AI extraction returned empty result")
                
        except Exception as e:
            self.performance_metrics['failed_extractions'] += 1
            self.logger.error(f"AI extraction failed for {url}: {e}")
            
            return {
                'success': False,
                'error': str(e),
                'extraction_time': (datetime.now() - start_time).total_seconds(),
                'ai_model': ai_model,
                'timestamp': datetime.now().isoformat()
            }
    
    async def _extract_with_scrapegraph(
        self, 
        url: str, 
        prompt: str, 
        ai_model: str
    ) -> Optional[Dict]:
        """Extract using ScrapeGraphAI."""
        if not SCRAPEGRAPH_AVAILABLE:
            raise Exception("ScrapeGraphAI not available")
        
        try:
            # Configure AI model
            model_config = self.ai_models.get(ai_model, self.ai_models['ollama'])
            
            graph_config = {
                "llm": {
                    "model": f"{ai_model}/{model_config['model']}",
                    "temperature": model_config['temperature']
                },
                "verbose": False,
                "headless": True,
                "browser_type": "chromium"
            }
            
            # Add API key for commercial models
            if ai_model in ['openai', 'anthropic']:
                graph_config["llm"]["api_key"] = model_config['api_key']
            elif ai_model == 'ollama':
                graph_config["llm"]["base_url"] = model_config['base_url']
            
            # Create smart scraper
            scraper = SmartScraperGraph(
                prompt=prompt,
                source=url,
                config=graph_config
            )
            
            # Execute extraction
            result = scraper.run()
            self.logger.info(f"ScrapeGraphAI extraction successful for {url}")
            
            return result
            
        except Exception as e:
            self.logger.error(f"ScrapeGraphAI extraction failed: {e}")
            return None
    
    async def advanced_crawl_with_ai(
        self, 
        urls: List[str],
        extraction_strategy: str = 'llm',
        concurrent_limit: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Advanced crawling with AI-powered content understanding.
        
        Args:
            urls: List of URLs to crawl
            extraction_strategy: Strategy for content extraction
            concurrent_limit: Maximum concurrent crawls
            
        Returns:
            List of extraction results
        """
        if not CRAWL4AI_AVAILABLE:
            self.logger.warning("Crawl4AI not available, falling back to basic extraction")
            return await self._fallback_crawl(urls)
        
        try:
            results = []
            
            # Configure browser for advanced crawling
            browser_config = BrowserConfig(
                browser_type="chromium",
                headless=True,
                verbose=False
            )
            
            # Configure crawler
            crawler_config = CrawlerRunConfig(
                word_count_threshold=50,
                extraction_strategy=LLMExtractionStrategy(
                    provider="ollama",
                    api_token=None,
                    instruction="Extract all relevant business and company information"
                ),
                chunking_strategy=NlpSentenceChunking(),
                bypass_cache=False
            )
            
            async with AsyncWebCrawler(config=browser_config) as crawler:
                # Process URLs concurrently
                semaphore = asyncio.Semaphore(concurrent_limit)
                tasks = [
                    self._crawl_single_url(crawler, url, crawler_config, semaphore)
                    for url in urls
                ]
                
                results = await asyncio.gather(*tasks, return_exceptions=True)
                
                # Filter and process results
                processed_results = []
                for i, result in enumerate(results):
                    if isinstance(result, Exception):
                        self.logger.error(f"Crawl failed for {urls[i]}: {result}")
                        processed_results.append({
                            'url': urls[i],
                            'success': False,
                            'error': str(result)
                        })
                    else:
                        processed_results.append(result)
                
                return processed_results
                
        except Exception as e:
            self.logger.error(f"Advanced crawling failed: {e}")
            return await self._fallback_crawl(urls)
    
    async def _crawl_single_url(
        self, 
        crawler, 
        url: str, 
        config, 
        semaphore: asyncio.Semaphore
    ) -> Dict[str, Any]:
        """Crawl a single URL with AI extraction."""
        async with semaphore:
            try:
                result = await crawler.arun(url=url, config=config)
                
                return {
                    'url': url,
                    'success': True,
                    'markdown': result.markdown,
                    'extracted_content': result.extracted_content,
                    'links': result.links,
                    'word_count': len(result.markdown.split()) if result.markdown else 0,
                    'swedish_content': self._is_swedish_content(result.markdown or ''),
                    'timestamp': datetime.now().isoformat()
                }
                
            except Exception as e:
                return {
                    'url': url,
                    'success': False,
                    'error': str(e),
                    'timestamp': datetime.now().isoformat()
                }
    
    async def _fallback_crawl(self, urls: List[str]) -> List[Dict[str, Any]]:
        """Fallback crawling method when advanced tools are unavailable."""
        results = []
        
        for url in urls:
            try:
                response = requests.get(url, timeout=10)
                response.raise_for_status()
                
                soup = BeautifulSoup(response.content, 'html.parser')
                text_content = soup.get_text(strip=True, separator=' ')
                
                results.append({
                    'url': url,
                    'success': True,
                    'content': text_content[:5000],  # Limit content length
                    'title': soup.title.string if soup.title else '',
                    'word_count': len(text_content.split()),
                    'swedish_content': self._is_swedish_content(text_content),
                    'timestamp': datetime.now().isoformat(),
                    'method': 'fallback'
                })
                
            except Exception as e:
                results.append({
                    'url': url,
                    'success': False,
                    'error': str(e),
                    'timestamp': datetime.now().isoformat(),
                    'method': 'fallback'
                })
        
        return results
    
    def _is_swedish_content(self, text: str) -> bool:
        """Detect Swedish content using keyword analysis."""
        swedish_keywords = [
            'och', 'att', 'det', 'som', 'för', 'på', 'med', 'av', 'är', 'till',
            'företag', 'bolag', 'aktie', 'omsättning', 'resultat', 'sverige',
            'svenska', 'kronor', 'sek', 'organisationsnummer', 'verksamhet'
        ]
        
        text_lower = text.lower()
        swedish_count = sum(1 for keyword in swedish_keywords if keyword in text_lower)
        
        return swedish_count >= 3  # Require at least 3 Swedish keywords
    
    def _update_model_usage(self, model: str) -> None:
        """Update AI model usage statistics."""
        if model not in self.performance_metrics['ai_model_usage']:
            self.performance_metrics['ai_model_usage'][model] = 0
        self.performance_metrics['ai_model_usage'][model] += 1
    
    def _update_average_time(self, new_time: float) -> None:
        """Update average extraction time."""
        total_successful = self.performance_metrics['successful_ai_extractions']
        current_avg = self.performance_metrics['average_extraction_time']
        
        # Calculate new average
        new_avg = ((current_avg * (total_successful - 1)) + new_time) / total_successful
        self.performance_metrics['average_extraction_time'] = new_avg
    
    def get_performance_report(self) -> Dict[str, Any]:
        """Generate comprehensive performance report."""
        total_extractions = self.performance_metrics['total_extractions']
        successful_extractions = self.performance_metrics['successful_ai_extractions']
        
        success_rate = (successful_extractions / total_extractions * 100) if total_extractions > 0 else 0
        
        return {
            'performance_summary': {
                'total_extractions': total_extractions,
                'successful_extractions': successful_extractions,
                'failed_extractions': self.performance_metrics['failed_extractions'],
                'success_rate_percent': round(success_rate, 2),
                'average_extraction_time_seconds': round(self.performance_metrics['average_extraction_time'], 3),
                'swedish_content_detected': self.performance_metrics['swedish_content_detected']
            },
            'ai_model_usage': self.performance_metrics['ai_model_usage'],
            'capabilities': {
                'scrapegraph_ai_available': SCRAPEGRAPH_AVAILABLE,
                'crawl4ai_available': CRAWL4AI_AVAILABLE,
                'swedish_optimization': True,
                'multi_model_support': True
            },
            'timestamp': datetime.now().isoformat()
        }
    
    async def save_extraction_results(
        self, 
        results: List[Dict], 
        filename: str = None
    ) -> str:
        """Save extraction results to file."""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"ai_extraction_results_{timestamp}.json"
        
        filepath = Path(filename)
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"Results saved to {filepath}")
            return str(filepath)
            
        except Exception as e:
            self.logger.error(f"Failed to save results: {e}")
            raise


async def test_advanced_ai_scraping():
    """Test the advanced AI scraping system."""
    print("🧪 TESTING ADVANCED AI SCRAPING SYSTEM")
    print("=" * 60)
    
    # Initialize system
    ai_scraper = AdvancedAIScrapingSystem()
    
    # Test URLs (Swedish companies)
    test_urls = [
        "https://www.volvo.com/sv-se/about-us/",
        "https://www.scania.com/se/sv/home.html",
        "https://www.ericsson.com/sv-se"
    ]
    
    # Test 1: AI-powered extraction
    print("🤖 Test 1: AI-Powered Content Extraction")
    print("-" * 40)
    
    for url in test_urls[:1]:  # Test one URL to avoid rate limits
        try:
            result = await ai_scraper.smart_extract_with_ai(
                url=url,
                prompt="Extract company information including name, business description, and key products",
                ai_model='ollama',
                extraction_type='company'
            )
            
            print(f"URL: {url}")
            print(f"Success: {result['success']}")
            if result['success']:
                print(f"AI Model: {result['ai_model']}")
                print(f"Extraction Time: {result['extraction_time']:.3f}s")
                print(f"Swedish Content: {result['swedish_content']}")
                print(f"Data Preview: {str(result['data'])[:200]}...")
            else:
                print(f"Error: {result['error']}")
            print()
            
        except Exception as e:
            print(f"Test failed for {url}: {e}")
    
    # Test 2: Advanced crawling (fallback)
    print("🕷️  Test 2: Advanced Crawling (Fallback Mode)")
    print("-" * 40)
    
    try:
        crawl_results = await ai_scraper.advanced_crawl_with_ai(
            urls=test_urls[:2],  # Test first two URLs
            concurrent_limit=2
        )
        
        for result in crawl_results:
            print(f"URL: {result['url']}")
            print(f"Success: {result['success']}")
            if result['success']:
                print(f"Word Count: {result.get('word_count', 'N/A')}")
                print(f"Swedish Content: {result.get('swedish_content', False)}")
                if 'content' in result:
                    print(f"Content Preview: {result['content'][:100]}...")
            else:
                print(f"Error: {result.get('error', 'Unknown error')}")
            print()
            
    except Exception as e:
        print(f"Advanced crawling test failed: {e}")
    
    # Test 3: Performance report
    print("📊 Test 3: Performance Report")
    print("-" * 40)
    
    performance_report = ai_scraper.get_performance_report()
    print(json.dumps(performance_report, indent=2))
    
    # Save results
    print("💾 Test 4: Save Results")
    print("-" * 40)
    
    all_results = []
    if 'result' in locals():
        all_results.append(result)
    if 'crawl_results' in locals():
        all_results.extend(crawl_results)
    
    if all_results:
        try:
            saved_file = await ai_scraper.save_extraction_results(all_results)
            print(f"✅ Results saved to: {saved_file}")
        except Exception as e:
            print(f"❌ Failed to save results: {e}")
    
    print("\n" + "=" * 60)
    print("🎉 ADVANCED AI SCRAPING TEST COMPLETED!")
    print("=" * 60)


if __name__ == "__main__":
    # Run the test
    asyncio.run(test_advanced_ai_scraping())
