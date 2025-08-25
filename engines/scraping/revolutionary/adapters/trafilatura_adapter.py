#!/usr/bin/env python3
"""
Trafilatura Content Extraction Integration - Revolutionary Ultimate System v4.0
Advanced web content extraction and article parsing
"""

import asyncio
import logging
import time
import json
import re
from typing import Dict, Any, Optional, List, Union, Set
from dataclasses import dataclass, asdict
from urllib.parse import urljoin, urlparse
import xml.etree.ElementTree as ET

try:
    import trafilatura
    from trafilatura import extract, extract_metadata, bare_extraction
    from trafilatura.settings import use_config
    from trafilatura.core import extract_content
    import trafilatura.htmlprocessing as htmlprocessing
    import trafilatura.extraction as extraction
    TRAFILATURA_AVAILABLE = True
except ImportError:
    TRAFILATURA_AVAILABLE = False

logger = logging.getLogger(__name__)

@dataclass
class TrafilaturaConfig:
    """Configuration for Trafilatura content extraction"""
    enabled: bool = True
    include_comments: bool = False
    include_tables: bool = True
    include_images: bool = True
    include_links: bool = True
    include_formatting: bool = True
    favor_precision: bool = False
    favor_recall: bool = True
    deduplicate: bool = True
    target_language: Optional[str] = None
    min_text_length: int = 25
    min_output_size: int = 10
    max_output_size: int = 100000
    extract_metadata: bool = True
    extract_tei: bool = False
    extract_xml: bool = False
    prune_xpath: Optional[List[str]] = None
    only_with_metadata: bool = False
    debug: bool = False

@dataclass
class ExtractedContent:
    """Container for extracted content"""
    url: str
    title: Optional[str] = None
    author: Optional[str] = None
    date: Optional[str] = None
    description: Optional[str] = None
    sitename: Optional[str] = None
    hostname: Optional[str] = None
    language: Optional[str] = None
    text_content: Optional[str] = None
    raw_text: Optional[str] = None
    comments: Optional[str] = None
    tags: Optional[List[str]] = None
    categories: Optional[List[str]] = None
    links: Optional[List[Dict[str, str]]] = None
    images: Optional[List[Dict[str, str]]] = None
    tables: Optional[List[Dict[str, Any]]] = None
    metadata: Optional[Dict[str, Any]] = None
    extraction_time: Optional[float] = None
    word_count: Optional[int] = None
    character_count: Optional[int] = None
    reading_time: Optional[float] = None
    content_quality_score: Optional[float] = None

