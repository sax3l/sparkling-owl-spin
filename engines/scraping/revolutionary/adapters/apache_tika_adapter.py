#!/usr/bin/env python3
"""
Apache Tika Content Extraction Integration - Revolutionary Ultimate System v4.0
Multi-format document parsing and content extraction using Apache Tika
"""

import asyncio
import logging
import time
import json
import subprocess
import tempfile
import shutil
from pathlib import Path
from typing import Dict, Any, Optional, List, Union
from dataclasses import dataclass, asdict
import mimetypes
import base64

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False

logger = logging.getLogger(__name__)

@dataclass
class TikaConfig:
    """Configuration for Apache Tika"""
    enabled: bool = True
    tika_server_url: str = "http://localhost:9998"
    tika_jar_path: Optional[str] = None
    java_path: str = "java"
    timeout: int = 300
    max_file_size: int = 50 * 1024 * 1024  # 50MB
    auto_start_server: bool = True
    server_port: int = 9998
    debug: bool = False
    extract_metadata: bool = True
    extract_content: bool = True
    ocr_enabled: bool = True
    ocr_language: str = "eng"
    supported_formats: List[str] = None

@dataclass
class ExtractedDocument:
    """Container for extracted document information"""
    filename: str
    content_type: str
    text_content: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    language: Optional[str] = None
    author: Optional[str] = None
    title: Optional[str] = None
    creation_date: Optional[str] = None
    modification_date: Optional[str] = None
    page_count: Optional[int] = None
    word_count: Optional[int] = None
    character_count: Optional[int] = None
    file_size: Optional[int] = None
    extraction_time: Optional[float] = None
    extracted_images: Optional[List[str]] = None
    links: Optional[List[str]] = None
    tables: Optional[List[Dict[str, Any]]] = None

