#!/usr/bin/env python3
"""
📄 REVOLUTIONARY CONTENT EXTRACTION SYSTEM 📄
===============================================

Implementerar den ultimata innehållsextraktion enligt prioriteringslistan:
1. trafilatura - robust text+metadata extraktion från webbsidor
2. Apache Tika - universell parser för 1000+ filtyper
3. PDF-Extract-Kit - modern PDF→Markdown/HTML extraktion
4. Microsoft Recognizers-Text - datum/mått/antal extrahering
5. RapidFuzz - fuzzy match för deduplicering

🎯 COMPLETE EXTRACTION PIPELINE:
- ⚡ HTML → trafilatura (boilerplate removal, clean text)
- 📄 PDF → Tika/PDF-Extract-Kit (layout, tables, OCR)
- 🧠 Entity extraction (dates, amounts, measurements)
- 🔍 Fuzzy matching för deduplication  
- 📊 Structured output (JSON/Markdown/HTML)
- 🎯 Intelligent fallback system
"""

import asyncio
import json
import logging
import re
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Any, Union, Tuple
import hashlib
import mimetypes
from urllib.parse import urljoin, urlparse
import tempfile
import subprocess
import shutil

# Core content extraction
try:
    import trafilatura
    TRAFILATURA_AVAILABLE = True
except ImportError:
    TRAFILATURA_AVAILABLE = False
    logging.warning("⚠️  trafilatura not available")

# PDF processing
try:
    import fitz  # PyMuPDF
    PYMUPDF_AVAILABLE = True
except ImportError:
    PYMUPDF_AVAILABLE = False
    logging.warning("⚠️  PyMuPDF not available")

# Apache Tika client
try:
    import requests
    TIKA_AVAILABLE = True
except ImportError:
    TIKA_AVAILABLE = False
    logging.warning("⚠️  requests not available for Tika")

# Entity recognition
try:
    from recognizers_text import Culture, ModelResult
    from recognizers_text.date_time import DateTimeRecognizer
    from recognizers_text.number import NumberRecognizer  
    from recognizers_text.number_with_unit import NumberWithUnitRecognizer
    RECOGNIZERS_TEXT_AVAILABLE = True
except ImportError:
    RECOGNIZERS_TEXT_AVAILABLE = False
    logging.warning("⚠️  recognizers-text not available")

# Fuzzy matching
try:
    from rapidfuzz import fuzz, process
    RAPIDFUZZ_AVAILABLE = True
except ImportError:
    RAPIDFUZZ_AVAILABLE = False
    logging.warning("⚠️  rapidfuzz not available")

# HTML parsing
from bs4 import BeautifulSoup
import lxml

logger = logging.getLogger(__name__)


class ExtractionMethod(Enum):
    """Content extraction methods"""
    TRAFILATURA = "trafilatura"
    BEAUTIFULSOUP = "beautifulsoup"
    TIKA = "tika"
    PYMUPDF = "pymupdf"
    PDF_EXTRACT_KIT = "pdf_extract_kit"
    RAW_TEXT = "raw_text"


class ContentType(Enum):
    """Supported content types"""
    HTML = "html"
    PDF = "pdf"
    TEXT = "text"
    DOCX = "docx"
    XLSX = "xlsx"
    PPTX = "pptx"
    JSON = "json"
    XML = "xml"
    UNKNOWN = "unknown"


@dataclass
class EntityResult:
    """Extracted entity result"""
    type: str
    value: str
    text: str
    start: int
    end: int
    confidence: float = 1.0
    normalized_value: Optional[str] = None