class TrafilaturaExtractor:
    """
    Trafilatura-based content extractor with advanced features.
    
    Features:
    - High-quality article text extraction
    - Metadata extraction (title, author, date, etc.)
    - Content deduplication
    - Language detection
    - Image and link extraction
    - Table extraction
    - Comment extraction
    - Content quality scoring
    """
    
    def __init__(self, config: TrafilaturaConfig):
        self.config = config
        self.trafilatura_config = None
        self._stats = {
            'extractions_total': 0,
            'extractions_successful': 0,
            'extractions_failed': 0,
            'total_processing_time': 0.0
        }
        
        if not TRAFILATURA_AVAILABLE:
            raise ImportError("trafilatura not available. Install with: pip install trafilatura")
            
        self._setup_trafilatura_config()
        
    def _setup_trafilatura_config(self):
        """Setup Trafilatura configuration"""
        
        # Create custom configuration
        self.trafilatura_config = use_config()
        
        # Configure extraction parameters
        self.trafilatura_config.set('DEFAULT', 'COMMENTS', str(self.config.include_comments).lower())
        self.trafilatura_config.set('DEFAULT', 'TABLES', str(self.config.include_tables).lower())
        self.trafilatura_config.set('DEFAULT', 'IMAGES', str(self.config.include_images).lower())
        self.trafilatura_config.set('DEFAULT', 'LINKS', str(self.config.include_links).lower())
        self.trafilatura_config.set('DEFAULT', 'FORMATTING', str(self.config.include_formatting).lower())
        self.trafilatura_config.set('DEFAULT', 'DEDUPLICATE', str(self.config.deduplicate).lower())
        
        # Content length settings
        self.trafilatura_config.set('DEFAULT', 'MIN_EXTRACTED_SIZE', str(self.config.min_output_size))
        self.trafilatura_config.set('DEFAULT', 'MIN_OUTPUT_SIZE', str(self.config.min_output_size))
        
        # Language settings
        if self.config.target_language:
            self.trafilatura_config.set('DEFAULT', 'TARGET_LANGUAGE', self.config.target_language)
            
        # Precision vs Recall
        if self.config.favor_precision:
            self.trafilatura_config.set('DEFAULT', 'FAVOR_PRECISION', 'True')
        elif self.config.favor_recall:
            self.trafilatura_config.set('DEFAULT', 'FAVOR_RECALL', 'True')
            
        logger.info("✅ Trafilatura configuration setup complete")
        
    async def extract_content(self, html_content: str, url: str,
                            custom_config: Optional[Dict[str, Any]] = None) -> ExtractedContent:
        """Extract content from HTML using Trafilatura"""
        
        start_time = time.time()
        self._stats['extractions_total'] += 1
        
        try:
            logger.info(f"📄 Extracting content from: {url}")
            
            # Use custom config if provided
            config = self.trafilatura_config
            if custom_config:
                # Create temporary config copy
                config = use_config()
                for section, options in custom_config.items():
                    for key, value in options.items():
                        config.set(section, key, str(value))
                        
            # Basic content extraction
            extracted_text = extract(
                html_content,
                url=url,
                config=config,
                include_comments=self.config.include_comments,
                include_tables=self.config.include_tables,
                include_images=self.config.include_images,
                include_links=self.config.include_links,
                include_formatting=self.config.include_formatting,
                favor_precision=self.config.favor_precision,
                favor_recall=self.config.favor_recall,
                prune_xpath=self.config.prune_xpath,
                only_with_metadata=self.config.only_with_metadata
            )
            
            # Extract metadata
            metadata = None
            if self.config.extract_metadata:
                metadata = extract_metadata(html_content, favor_precision=self.config.favor_precision)
                
            # Bare extraction for additional data
            bare_result = bare_extraction(
                html_content,
                url=url,
                favor_precision=self.config.favor_precision,
                favor_recall=self.config.favor_recall,
                include_comments=self.config.include_comments,
                include_tables=self.config.include_tables
            )
            
            # Process extracted content
            result = await self._process_extraction(
                extracted_text, metadata, bare_result, url, html_content
            )
            
            extraction_time = time.time() - start_time
            result.extraction_time = extraction_time
            
            self._stats['extractions_successful'] += 1
            self._stats['total_processing_time'] += extraction_time
            
            logger.info(f"✅ Content extracted: {url} ({extraction_time:.2f}s)")
            
            return result
            
        except Exception as e:
            self._stats['extractions_failed'] += 1
            logger.error(f"❌ Content extraction failed for {url}: {str(e)}")
            
            # Return minimal result on failure
            return ExtractedContent(
                url=url,
                extraction_time=time.time() - start_time
            )
            
    async def _process_extraction(self, extracted_text: Optional[str],
                                metadata: Optional[Dict[str, Any]],
                                bare_result: Optional[Dict[str, Any]],
                                url: str,
                                html_content: str) -> ExtractedContent:
        """Process and enhance extracted content"""
        
        result = ExtractedContent(url=url)
        
        # Basic text content
        result.text_content = extracted_text
        result.raw_text = bare_result.get('text') if bare_result else None
        
        # Metadata processing
        if metadata:
            result.title = metadata.get('title')
            result.author = metadata.get('author')
            result.date = metadata.get('date')
            result.description = metadata.get('description')
            result.sitename = metadata.get('sitename')
            result.hostname = metadata.get('hostname')
            result.language = metadata.get('language')
            result.tags = metadata.get('tags', [])
            result.categories = metadata.get('categories', [])
            result.metadata = metadata
            
        # Additional data from bare extraction
        if bare_result:
            if not result.title:
                result.title = bare_result.get('title')
            if not result.author:
                result.author = bare_result.get('author')
            if not result.date:
                result.date = bare_result.get('date')
                
            # Comments
            if self.config.include_comments:
                result.comments = bare_result.get('comments')
                
        # Extract links if enabled
        if self.config.include_links:
            result.links = await self._extract_links(html_content, url)
            
        # Extract images if enabled  
        if self.config.include_images:
            result.images = await self._extract_images(html_content, url)
            
        # Extract tables if enabled
        if self.config.include_tables:
            result.tables = await self._extract_tables(html_content)
            
        # Calculate metrics
        if result.text_content:
            result.word_count = len(result.text_content.split())
            result.character_count = len(result.text_content)
            # Estimate reading time (average 200 words per minute)
            result.reading_time = result.word_count / 200.0
            
        # Content quality score
        result.content_quality_score = await self._calculate_quality_score(result)
        
        return result
        
    async def _extract_links(self, html_content: str, base_url: str) -> List[Dict[str, str]]:
        """Extract and process links from HTML"""
        
        links = []
        
        try:
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(html_content, 'html.parser')
            
            for link in soup.find_all('a', href=True):
                href = link['href']
                text = link.get_text(strip=True)
                title = link.get('title', '')
                
                # Resolve relative URLs
                full_url = urljoin(base_url, href)
                
                # Filter out obvious non-content links
                if self._is_content_link(href, text):
                    links.append({
                        'url': full_url,
                        'text': text,
                        'title': title,
                        'type': self._classify_link_type(href, text)
                    })
                    
        except ImportError:
            # Fallback regex-based extraction
            import re
            link_pattern = r'<a\s+(?:[^>]*?\s+)?href=["\'](.*?)["\'][^>]*?>(.*?)</a>'
            
            for match in re.finditer(link_pattern, html_content, re.IGNORECASE | re.DOTALL):
                href, text = match.groups()
                full_url = urljoin(base_url, href)
                text = re.sub(r'<[^>]+>', '', text).strip()
                
                if self._is_content_link(href, text):
                    links.append({
                        'url': full_url,
                        'text': text,
                        'title': '',
                        'type': self._classify_link_type(href, text)
                    })
                    
        except Exception as e:
            logger.error(f"❌ Link extraction failed: {str(e)}")
            
        return links
        
    async def _extract_images(self, html_content: str, base_url: str) -> List[Dict[str, str]]:
        """Extract and process images from HTML"""
        
        images = []
        
        try:
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(html_content, 'html.parser')
            
            for img in soup.find_all('img', src=True):
                src = img['src']
                alt = img.get('alt', '')
                title = img.get('title', '')
                width = img.get('width', '')
                height = img.get('height', '')
                
                # Resolve relative URLs
                full_url = urljoin(base_url, src)
                
                # Filter out obvious non-content images
                if self._is_content_image(src, alt):
                    images.append({
                        'url': full_url,
                        'alt': alt,
                        'title': title,
                        'width': width,
                        'height': height,
                        'type': self._classify_image_type(src, alt)
                    })
                    
        except ImportError:
            # Fallback regex-based extraction
            import re
            img_pattern = r'<img\s+(?:[^>]*?\s+)?src=["\'](.*?)["\'][^>]*?/?>'
            
            for match in re.finditer(img_pattern, html_content, re.IGNORECASE):
                src = match.group(1)
                full_url = urljoin(base_url, src)
                
                if self._is_content_image(src, ''):
                    images.append({
                        'url': full_url,
                        'alt': '',
                        'title': '',
                        'width': '',
                        'height': '',
                        'type': self._classify_image_type(src, '')
                    })
                    
        except Exception as e:
            logger.error(f"❌ Image extraction failed: {str(e)}")
            
        return images
        
    async def _extract_tables(self, html_content: str) -> List[Dict[str, Any]]:
        """Extract and process tables from HTML"""
        
        tables = []
        
        try:
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(html_content, 'html.parser')
            
            for i, table in enumerate(soup.find_all('table')):
                table_data = {
                    'id': i,
                    'headers': [],
                    'rows': [],
                    'caption': '',
                    'summary': ''
                }
                
                # Extract caption
                caption = table.find('caption')
                if caption:
                    table_data['caption'] = caption.get_text(strip=True)
                    
                # Extract headers
                headers = table.find_all('th')
                if headers:
                    table_data['headers'] = [th.get_text(strip=True) for th in headers]
                    
                # Extract rows
                for row in table.find_all('tr'):
                    cells = row.find_all(['td', 'th'])
                    if cells:
                        row_data = [cell.get_text(strip=True) for cell in cells]
                        table_data['rows'].append(row_data)
                        
                # Generate summary
                if table_data['rows']:
                    table_data['summary'] = f"Table with {len(table_data['rows'])} rows"
                    if table_data['headers']:
                        table_data['summary'] += f" and {len(table_data['headers'])} columns"
                        
                tables.append(table_data)
                
        except Exception as e:
            logger.error(f"❌ Table extraction failed: {str(e)}")
            
        return tables
        
    def _is_content_link(self, href: str, text: str) -> bool:
        """Determine if a link is likely to contain content"""
        
        # Skip obvious non-content links
        skip_patterns = [
            r'^mailto:',
            r'^tel:',
            r'^javascript:',
            r'^#',
            r'\.css$',
            r'\.js$',
            r'\.pdf$',
            r'\.doc$',
            r'\.zip$',
            r'/admin',
            r'/login',
            r'/logout',
            r'/search',
            r'/contact'
        ]
        
        for pattern in skip_patterns:
            if re.search(pattern, href, re.IGNORECASE):
                return False
                
        # Skip if text is too short or common navigation text
        if len(text.strip()) < 3:
            return False
            
        nav_text = ['home', 'menu', 'back', 'next', 'prev', 'more', 'click here']
        if text.lower().strip() in nav_text:
            return False
            
        return True
        
    def _is_content_image(self, src: str, alt: str) -> bool:
        """Determine if an image is likely to be content-related"""
        
        # Skip obvious non-content images
        skip_patterns = [
            r'icon',
            r'logo',
            r'badge',
            r'button',
            r'arrow',
            r'spacer',
            r'tracking',
            r'analytics',
            r'1x1',
            r'\.gif$'
        ]
        
        src_lower = src.lower()
        alt_lower = alt.lower()
        
        for pattern in skip_patterns:
            if re.search(pattern, src_lower) or re.search(pattern, alt_lower):
                return False
                
        return True
        
    def _classify_link_type(self, href: str, text: str) -> str:
        """Classify link type"""
        
        if re.search(r'article|post|story|news', href, re.IGNORECASE):
            return 'article'
        elif re.search(r'category|tag|topic', href, re.IGNORECASE):
            return 'category'
        elif re.search(r'author|profile|about', href, re.IGNORECASE):
            return 'author'
        elif re.search(r'external|outbound', href, re.IGNORECASE):
            return 'external'
        else:
            return 'internal'
            
    def _classify_image_type(self, src: str, alt: str) -> str:
        """Classify image type"""
        
        if re.search(r'photo|picture|image', alt, re.IGNORECASE):
            return 'photo'
        elif re.search(r'chart|graph|diagram', alt, re.IGNORECASE):
            return 'chart'
        elif re.search(r'screenshot|capture', alt, re.IGNORECASE):
            return 'screenshot'
        else:
            return 'image'
            
    async def _calculate_quality_score(self, content: ExtractedContent) -> float:
        """Calculate content quality score (0.0 - 1.0)"""
        
        score = 0.0
        
        # Text content quality
        if content.text_content:
            text_len = len(content.text_content)
            if text_len >= 100:
                score += 0.3
            elif text_len >= 50:
                score += 0.15
                
        # Metadata completeness
        metadata_score = 0.0
        if content.title:
            metadata_score += 0.1
        if content.author:
            metadata_score += 0.05
        if content.date:
            metadata_score += 0.05
        if content.description:
            metadata_score += 0.05
            
        score += metadata_score
        
        # Content richness
        if content.links and len(content.links) > 0:
            score += 0.1
        if content.images and len(content.images) > 0:
            score += 0.1
        if content.tables and len(content.tables) > 0:
            score += 0.05
            
        # Reading time (optimal range)
        if content.reading_time:
            if 1.0 <= content.reading_time <= 10.0:
                score += 0.2
            elif content.reading_time <= 20.0:
                score += 0.1
                
        return min(1.0, score)
        
    async def extract_multiple(self, html_contents: List[Dict[str, str]],
                             max_concurrent: int = 5) -> List[ExtractedContent]:
        """Extract content from multiple HTML sources concurrently"""
        
        semaphore = asyncio.Semaphore(max_concurrent)
        
        async def extract_single(item):
            async with semaphore:
                return await self.extract_content(
                    item['html'], 
                    item['url']
                )
                
        tasks = [extract_single(item) for item in html_contents]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Filter out exceptions
        valid_results = []
        for result in results:
            if isinstance(result, ExtractedContent):
                valid_results.append(result)
            else:
                logger.error(f"❌ Extraction task failed: {str(result)}")
                
        return valid_results
        
    def get_stats(self) -> Dict[str, Any]:
        """Get extraction statistics"""
        success_rate = 0.0
        if self._stats['extractions_total'] > 0:
            success_rate = self._stats['extractions_successful'] / self._stats['extractions_total']
            
        avg_processing_time = 0.0
        if self._stats['extractions_successful'] > 0:
            avg_processing_time = self._stats['total_processing_time'] / self._stats['extractions_successful']
            
        return {
            **self._stats,
            'success_rate': success_rate,
            'average_processing_time': avg_processing_time,
            'config': asdict(self.config)
        }

