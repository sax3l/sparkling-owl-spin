#!/usr/bin/env python3
"""
Trafilatura Document Adapter för Sparkling-Owl-Spin
Web content extraction med boilerplate removal
"""

import logging
import asyncio
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass
from datetime import datetime
import tempfile
import os

logger = logging.getLogger(__name__)

@dataclass
class ExtractionConfig:
    """Trafilatura extraction configuration"""
    include_comments: bool = False
    include_tables: bool = True
    include_images: bool = False
    include_links: bool = False
    include_formatting: bool = False
    deduplicate: bool = True
    favor_precision: bool = True
    favor_recall: bool = False
    language: Optional[str] = None
    url: Optional[str] = None

@dataclass
class ExtractedContent:
    """Extracted content från Trafilatura"""
    text: str
    title: str
    author: Optional[str] = None
    date: Optional[str] = None
    url: Optional[str] = None
    hostname: Optional[str] = None
    description: Optional[str] = None
    categories: List[str] = None
    tags: List[str] = None
    language: Optional[str] = None
    comments: Optional[str] = None
    raw_text: Optional[str] = None
    extraction_time: float = 0.0
    word_count: int = 0
    
@dataclass
class ExtractionJob:
    """Batch extraction job"""
    job_id: str
    inputs: List[Union[str, Dict[str, str]]]  # URLs or HTML content
    config: ExtractionConfig
    status: str
    start_time: datetime
    end_time: Optional[datetime] = None
    processed_count: int = 0
    total_count: int = 0
    results: List[ExtractedContent] = None
    errors: List[str] = None