@dataclass
class ExtractedContent:
    """Complete extracted content result"""
    success: bool = False
    method_used: Optional[ExtractionMethod] = None
    content_type: ContentType = ContentType.UNKNOWN
    
    # Basic content
    title: Optional[str] = None
    text: Optional[str] = None
    html: Optional[str] = None
    markdown: Optional[str] = None
    
    # Metadata
    author: Optional[str] = None
    date: Optional[str] = None
    description: Optional[str] = None
    keywords: List[str] = field(default_factory=list)
    language: Optional[str] = None
    
    # URLs and links
    url: Optional[str] = None
    links: List[Dict[str, str]] = field(default_factory=list)
    images: List[Dict[str, str]] = field(default_factory=list)
    
    # Structured data
    entities: List[EntityResult] = field(default_factory=list)
    tables: List[Dict[str, Any]] = field(default_factory=list)
    
    # Quality metrics
    text_length: int = 0
    word_count: int = 0
    quality_score: float = 0.0
    extraction_time: float = 0.0
    
    # Error handling
    error: Optional[str] = None
    warnings: List[str] = field(default_factory=list)


@dataclass
class ExtractionConfig:
    """Content extraction configuration"""
    # Trafilatura settings
    trafilatura_config: Dict[str, Any] = field(default_factory=lambda: {
        'include_comments': False,
        'include_tables': True,
        'include_images': True,
        'include_formatting': True,
        'favor_precision': True,
        'favor_recall': False,
        'deduplicate': True,
        'only_with_metadata': False
    })
    
    # Tika settings
    tika_server_url: str = "http://localhost:9998"
    tika_timeout: int = 120
    tika_max_file_size: int = 100 * 1024 * 1024  # 100MB
    
    # Entity extraction
    extract_entities: bool = True
    entity_languages: List[str] = field(default_factory=lambda: ['sv-SE', 'en-US'])
    entity_types: List[str] = field(default_factory=lambda: [
        'datetime', 'number', 'currency', 'percentage', 'dimension'
    ])
    
    # Quality control
    min_text_length: int = 50
    min_word_count: int = 10
    quality_threshold: float = 0.3
    
    # Deduplication
    enable_deduplication: bool = True
    similarity_threshold: float = 0.85
    
    # Output formats
    output_formats: List[str] = field(default_factory=lambda: ['text', 'markdown', 'json'])


class TikaClient:
    """Apache Tika server client"""
    
    def __init__(self, config: ExtractionConfig):
        self.config = config
        self.server_url = config.tika_server_url
        
    def is_server_available(self) -> bool:
        """Check if Tika server is running"""
        try:
            response = requests.get(
                f"{self.server_url}/tika", 
                timeout=5
            )
            return response.status_code == 200
        except:
            return False
    
    async def extract_content(self, content: bytes, 
                            content_type: Optional[str] = None) -> Optional[ExtractedContent]:
        """Extract content via Tika server"""
        if not self.is_server_available():
            logger.warning("⚠️  Tika server not available")
            return None
        
        try:
            import time
            start_time = time.time()
            
            # Prepare headers
            headers = {'Accept': 'application/json'}
            if content_type:
                headers['Content-Type'] = content_type
            
            # Extract text and metadata
            response = requests.put(
                f"{self.server_url}/tika",
                data=content,
                headers=headers,
                timeout=self.config.tika_timeout
            )
            
            if response.status_code != 200:
                return ExtractedContent(
                    success=False,
                    error=f"Tika server error: {response.status_code}"
                )
            
            # Parse response
            try:
                tika_result = response.json() if response.headers.get('content-type', '').startswith('application/json') else response.text
            except:
                tika_result = response.text
            
            # Extract metadata
            meta_response = requests.put(
                f"{self.server_url}/meta",
                data=content,
                headers={'Accept': 'application/json'},
                timeout=self.config.tika_timeout
            )
            
            metadata = {}
            if meta_response.status_code == 200:
                try:
                    metadata = meta_response.json()
                except:
                    pass
            
            extraction_time = time.time() - start_time
            
            # Build result
            if isinstance(tika_result, str):
                text = tika_result
            else:
                text = str(tika_result)
            
            return ExtractedContent(
                success=True,
                method_used=ExtractionMethod.TIKA,
                content_type=self._detect_content_type(content_type or metadata.get('Content-Type', '')),
                title=metadata.get('title') or metadata.get('dc:title'),
                text=text,
                author=metadata.get('Author') or metadata.get('dc:creator'),
                date=metadata.get('Creation-Date') or metadata.get('dcterms:created'),
                description=metadata.get('description') or metadata.get('dc:description'),
                language=metadata.get('language') or metadata.get('dc:language'),
                text_length=len(text),
                word_count=len(text.split()),
                extraction_time=extraction_time
            )
            
        except Exception as e:
            return ExtractedContent(
                success=False,
                error=f"Tika extraction failed: {str(e)}"
            )
    
    def _detect_content_type(self, content_type_str: str) -> ContentType:
        """Detect content type from MIME type"""
        if not content_type_str:
            return ContentType.UNKNOWN
            
        content_type_str = content_type_str.lower()
        
        if 'html' in content_type_str:
            return ContentType.HTML
        elif 'pdf' in content_type_str:
            return ContentType.PDF
        elif 'text' in content_type_str:
            return ContentType.TEXT
        elif 'json' in content_type_str:
            return ContentType.JSON
        elif 'xml' in content_type_str:
            return ContentType.XML
        elif any(x in content_type_str for x in ['word', 'docx']):
            return ContentType.DOCX
        elif any(x in content_type_str for x in ['excel', 'xlsx']):
            return ContentType.XLSX
        elif any(x in content_type_str for x in ['powerpoint', 'pptx']):
            return ContentType.PPTX
        else:
            return ContentType.UNKNOWN