class TrafilaturaAdapter:
    """High-level adapter for Trafilatura content extraction"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = TrafilaturaConfig(**config)
        self.extractor = TrafilaturaExtractor(self.config) if self.config.enabled else None
        
    async def initialize(self):
        """Initialize the adapter"""
        if not self.config.enabled:
            logger.info("Trafilatura adapter disabled")
            return
            
        if not TRAFILATURA_AVAILABLE:
            logger.error("❌ trafilatura not available")
            if self.config.enabled:
                raise ImportError("trafilatura package required")
            return
            
        logger.info("✅ Trafilatura adapter initialized")
        
    async def extract_article_content(self, html_content: str, url: str,
                                    custom_settings: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Extract article content from HTML.
        
        Returns:
        {
            'success': bool,
            'url': str,
            'title': str,
            'author': str,
            'date': str,
            'text_content': str,
            'metadata': dict,
            'links': list,
            'images': list,
            'tables': list,
            'word_count': int,
            'reading_time': float,
            'quality_score': float,
            'extraction_time': float
        }
        """
        
        if not self.config.enabled or not self.extractor:
            return {
                'success': False,
                'url': url,
                'error': 'Trafilatura is disabled or not available'
            }
            
        try:
            result = await self.extractor.extract_content(
                html_content, url, custom_config=custom_settings
            )
            
            return {
                'success': True,
                'url': result.url,
                'title': result.title,
                'author': result.author,
                'date': result.date,
                'description': result.description,
                'sitename': result.sitename,
                'language': result.language,
                'text_content': result.text_content,
                'raw_text': result.raw_text,
                'comments': result.comments,
                'tags': result.tags or [],
                'categories': result.categories or [],
                'metadata': result.metadata or {},
                'links': result.links or [],
                'images': result.images or [],
                'tables': result.tables or [],
                'word_count': result.word_count or 0,
                'character_count': result.character_count or 0,
                'reading_time': result.reading_time or 0.0,
                'quality_score': result.content_quality_score or 0.0,
                'extraction_time': result.extraction_time or 0.0,
                'method': 'trafilatura'
            }
            
        except Exception as e:
            logger.error(f"❌ Article extraction failed: {str(e)}")
            return {
                'success': False,
                'url': url,
                'error': str(e),
                'method': 'trafilatura'
            }
            
    async def extract_multiple_articles(self, html_sources: List[Dict[str, str]],
                                      max_concurrent: int = 5) -> List[Dict[str, Any]]:
        """Extract content from multiple articles concurrently"""
        
        if not self.config.enabled or not self.extractor:
            return [{
                'success': False,
                'url': item.get('url', ''),
                'error': 'Trafilatura is disabled'
            } for item in html_sources]
            
        try:
            results = await self.extractor.extract_multiple(html_sources, max_concurrent)
            
            # Convert to standardized format
            return [
                await self.extract_article_content(item['html'], item['url'])
                for item in html_sources
            ]
            
        except Exception as e:
            logger.error(f"❌ Multiple extraction failed: {str(e)}")
            return [{
                'success': False,
                'url': item.get('url', ''),
                'error': str(e)
            } for item in html_sources]
            
    async def get_stats(self) -> Dict[str, Any]:
        """Get adapter statistics"""
        base_stats = {
            'enabled': self.config.enabled,
            'config': asdict(self.config)
        }
        
        if self.extractor:
            base_stats['extractor_stats'] = self.extractor.get_stats()
        else:
            base_stats['extractor_stats'] = {}
            
        return base_stats