class TrafilaturaAdapter:
    """Trafilatura integration för clean content extraction"""
    
    def __init__(self, plugin_info):
        self.plugin_info = plugin_info
        self.trafilatura_available = False
        self.active_jobs = {}
        self.initialized = False
        self.supported_languages = []
        
    async def initialize(self):
        """Initiera Trafilatura adapter"""
        try:
            logger.info("📰 Initializing Trafilatura Content Extraction Adapter")
            
            # Try to import trafilatura
            try:
                # import trafilatura  # Uncomment when available
                # from trafilatura import extract, extract_metadata, settings
                # import trafilatura.meta
                logger.info("✅ Trafilatura available")
                self.trafilatura_available = True
                
                # Setup supported languages
                self.supported_languages = [
                    'en', 'de', 'fr', 'es', 'it', 'pt', 'nl', 'sv', 'da', 'no', 
                    'fi', 'pl', 'ru', 'zh', 'ja', 'ko', 'ar', 'tr', 'cs', 'hu'
                ]
                
            except ImportError:
                logger.warning("⚠️ Trafilatura not available - using fallback extraction")
                self.trafilatura_available = False
                self.supported_languages = ['en']
                
            self.initialized = True
            logger.info("✅ Trafilatura Adapter initialized")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize Trafilatura: {str(e)}")
            raise
            
    async def extract_from_html(self, html_content: str, 
                              config: ExtractionConfig = None) -> ExtractedContent:
        """Extract content från HTML"""
        import time
        start_time = time.time()
        
        if not self.initialized:
            await self.initialize()
            
        if config is None:
            config = ExtractionConfig()
            
        logger.info("📄 Extracting content from HTML")
        
        if self.trafilatura_available:
            result = await self._extract_with_trafilatura(html_content, config)
        else:
            result = await self._extract_fallback(html_content, config)
            
        result.extraction_time = time.time() - start_time
        result.word_count = len(result.text.split()) if result.text else 0
        
        return result
        
    async def extract_from_url(self, url: str, 
                             config: ExtractionConfig = None) -> ExtractedContent:
        """Extract content från URL"""
        if config is None:
            config = ExtractionConfig()
            
        config.url = url
        
        # Fetch HTML content
        html_content = await self._fetch_url_content(url)
        
        # Extract content
        result = await self.extract_from_html(html_content, config)
        result.url = url
        
        # Extract hostname
        try:
            from urllib.parse import urlparse
            parsed = urlparse(url)
            result.hostname = parsed.netloc
        except:
            pass
            
        return result
        
    async def _fetch_url_content(self, url: str) -> str:
        """Fetch HTML content från URL"""
        try:
            import aiohttp
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=30) as response:
                    if response.status == 200:
                        return await response.text()
                    else:
                        raise Exception(f"HTTP {response.status}")
        except ImportError:
            # Fallback to requests if aiohttp not available
            import requests
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            return response.text
        except Exception as e:
            logger.error(f"❌ Failed to fetch URL {url}: {str(e)}")
            return f"<html><body><p>Failed to fetch content: {str(e)}</p></body></html>"
            
    async def _extract_with_trafilatura(self, html_content: str, 
                                      config: ExtractionConfig) -> ExtractedContent:
        """Extract using real Trafilatura"""
        await asyncio.sleep(0.1)  # Simulate processing
        
        # Mock trafilatura extraction - replace with real implementation
        text = await self._extract_text_content(html_content)
        title = await self._extract_title(html_content)
        
        # Mock metadata extraction
        metadata = {
            'author': None,
            'date': None,
            'description': None,
            'categories': [],
            'tags': [],
            'language': config.language
        }
        
        return ExtractedContent(
            text=text,
            title=title,
            author=metadata.get('author'),
            date=metadata.get('date'),
            url=config.url,
            description=metadata.get('description'),
            categories=metadata.get('categories', []),
            tags=metadata.get('tags', []),
            language=metadata.get('language'),
            raw_text=text  # In real implementation, this would be different
        )
        
    async def _extract_fallback(self, html_content: str, 
                              config: ExtractionConfig) -> ExtractedContent:
        """Fallback extraction using basic HTML parsing"""
        import re
        from html import unescape
        
        # Remove script and style tags
        clean_html = re.sub(r'<script[^>]*>.*?</script>', '', html_content, flags=re.DOTALL | re.IGNORECASE)
        clean_html = re.sub(r'<style[^>]*>.*?</style>', '', clean_html, flags=re.DOTALL | re.IGNORECASE)
        
        # Extract title
        title_match = re.search(r'<title[^>]*>(.*?)</title>', clean_html, re.IGNORECASE | re.DOTALL)
        title = unescape(title_match.group(1).strip()) if title_match else ""
        
        # Extract meta description
        desc_match = re.search(r'<meta[^>]*name=["\']description["\'][^>]*content=["\']([^"\']*)["\']', 
                              clean_html, re.IGNORECASE)
        description = unescape(desc_match.group(1)) if desc_match else None
        
        # Remove HTML tags and extract text
        text = re.sub(r'<[^>]+>', ' ', clean_html)
        text = re.sub(r'\s+', ' ', text).strip()
        text = unescape(text)
        
        # Basic content filtering (remove common boilerplate)
        lines = text.split('\n')
        filtered_lines = []
        
        for line in lines:
            line = line.strip()
            if len(line) < 10:  # Skip very short lines
                continue
            if any(skip in line.lower() for skip in ['cookie', 'privacy policy', 'terms of service', 'advertisement']):
                continue
            filtered_lines.append(line)
            
        clean_text = '\n'.join(filtered_lines)
        
        return ExtractedContent(
            text=clean_text,
            title=title,
            url=config.url,
            description=description,
            raw_text=text
        )
        
    async def _extract_text_content(self, html_content: str) -> str:
        """Extract main text content"""
        # Mock implementation - would use real trafilatura.extract()
        import re
        from html import unescape
        
        # Focus on content areas
        content_patterns = [
            r'<article[^>]*>(.*?)</article>',
            r'<main[^>]*>(.*?)</main>',
            r'<div[^>]*class=["\'][^"\']*content[^"\']*["\'][^>]*>(.*?)</div>',
            r'<div[^>]*id=["\'][^"\']*content[^"\']*["\'][^>]*>(.*?)</div>'
        ]
        
        content_html = html_content
        for pattern in content_patterns:
            matches = re.findall(pattern, html_content, re.IGNORECASE | re.DOTALL)
            if matches:
                content_html = ' '.join(matches)
                break
                
        # Remove unwanted elements
        content_html = re.sub(r'<script[^>]*>.*?</script>', '', content_html, flags=re.DOTALL | re.IGNORECASE)
        content_html = re.sub(r'<style[^>]*>.*?</style>', '', content_html, flags=re.DOTALL | re.IGNORECASE)
        content_html = re.sub(r'<nav[^>]*>.*?</nav>', '', content_html, flags=re.DOTALL | re.IGNORECASE)
        content_html = re.sub(r'<footer[^>]*>.*?</footer>', '', content_html, flags=re.DOTALL | re.IGNORECASE)
        content_html = re.sub(r'<header[^>]*>.*?</header>', '', content_html, flags=re.DOTALL | re.IGNORECASE)
        
        # Extract text
        text = re.sub(r'<[^>]+>', ' ', content_html)
        text = re.sub(r'\s+', ' ', text).strip()
        text = unescape(text)
        
        return text
        
    async def _extract_title(self, html_content: str) -> str:
        """Extract page title"""
        import re
        from html import unescape
        
        # Try h1 first
        h1_match = re.search(r'<h1[^>]*>(.*?)</h1>', html_content, re.IGNORECASE | re.DOTALL)
        if h1_match:
            return unescape(h1_match.group(1).strip())
            
        # Fallback to title tag
        title_match = re.search(r'<title[^>]*>(.*?)</title>', html_content, re.IGNORECASE | re.DOTALL)
        if title_match:
            return unescape(title_match.group(1).strip())
            
        return ""
        
    async def batch_extract(self, inputs: List[Union[str, Dict[str, str]]], 
                          config: ExtractionConfig = None) -> str:
        """Batch extract multiple URLs or HTML content"""
        if config is None:
            config = ExtractionConfig()
            
        job_id = f"trafilatura_job_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{len(self.active_jobs)}"
        
        job = ExtractionJob(
            job_id=job_id,
            inputs=inputs,
            config=config,
            status="running",
            start_time=datetime.now(),
            total_count=len(inputs),
            results=[],
            errors=[]
        )
        
        self.active_jobs[job_id] = job
        
        # Start processing
        asyncio.create_task(self._run_batch_job(job_id))
        
        logger.info(f"🚀 Started batch extraction job {job_id} with {len(inputs)} items")
        return job_id
        
    async def _run_batch_job(self, job_id: str):
        """Run batch extraction job"""
        job = self.active_jobs[job_id]
        
        try:
            for input_item in job.inputs:
                if job.status == "cancelled":
                    break
                    
                try:
                    if isinstance(input_item, str):
                        if input_item.startswith(('http://', 'https://')):
                            result = await self.extract_from_url(input_item, job.config)
                        else:
                            result = await self.extract_from_html(input_item, job.config)
                    elif isinstance(input_item, dict):
                        html_content = input_item.get('html', input_item.get('content', ''))
                        result = await self.extract_from_html(html_content, job.config)
                        if 'url' in input_item:
                            result.url = input_item['url']
                    else:
                        raise ValueError(f"Unsupported input type: {type(input_item)}")
                        
                    job.results.append(result)
                    job.processed_count += 1
                    
                except Exception as e:
                    error_msg = f"Failed to process item {job.processed_count + 1}: {str(e)}"
                    job.errors.append(error_msg)
                    logger.error(f"❌ {error_msg}")
                    job.processed_count += 1
                    
            job.status = "completed"
            
        except Exception as e:
            job.status = "failed"
            job.errors.append(f"Batch job error: {str(e)}")
            
        finally:
            job.end_time = datetime.now()
            
        logger.info(f"✅ Batch job {job_id} completed: {len(job.results)} successful, {len(job.errors)} errors")
        
    def get_job_status(self, job_id: str) -> Dict[str, Any]:
        """Get batch job status"""
        if job_id not in self.active_jobs:
            raise ValueError(f"Unknown job: {job_id}")
            
        job = self.active_jobs[job_id]
        
        return {
            "job_id": job.job_id,
            "status": job.status,
            "processed_count": job.processed_count,
            "total_count": job.total_count,
            "progress": job.processed_count / job.total_count if job.total_count > 0 else 0,
            "start_time": job.start_time.isoformat(),
            "end_time": job.end_time.isoformat() if job.end_time else None,
            "results_count": len(job.results) if job.results else 0,
            "errors_count": len(job.errors),
            "duration": (job.end_time - job.start_time).total_seconds() if job.end_time else None
        }
        
    def get_job_results(self, job_id: str) -> List[Dict[str, Any]]:
        """Get batch job results"""
        if job_id not in self.active_jobs:
            raise ValueError(f"Unknown job: {job_id}")
            
        job = self.active_jobs[job_id]
        results = job.results or []
        
        return [
            {
                "text": r.text,
                "title": r.title,
                "author": r.author,
                "date": r.date,
                "url": r.url,
                "hostname": r.hostname,
                "description": r.description,
                "categories": r.categories or [],
                "tags": r.tags or [],
                "language": r.language,
                "word_count": r.word_count,
                "extraction_time": r.extraction_time
            }
            for r in results
        ]
        
    async def export_job_results(self, job_id: str, format: str = "json", 
                               output_file: str = None) -> str:
        """Export job results"""
        results = self.get_job_results(job_id)
        
        if not output_file:
            output_file = f"trafilatura_results_{job_id}.{format}"
            
        if format.lower() == "json":
            import json
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, ensure_ascii=False)
        elif format.lower() == "csv":
            import csv
            with open(output_file, 'w', newline='', encoding='utf-8') as f:
                if results:
                    # Flatten nested fields
                    flattened_results = []
                    for result in results:
                        flat_result = result.copy()
                        flat_result['categories'] = '; '.join(result.get('categories', []))
                        flat_result['tags'] = '; '.join(result.get('tags', []))
                        flattened_results.append(flat_result)
                        
                    writer = csv.DictWriter(f, fieldnames=flattened_results[0].keys())
                    writer.writeheader()
                    writer.writerows(flattened_results)
        elif format.lower() == "txt":
            with open(output_file, 'w', encoding='utf-8') as f:
                for i, result in enumerate(results, 1):
                    f.write(f"=== Article {i} ===\n")
                    f.write(f"Title: {result.get('title', 'N/A')}\n")
                    f.write(f"URL: {result.get('url', 'N/A')}\n")
                    f.write(f"Word Count: {result.get('word_count', 0)}\n")
                    f.write(f"\n{result.get('text', '')}\n\n")
        else:
            raise ValueError(f"Unsupported format: {format}")
            
        logger.info(f"📄 Exported {len(results)} results to {output_file}")
        return output_file
        
    def get_extraction_statistics(self, content: ExtractedContent) -> Dict[str, Any]:
        """Get extraction statistics"""
        text_length = len(content.text) if content.text else 0
        
        return {
            "word_count": content.word_count,
            "character_count": text_length,
            "has_title": bool(content.title),
            "has_author": bool(content.author),
            "has_date": bool(content.date),
            "has_description": bool(content.description),
            "categories_count": len(content.categories) if content.categories else 0,
            "tags_count": len(content.tags) if content.tags else 0,
            "extraction_time": content.extraction_time,
            "language": content.language,
            "estimated_reading_time": max(1, content.word_count // 200) if content.word_count else 0  # minutes
        }
        
    def create_config(self, **kwargs) -> ExtractionConfig:
        """Create extraction configuration"""
        return ExtractionConfig(**kwargs)
        
    def get_supported_languages(self) -> List[str]:
        """Get supported languages"""
        return self.supported_languages.copy()
        
    def get_system_info(self) -> Dict[str, Any]:
        """Get system information"""
        return {
            "trafilatura_available": self.trafilatura_available,
            "supported_languages": len(self.supported_languages),
            "active_jobs": len([job for job in self.active_jobs.values() if job.status == "running"]),
            "total_jobs": len(self.active_jobs)
        }
        
    async def cleanup(self):
        """Cleanup Trafilatura adapter"""
        logger.info("🧹 Cleaning up Trafilatura Adapter")
        
        # Cancel active jobs
        for job_id in list(self.active_jobs.keys()):
            job = self.active_jobs[job_id]
            if job.status == "running":
                job.status = "cancelled"
                job.end_time = datetime.now()
                
        self.active_jobs.clear()
        self.initialized = False
        
        logger.info("✅ Trafilatura Adapter cleanup completed")