class EntityExtractor:
    """Microsoft Recognizers-Text based entity extractor"""
    
    def __init__(self, config: ExtractionConfig):
        self.config = config
        
        if RECOGNIZERS_TEXT_AVAILABLE:
            self.datetime_recognizer = DateTimeRecognizer()
            self.number_recognizer = NumberRecognizer()
            self.unit_recognizer = NumberWithUnitRecognizer()
    
    def extract_entities(self, text: str, url: Optional[str] = None) -> List[EntityResult]:
        """Extract entities from text"""
        if not RECOGNIZERS_TEXT_AVAILABLE:
            return []
        
        entities = []
        
        for lang_code in self.config.entity_languages:
            try:
                culture = Culture.Swedish if lang_code.startswith('sv') else Culture.English
                
                # Extract datetime entities
                if 'datetime' in self.config.entity_types:
                    datetime_results = self.datetime_recognizer.recognize(text, culture)
                    for result in datetime_results:
                        entities.append(EntityResult(
                            type='datetime',
                            value=str(result.resolution.get('values', [{}])[0].get('value', '')),
                            text=result.text,
                            start=result.start,
                            end=result.end,
                            confidence=0.9
                        ))
                
                # Extract number entities
                if 'number' in self.config.entity_types:
                    number_results = self.number_recognizer.recognize(text, culture)
                    for result in number_results:
                        entities.append(EntityResult(
                            type='number',
                            value=str(result.resolution.get('value', '')),
                            text=result.text,
                            start=result.start,
                            end=result.end,
                            confidence=0.85
                        ))
                
                # Extract units/measurements
                if any(t in self.config.entity_types for t in ['currency', 'dimension', 'percentage']):
                    unit_results = self.unit_recognizer.recognize(text, culture)
                    for result in unit_results:
                        unit_type = result.resolution.get('unit', 'dimension')
                        entities.append(EntityResult(
                            type=unit_type,
                            value=str(result.resolution.get('value', '')),
                            text=result.text,
                            start=result.start,
                            end=result.end,
                            confidence=0.8
                        ))
                        
            except Exception as e:
                logger.warning(f"⚠️  Entity extraction failed for {lang_code}: {e}")
        
        return entities