# Factory function
def create_trafilatura_adapter(config: Dict[str, Any]) -> TrafilaturaAdapter:
    """Create and configure Trafilatura adapter"""
    return TrafilaturaAdapter(config)

# Example usage
async def main():
    """Example usage"""
    config = {
        'enabled': True,
        'include_images': True,
        'include_links': True,
        'include_tables': True,
        'extract_metadata': True,
        'favor_recall': True,
        'debug': True
    }
    
    adapter = create_trafilatura_adapter(config)
    
    try:
        await adapter.initialize()
        
        # Test content extraction
        test_html = """
        <html>
        <head><title>Test Article</title></head>
        <body>
        <article>
        <h1>Test Article Title</h1>
        <p>This is a test article with some content.</p>
        <p>It contains multiple paragraphs to test extraction.</p>
        <a href="https://example.com">External link</a>
        <img src="test.jpg" alt="Test image">
        </article>
        </body>
        </html>
        """
        
        result = await adapter.extract_article_content(
            test_html, 
            'https://example.com/test'
        )
        
        if result['success']:
            print(f"✅ Success: {result['title']}")
            print(f"Text content: {result['text_content'][:100]}...")
            print(f"Quality score: {result['quality_score']}")
        else:
            print(f"❌ Failed: {result['error']}")
            
    finally:
        pass  # No cleanup needed

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