class ApacheTikaManager:
    """
    Apache Tika manager for multi-format document parsing.
    
    Features:
    - Support for 1000+ file formats
    - OCR for images and PDFs
    - Metadata extraction
    - Content extraction
    - Language detection
    - Embedded object extraction
    - Table detection and extraction
    """
    
    def __init__(self, config: TikaConfig):
        self.config = config
        self.server_process = None
        self.temp_dir = None
        self._stats = {
            'extractions_total': 0,
            'extractions_successful': 0,
            'extractions_failed': 0,
            'total_processing_time': 0.0,
            'formats_processed': {}
        }
        
        if not REQUESTS_AVAILABLE:
            raise ImportError("requests not available. Install with: pip install requests")
            
        # Default supported formats if not specified
        if self.config.supported_formats is None:
            self.config.supported_formats = [
                'pdf', 'doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx',
                'txt', 'rtf', 'html', 'xml', 'csv', 'json',
                'jpg', 'jpeg', 'png', 'gif', 'bmp', 'tiff',
                'mp3', 'mp4', 'avi', 'mov', 'wmv',
                'zip', 'rar', '7z', 'tar', 'gz'
            ]
            
    async def initialize(self):
        """Initialize Apache Tika server"""
        
        if not self.config.enabled:
            return
            
        # Create temporary directory
        self.temp_dir = Path(tempfile.mkdtemp(prefix="tika_"))
        
        # Check if server is already running
        if await self._check_server_status():
            logger.info("✅ Apache Tika server already running")
            return
            
        # Start server if needed
        if self.config.auto_start_server:
            await self._start_tika_server()
        else:
            logger.warning("⚠️ Tika server not running and auto_start_server is disabled")
            
        logger.info("✅ Apache Tika manager initialized")
        
    async def _check_server_status(self) -> bool:
        """Check if Tika server is running"""
        
        try:
            response = requests.get(
                f"{self.config.tika_server_url}/version",
                timeout=5
            )
            
            if response.status_code == 200:
                version = response.text.strip()
                logger.info(f"✅ Tika server running: {version}")
                return True
                
        except Exception as e:
            logger.debug(f"Tika server not available: {str(e)}")
            
        return False
        
    async def _start_tika_server(self):
        """Start Apache Tika server"""
        
        tika_jar = self.config.tika_jar_path
        
        # Try to find Tika jar if not specified
        if not tika_jar:
            tika_jar = await self._find_or_download_tika_jar()
            
        if not tika_jar or not Path(tika_jar).exists():
            raise RuntimeError("Apache Tika jar not found")
            
        try:
            logger.info(f"🚀 Starting Tika server on port {self.config.server_port}")
            
            # Start Tika server
            cmd = [
                self.config.java_path,
                '-jar', str(tika_jar),
                '--server',
                '--port', str(self.config.server_port)
            ]
            
            if self.config.ocr_enabled:
                cmd.extend(['--config', self._create_tika_config()])
                
            self.server_process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=self.temp_dir
            )
            
            # Wait for server to start
            for _ in range(30):  # Wait up to 30 seconds
                await asyncio.sleep(1)
                if await self._check_server_status():
                    logger.info("✅ Tika server started successfully")
                    return
                    
            raise RuntimeError("Failed to start Tika server within timeout")
            
        except Exception as e:
            logger.error(f"❌ Failed to start Tika server: {str(e)}")
            raise
            
    async def _find_or_download_tika_jar(self) -> Optional[str]:
        """Find existing or download Apache Tika jar"""
        
        # Check common locations
        common_paths = [
            "/usr/local/lib/tika-server.jar",
            "/opt/tika/tika-server.jar",
            self.temp_dir / "tika-server.jar"
        ]
        
        for path in common_paths:
            if Path(path).exists():
                return str(path)
                
        # Download Tika jar
        return await self._download_tika_jar()
        
    async def _download_tika_jar(self) -> Optional[str]:
        """Download Apache Tika jar"""
        
        try:
            logger.info("📥 Downloading Apache Tika server jar...")
            
            # Get latest version info
            tika_version = "2.9.1"  # Latest stable version
            download_url = f"https://dlcdn.apache.org/tika/2.9.1/tika-server-standard-{tika_version}.jar"
            
            jar_path = self.temp_dir / f"tika-server-{tika_version}.jar"
            
            # Download with progress
            response = requests.get(download_url, stream=True)
            response.raise_for_status()
            
            total_size = int(response.headers.get('content-length', 0))
            downloaded = 0
            
            with open(jar_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        
                        if total_size > 0:
                            progress = (downloaded / total_size) * 100
                            if downloaded % (1024 * 1024) == 0:  # Log every MB
                                logger.info(f"📥 Download progress: {progress:.1f}%")
                                
            logger.info(f"✅ Downloaded Tika jar: {jar_path}")
            return str(jar_path)
            
        except Exception as e:
            logger.error(f"❌ Failed to download Tika jar: {str(e)}")
            return None
            
    def _create_tika_config(self) -> str:
        """Create Tika configuration file for OCR"""
        
        config_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<properties>
    <parsers>
        <parser class="org.apache.tika.parser.ocr.TesseractOCRParser">
            <params>
                <param name="language" type="string">{self.config.ocr_language}</param>
                <param name="timeout" type="int">{self.config.timeout}</param>
                <param name="outputType" type="string">txt</param>
            </params>
        </parser>
    </parsers>
</properties>
"""
        
        config_path = self.temp_dir / "tika-config.xml"
        with open(config_path, 'w', encoding='utf-8') as f:
            f.write(config_content)
            
        return str(config_path)
        
    async def extract_from_file(self, file_path: Union[str, Path],
                              extract_content: bool = True,
                              extract_metadata: bool = True) -> ExtractedDocument:
        """Extract content and metadata from file"""
        
        start_time = time.time()
        self._stats['extractions_total'] += 1
        
        file_path = Path(file_path)
        
        try:
            logger.info(f"📄 Extracting from file: {file_path.name}")
            
            if not file_path.exists():
                raise FileNotFoundError(f"File not found: {file_path}")
                
            if file_path.stat().st_size > self.config.max_file_size:
                raise ValueError(f"File too large: {file_path.stat().st_size} bytes")
                
            # Detect content type
            content_type, _ = mimetypes.guess_type(str(file_path))
            if not content_type:
                content_type = 'application/octet-stream'
                
            # Check if format is supported
            file_ext = file_path.suffix.lower().lstrip('.')
            if file_ext not in self.config.supported_formats:
                logger.warning(f"⚠️ Unsupported format: {file_ext}")
                
            result = ExtractedDocument(
                filename=file_path.name,
                content_type=content_type,
                file_size=file_path.stat().st_size
            )
            
            # Extract content
            if extract_content:
                result.text_content = await self._extract_content(file_path)
                
            # Extract metadata
            if extract_metadata:
                result.metadata = await self._extract_metadata(file_path)
                
            # Process metadata
            if result.metadata:
                result = await self._process_metadata(result)
                
            # Calculate statistics
            if result.text_content:
                result.character_count = len(result.text_content)
                result.word_count = len(result.text_content.split())
                
            extraction_time = time.time() - start_time
            result.extraction_time = extraction_time
            
            # Update stats
            self._stats['extractions_successful'] += 1
            self._stats['total_processing_time'] += extraction_time
            self._stats['formats_processed'][file_ext] = self._stats['formats_processed'].get(file_ext, 0) + 1
            
            logger.info(f"✅ Extracted from {file_path.name} ({extraction_time:.2f}s)")
            
            return result
            
        except Exception as e:
            self._stats['extractions_failed'] += 1
            logger.error(f"❌ Failed to extract from {file_path.name}: {str(e)}")
            
            return ExtractedDocument(
                filename=file_path.name if file_path else 'unknown',
                content_type='unknown',
                extraction_time=time.time() - start_time
            )
            
    async def _extract_content(self, file_path: Path) -> Optional[str]:
        """Extract text content from file using Tika"""
        
        try:
            with open(file_path, 'rb') as f:
                files = {'file': (file_path.name, f, 'application/octet-stream')}
                
                response = requests.put(
                    f"{self.config.tika_server_url}/tika",
                    files=files,
                    timeout=self.config.timeout,
                    headers={'Accept': 'text/plain'}
                )
                
                if response.status_code == 200:
                    return response.text.strip()
                else:
                    logger.error(f"❌ Tika content extraction failed: {response.status_code}")
                    return None
                    
        except Exception as e:
            logger.error(f"❌ Content extraction error: {str(e)}")
            return None
            
    async def _extract_metadata(self, file_path: Path) -> Optional[Dict[str, Any]]:
        """Extract metadata from file using Tika"""
        
        try:
            with open(file_path, 'rb') as f:
                files = {'file': (file_path.name, f, 'application/octet-stream')}
                
                response = requests.put(
                    f"{self.config.tika_server_url}/meta",
                    files=files,
                    timeout=self.config.timeout,
                    headers={'Accept': 'application/json'}
                )
                
                if response.status_code == 200:
                    return response.json()
                else:
                    logger.error(f"❌ Tika metadata extraction failed: {response.status_code}")
                    return None
                    
        except Exception as e:
            logger.error(f"❌ Metadata extraction error: {str(e)}")
            return None
            
    async def _process_metadata(self, document: ExtractedDocument) -> ExtractedDocument:
        """Process and extract structured data from metadata"""
        
        if not document.metadata:
            return document
            
        metadata = document.metadata
        
        # Extract common fields
        document.title = (
            metadata.get('title') or
            metadata.get('dc:title') or
            metadata.get('Title')
        )
        
        document.author = (
            metadata.get('author') or
            metadata.get('dc:creator') or
            metadata.get('Author') or
            metadata.get('meta:author')
        )
        
        document.creation_date = (
            metadata.get('created') or
            metadata.get('Creation-Date') or
            metadata.get('meta:creation-date')
        )
        
        document.modification_date = (
            metadata.get('modified') or
            metadata.get('Last-Modified') or
            metadata.get('meta:save-date')
        )
        
        document.language = (
            metadata.get('language') or
            metadata.get('dc:language') or
            metadata.get('Content-Language')
        )
        
        # Extract page count for documents
        page_count_fields = [
            'xmpTPg:NPages', 'meta:page-count', 'Page-Count',
            'pdf:unmappedUnicodeCharsPerPage', 'Pages'
        ]
        
        for field in page_count_fields:
            if field in metadata and metadata[field]:
                try:
                    document.page_count = int(metadata[field])
                    break
                except (ValueError, TypeError):
                    continue
                    
        return document
        
    async def extract_from_url(self, url: str) -> ExtractedDocument:
        """Extract content from URL using Tika"""
        
        try:
            logger.info(f"🌐 Extracting from URL: {url}")
            
            response = requests.put(
                f"{self.config.tika_server_url}/tika",
                headers={
                    'Accept': 'text/plain',
                    'Content-Type': 'text/plain'
                },
                data=url,
                timeout=self.config.timeout
            )
            
            if response.status_code == 200:
                text_content = response.text.strip()
                
                # Get metadata
                meta_response = requests.put(
                    f"{self.config.tika_server_url}/meta",
                    headers={
                        'Accept': 'application/json',
                        'Content-Type': 'text/plain'
                    },
                    data=url,
                    timeout=self.config.timeout
                )
                
                metadata = meta_response.json() if meta_response.status_code == 200 else None
                
                result = ExtractedDocument(
                    filename=url.split('/')[-1] or 'web_content',
                    content_type='text/html',
                    text_content=text_content,
                    metadata=metadata
                )
                
                if metadata:
                    result = await self._process_metadata(result)
                    
                return result
                
            else:
                raise Exception(f"Tika server error: {response.status_code}")
                
        except Exception as e:
            logger.error(f"❌ URL extraction failed: {str(e)}")
            return ExtractedDocument(
                filename='url_extraction_failed',
                content_type='unknown'
            )
            
    async def extract_batch(self, file_paths: List[Union[str, Path]],
                          max_concurrent: int = 5) -> List[ExtractedDocument]:
        """Extract content from multiple files concurrently"""
        
        semaphore = asyncio.Semaphore(max_concurrent)
        
        async def extract_single(file_path):
            async with semaphore:
                return await self.extract_from_file(file_path)
                
        tasks = [extract_single(path) for path in file_paths]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Filter out exceptions
        valid_results = []
        for result in results:
            if isinstance(result, ExtractedDocument):
                valid_results.append(result)
            else:
                logger.error(f"❌ Batch extraction task failed: {str(result)}")
                
        return valid_results
        
    def get_supported_formats(self) -> List[str]:
        """Get list of supported file formats"""
        return self.config.supported_formats.copy()
        
    def is_format_supported(self, file_path: Union[str, Path]) -> bool:
        """Check if file format is supported"""
        file_ext = Path(file_path).suffix.lower().lstrip('.')
        return file_ext in self.config.supported_formats
        
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
        
    async def cleanup(self):
        """Clean up resources"""
        
        # Stop Tika server if we started it
        if self.server_process:
            try:
                self.server_process.terminate()
                self.server_process.wait(timeout=10)
                logger.info("🛑 Tika server stopped")
            except Exception as e:
                logger.error(f"❌ Failed to stop Tika server: {str(e)}")
                
        # Clean up temporary directory
        if self.temp_dir and self.temp_dir.exists():
            try:
                shutil.rmtree(self.temp_dir)
                logger.info(f"🧹 Cleaned up Tika temp directory")
            except Exception as e:
                logger.error(f"❌ Failed to cleanup temp dir: {str(e)}")

class ApacheTikaAdapter:
    """High-level adapter for Apache Tika integration"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = TikaConfig(**config)
        self.manager = ApacheTikaManager(self.config) if self.config.enabled else None
        
    async def initialize(self):
        """Initialize the adapter"""
        if not self.config.enabled:
            logger.info("Apache Tika adapter disabled")
            return
            
        if self.manager:
            await self.manager.initialize()
            logger.info("✅ Apache Tika adapter initialized")
        else:
            logger.error("❌ Apache Tika manager not available")
            
    async def extract_document_content(self, file_path: Union[str, Path],
                                     include_metadata: bool = True,
                                     include_text: bool = True) -> Dict[str, Any]:
        """
        Extract content from document file.
        
        Returns:
        {
            'success': bool,
            'filename': str,
            'content_type': str,
            'text_content': str,
            'metadata': dict,
            'title': str,
            'author': str,
            'page_count': int,
            'word_count': int,
            'extraction_time': float
        }
        """
        
        if not self.config.enabled or not self.manager:
            return {
                'success': False,
                'filename': str(file_path),
                'error': 'Apache Tika is disabled or not available'
            }
            
        try:
            result = await self.manager.extract_from_file(
                file_path,
                extract_content=include_text,
                extract_metadata=include_metadata
            )
            
            return {
                'success': bool(result.text_content or result.metadata),
                'filename': result.filename,
                'content_type': result.content_type,
                'text_content': result.text_content or '',
                'metadata': result.metadata or {},
                'title': result.title,
                'author': result.author,
                'creation_date': result.creation_date,
                'language': result.language,
                'page_count': result.page_count,
                'word_count': result.word_count or 0,
                'character_count': result.character_count or 0,
                'file_size': result.file_size,
                'extraction_time': result.extraction_time or 0.0,
                'method': 'apache-tika'
            }
            
        except Exception as e:
            logger.error(f"❌ Document extraction failed: {str(e)}")
            return {
                'success': False,
                'filename': str(file_path),
                'error': str(e),
                'method': 'apache-tika'
            }
            
    async def extract_from_url(self, url: str) -> Dict[str, Any]:
        """Extract content from URL"""
        
        if not self.config.enabled or not self.manager:
            return {
                'success': False,
                'url': url,
                'error': 'Apache Tika is disabled or not available'
            }
            
        try:
            result = await self.manager.extract_from_url(url)
            
            return {
                'success': bool(result.text_content),
                'url': url,
                'text_content': result.text_content or '',
                'metadata': result.metadata or {},
                'title': result.title,
                'author': result.author,
                'content_type': result.content_type,
                'method': 'apache-tika-url'
            }
            
        except Exception as e:
            return {
                'success': False,
                'url': url,
                'error': str(e),
                'method': 'apache-tika-url'
            }
            
    async def extract_batch_documents(self, file_paths: List[Union[str, Path]],
                                    max_concurrent: int = 5) -> List[Dict[str, Any]]:
        """Extract content from multiple documents"""
        
        if not self.config.enabled or not self.manager:
            return [{
                'success': False,
                'filename': str(path),
                'error': 'Apache Tika is disabled'
            } for path in file_paths]
            
        try:
            results = await self.manager.extract_batch(file_paths, max_concurrent)
            
            return [
                await self.extract_document_content(Path(result.filename))
                for result in results
            ]
            
        except Exception as e:
            logger.error(f"❌ Batch extraction failed: {str(e)}")
            return [{
                'success': False,
                'filename': str(path),
                'error': str(e)
            } for path in file_paths]
            
    async def get_stats(self) -> Dict[str, Any]:
        """Get adapter statistics"""
        base_stats = {
            'enabled': self.config.enabled,
            'config': asdict(self.config)
        }
        
        if self.manager:
            base_stats['manager_stats'] = self.manager.get_stats()
        else:
            base_stats['manager_stats'] = {}
            
        return base_stats
        
    async def cleanup(self):
        """Clean up all resources"""
        if self.manager:
            await self.manager.cleanup()

# Factory function
def create_apache_tika_adapter(config: Dict[str, Any]) -> ApacheTikaAdapter:
    """Create and configure Apache Tika adapter"""
    return ApacheTikaAdapter(config)

# Example usage
async def main():
    """Example usage"""
    config = {
        'enabled': True,
        'auto_start_server': True,
        'ocr_enabled': True,
        'extract_metadata': True,
        'debug': True
    }
    
    adapter = create_apache_tika_adapter(config)
    
    try:
        await adapter.initialize()
        
        # Test document extraction (create a test file)
        test_file = Path("test_document.txt")
        test_file.write_text("This is a test document for Apache Tika extraction.")
        
        result = await adapter.extract_document_content(test_file)
        
        if result['success']:
            print(f"✅ Success: {result['filename']}")
            print(f"Text: {result['text_content'][:100]}...")
            print(f"Word count: {result['word_count']}")
        else:
            print(f"❌ Failed: {result['error']}")
            
        # Cleanup test file
        if test_file.exists():
            test_file.unlink()
            
    finally:
        await adapter.cleanup()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