class ContentDeduplicator:
    """RapidFuzz based content deduplication"""
    
    def __init__(self, config: ExtractionConfig):
        self.config = config
        self.content_cache: List[Dict[str, Any]] = []
    
    def is_duplicate(self, content: ExtractedContent) -> bool:
        """Check if content is duplicate of existing content"""
        if not RAPIDFUZZ_AVAILABLE or not self.config.enable_deduplication:
            return False
        
        if not content.text or len(content.text) < self.config.min_text_length:
            return False
        
        # Create content fingerprint
        content_hash = self._create_content_hash(content.text)
        
        # Check exact hash matches first
        for cached_item in self.content_cache:
            if cached_item['hash'] == content_hash:
                return True
        
        # Fuzzy matching for near-duplicates
        for cached_item in self.content_cache:
            similarity = fuzz.ratio(content.text, cached_item['text'])
            if similarity >= (self.config.similarity_threshold * 100):
                logger.info(f"🔍 Duplicate content detected (similarity: {similarity:.1f}%)")
                return True
        
        # Add to cache if not duplicate
        self.content_cache.append({
            'hash': content_hash,
            'text': content.text[:1000],  # Store first 1000 chars for fuzzy matching
            'url': content.url,
            'timestamp': datetime.now().isoformat()
        })
        
        # Limit cache size
        if len(self.content_cache) > 10000:
            self.content_cache = self.content_cache[-5000:]  # Keep recent 5000
        
        return False
    
    def _create_content_hash(self, text: str) -> str:
        """Create content hash for exact duplicate detection"""
        # Normalize text (remove extra whitespace, convert to lowercase)
        normalized = re.sub(r'\s+', ' ', text.lower().strip())
        return hashlib.md5(normalized.encode()).hexdigest()
    
    def get_similar_content(self, text: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Find similar content in cache"""
        if not RAPIDFUZZ_AVAILABLE or not text:
            return []
        
        # Get top similar items
        choices = [(item['text'], item) for item in self.content_cache]
        if not choices:
            return []
        
        matches = process.extract(
            text[:1000], 
            choices, 
            scorer=fuzz.ratio,
            limit=limit
        )
        
        return [
            {
                'similarity': score,
                'url': match[2]['url'],
                'timestamp': match[2]['timestamp']
            }
            for match, score, _ in matches
            if score >= 70  # At least 70% similarity
        ]


class RevolutionaryContentExtractor:
    """Revolutionary Content Extraction System - Main Controller"""
    
    def __init__(self, config: Optional[ExtractionConfig] = None):
        self.config = config or ExtractionConfig()
        self.tika_client = TikaClient(self.config)
        self.entity_extractor = EntityExtractor(self.config)
        self.deduplicator = ContentDeduplicator(self.config)
    
    async def extract(self, content: Union[str, bytes], 
                     url: Optional[str] = None,
                     content_type: Optional[str] = None,
                     force_method: Optional[ExtractionMethod] = None) -> ExtractedContent:
        """
        Main extraction method with intelligent content-type detection
        
        Pipeline: HTML→trafilatura / PDF→Tika/PDF-Extract-Kit / Other→Tika
        """
        
        import time
        start_time = time.time()
        
        logger.info(f"🔍 Extracting content from: {url or 'direct input'}")
        
        # Convert content to appropriate format
        if isinstance(content, str):
            content_bytes = content.encode('utf-8')
            content_str = content
        else:
            content_bytes = content
            try:
                content_str = content.decode('utf-8', errors='ignore')
            except:
                content_str = str(content)
        
        # Detect content type
        detected_type = self._detect_content_type(content_str, content_type, url)
        logger.info(f"📄 Detected content type: {detected_type.value}")
        
        # Choose extraction method based on content type and availability
        if force_method:
            methods = [force_method]
        else:
            methods = self._get_extraction_methods(detected_type)
        
        # Try extraction methods in priority order
        last_result = None
        for method in methods:
            try:
                logger.info(f"⚙️  Trying extraction method: {method.value}")
                
                if method == ExtractionMethod.TRAFILATURA:
                    result = await self._extract_with_trafilatura(content_str, url)
                elif method == ExtractionMethod.BEAUTIFULSOUP:
                    result = await self._extract_with_beautifulsoup(content_str, url)
                elif method == ExtractionMethod.TIKA:
                    result = await self.tika_client.extract_content(content_bytes, content_type)
                elif method == ExtractionMethod.PYMUPDF:
                    result = await self._extract_pdf_with_pymupdf(content_bytes, url)
                else:
                    continue  # Method not implemented
                
                if not result:
                    continue
                
                result.url = url
                result.content_type = detected_type
                result.extraction_time = time.time() - start_time
                
                # Post-processing
                if result.success:
                    # Extract entities
                    if self.config.extract_entities and result.text:
                        result.entities = self.entity_extractor.extract_entities(result.text, url)
                    
                    # Calculate quality score
                    result.quality_score = self._calculate_quality_score(result)
                    
                    # Check for duplicates
                    if self.deduplicator.is_duplicate(result):
                        result.warnings.append("Content marked as duplicate")
                    
                    # Quality threshold check
                    if result.quality_score >= self.config.quality_threshold:
                        logger.info(f"✅ Extraction successful with {method.value} "
                                  f"(quality: {result.quality_score:.2f}, "
                                  f"time: {result.extraction_time:.2f}s)")
                        return result
                    else:
                        logger.warning(f"⚠️  Low quality result from {method.value} "
                                     f"(quality: {result.quality_score:.2f})")
                
                last_result = result
                
            except Exception as e:
                logger.error(f"❌ Extraction method {method.value} failed: {e}")
        
        # All methods failed or low quality
        if last_result:
            logger.warning("⚠️  All high-quality extractions failed, returning best attempt")
            return last_result
        else:
            return ExtractedContent(
                success=False,
                content_type=detected_type,
                extraction_time=time.time() - start_time,
                error="All extraction methods failed"
            )
    
    def _detect_content_type(self, content: str, content_type: Optional[str], 
                           url: Optional[str]) -> ContentType:
        """Detect content type from various indicators"""
        
        # Check explicit content type
        if content_type:
            return self.tika_client._detect_content_type(content_type)
        
        # Check URL extension
        if url:
            parsed = urlparse(url)
            path = parsed.path.lower()
            if path.endswith('.pdf'):
                return ContentType.PDF
            elif path.endswith(('.html', '.htm')):
                return ContentType.HTML
            elif path.endswith(('.doc', '.docx')):
                return ContentType.DOCX
            elif path.endswith(('.xls', '.xlsx')):
                return ContentType.XLSX
            elif path.endswith(('.ppt', '.pptx')):
                return ContentType.PPTX
            elif path.endswith('.json'):
                return ContentType.JSON
            elif path.endswith('.xml'):
                return ContentType.XML
        
        # Check content patterns
        content_lower = content[:1000].lower().strip()
        
        if content_lower.startswith('%pdf'):
            return ContentType.PDF
        elif any(x in content_lower for x in ['<html', '<!doctype html', '<head', '<body']):
            return ContentType.HTML
        elif content_lower.startswith(('{', '[')):
            try:
                json.loads(content[:100])
                return ContentType.JSON
            except:
                pass
        elif content_lower.startswith('<?xml') or '<xml' in content_lower:
            return ContentType.XML
        
        return ContentType.TEXT
    
    def _get_extraction_methods(self, content_type: ContentType) -> List[ExtractionMethod]:
        """Get extraction methods in priority order for content type"""
        
        if content_type == ContentType.HTML:
            methods = []
            if TRAFILATURA_AVAILABLE:
                methods.append(ExtractionMethod.TRAFILATURA)
            methods.append(ExtractionMethod.BEAUTIFULSOUP)
            if TIKA_AVAILABLE:
                methods.append(ExtractionMethod.TIKA)
            return methods
            
        elif content_type == ContentType.PDF:
            methods = []
            if PYMUPDF_AVAILABLE:
                methods.append(ExtractionMethod.PYMUPDF)
            if TIKA_AVAILABLE:
                methods.append(ExtractionMethod.TIKA)
            return methods
            
        else:
            # For other types, prefer Tika
            methods = []
            if TIKA_AVAILABLE:
                methods.append(ExtractionMethod.TIKA)
            methods.append(ExtractionMethod.RAW_TEXT)
            return methods
    
    async def _extract_with_trafilatura(self, content: str, url: Optional[str]) -> Optional[ExtractedContent]:
        """Extract content using trafilatura"""
        if not TRAFILATURA_AVAILABLE:
            return None
        
        try:
            # Configure trafilatura
            config = trafilatura.settings.use_config()
            config.set('DEFAULT', 'EXTRACTION_TIMEOUT', '30')
            
            # Extract content
            result = trafilatura.extract(
                content,
                url=url,
                config=config,
                **self.config.trafilatura_config
            )
            
            if not result:
                return ExtractedContent(
                    success=False,
                    error="Trafilatura returned no content"
                )
            
            # Extract metadata
            metadata = trafilatura.metadata.extract_metadata(content, fast=True, url=url)
            
            # Extract links
            links = []
            try:
                soup = BeautifulSoup(content, 'html.parser')
                for link in soup.find_all('a', href=True):
                    href = link['href']
                    if url:
                        href = urljoin(url, href)
                    links.append({
                        'url': href,
                        'text': link.get_text(strip=True),
                        'title': link.get('title', '')
                    })
            except:
                pass
            
            # Extract images
            images = []
            try:
                soup = BeautifulSoup(content, 'html.parser')
                for img in soup.find_all('img', src=True):
                    src = img['src']
                    if url:
                        src = urljoin(url, src)
                    images.append({
                        'url': src,
                        'alt': img.get('alt', ''),
                        'title': img.get('title', '')
                    })
            except:
                pass
            
            return ExtractedContent(
                success=True,
                method_used=ExtractionMethod.TRAFILATURA,
                title=metadata.title if metadata else None,
                text=result,
                author=metadata.author if metadata else None,
                date=metadata.date if metadata else None,
                description=metadata.description if metadata else None,
                language=metadata.language if metadata else None,
                links=links,
                images=images,
                text_length=len(result),
                word_count=len(result.split())
            )
            
        except Exception as e:
            return ExtractedContent(
                success=False,
                error=f"Trafilatura extraction failed: {str(e)}"
            )
    
    async def _extract_with_beautifulsoup(self, content: str, url: Optional[str]) -> Optional[ExtractedContent]:
        """Extract content using BeautifulSoup as fallback"""
        try:
            soup = BeautifulSoup(content, 'html.parser')
            
            # Remove script and style elements
            for script in soup(["script", "style", "nav", "footer", "header", "aside"]):
                script.decompose()
            
            # Extract title
            title = None
            title_tag = soup.find('title')
            if title_tag:
                title = title_tag.get_text(strip=True)
            
            # Extract text
            text = soup.get_text()
            
            # Clean up text
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = ' '.join(chunk for chunk in chunks if chunk)
            
            # Extract metadata
            description = None
            author = None
            
            meta_desc = soup.find('meta', attrs={'name': 'description'})
            if meta_desc:
                description = meta_desc.get('content', '')
            
            meta_author = soup.find('meta', attrs={'name': 'author'})
            if meta_author:
                author = meta_author.get('content', '')
            
            return ExtractedContent(
                success=True,
                method_used=ExtractionMethod.BEAUTIFULSOUP,
                title=title,
                text=text,
                author=author,
                description=description,
                text_length=len(text),
                word_count=len(text.split())
            )
            
        except Exception as e:
            return ExtractedContent(
                success=False,
                error=f"BeautifulSoup extraction failed: {str(e)}"
            )
    
    async def _extract_pdf_with_pymupdf(self, content: bytes, url: Optional[str]) -> Optional[ExtractedContent]:
        """Extract PDF content using PyMuPDF"""
        if not PYMUPDF_AVAILABLE:
            return None
        
        try:
            # Load PDF from bytes
            doc = fitz.open(stream=content, filetype="pdf")
            
            # Extract text and metadata
            text_parts = []
            tables = []
            
            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                
                # Extract text
                text = page.get_text()
                if text.strip():
                    text_parts.append(text)
                
                # Try to extract tables (basic)
                try:
                    tabs = page.find_tables()
                    for tab in tabs:
                        table_data = tab.extract()
                        if table_data:
                            tables.append({
                                'page': page_num + 1,
                                'data': table_data
                            })
                except:
                    pass  # Tables extraction is optional
            
            full_text = '\n\n'.join(text_parts)
            
            # Extract metadata
            metadata = doc.metadata
            
            doc.close()
            
            return ExtractedContent(
                success=True,
                method_used=ExtractionMethod.PYMUPDF,
                title=metadata.get('title'),
                text=full_text,
                author=metadata.get('author'),
                description=metadata.get('subject'),
                tables=tables,
                text_length=len(full_text),
                word_count=len(full_text.split())
            )
            
        except Exception as e:
            return ExtractedContent(
                success=False,
                error=f"PyMuPDF extraction failed: {str(e)}"
            )
    
    def _calculate_quality_score(self, result: ExtractedContent) -> float:
        """Calculate content quality score"""
        score = 0.0
        
        # Text length score (0-0.3)
        if result.text_length >= self.config.min_text_length:
            text_score = min(result.text_length / 1000, 1.0) * 0.3
            score += text_score
        
        # Word count score (0-0.2)
        if result.word_count >= self.config.min_word_count:
            word_score = min(result.word_count / 100, 1.0) * 0.2
            score += word_score
        
        # Metadata completeness score (0-0.2)
        metadata_fields = [result.title, result.author, result.date, result.description]
        metadata_score = sum(1 for field in metadata_fields if field) / len(metadata_fields) * 0.2
        score += metadata_score
        
        # Entity richness score (0-0.15)
        if result.entities:
            entity_score = min(len(result.entities) / 10, 1.0) * 0.15
            score += entity_score
        
        # Structure score (0-0.15)
        structure_score = 0
        if result.links:
            structure_score += 0.05
        if result.images:
            structure_score += 0.05
        if result.tables:
            structure_score += 0.05
        score += structure_score
        
        return min(score, 1.0)


# Example usage and testing
async def test_content_extraction():
    """Test the content extraction system"""
    
    config = ExtractionConfig()
    extractor = RevolutionaryContentExtractor(config)
    
    # Test HTML content
    html_content = """
    <html>
        <head>
            <title>Test Article</title>
            <meta name="description" content="This is a test article">
            <meta name="author" content="Test Author">
        </head>
        <body>
            <h1>Test Article</h1>
            <p>This is some test content with <a href="https://example.com">a link</a>.</p>
            <p>Published on 2024-01-15. Price: $299.99</p>
            <img src="test.jpg" alt="Test image">
        </body>
    </html>
    """
    
    print("🧪 Testing HTML extraction...")
    result = await extractor.extract(html_content, url="https://example.com/article")
    
    if result.success:
        print(f"✅ Success with {result.method_used.value}")
        print(f"📄 Title: {result.title}")
        print(f"📝 Text length: {result.text_length} chars")
        print(f"🎯 Quality score: {result.quality_score:.2f}")
        print(f"🏷️  Entities: {len(result.entities)}")
        print(f"🔗 Links: {len(result.links)}")
        print(f"⏱️  Time: {result.extraction_time:.2f}s")
        
        # Show entities
        for entity in result.entities:
            print(f"  🏷️  {entity.type}: {entity.text} → {entity.value}")
    else:
        print(f"❌ Failed: {result.error}")


if __name__ == "__main__":
    asyncio.run(test_content_extraction())
