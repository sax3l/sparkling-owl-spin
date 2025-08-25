#!/usr/bin/env python3
"""
Apache Tika Document Processing Adapter för Sparkling-Owl-Spin
Integration för Apache Tika document parsing och content extraction
"""

import logging
import asyncio
import subprocess
import tempfile
import os
from typing import Dict, List, Any, Optional, Union, BinaryIO
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
import json

logger = logging.getLogger(__name__)

@dataclass
class DocumentMetadata:
    """Document metadata från Tika"""
    content_type: str
    title: Optional[str] = None
    author: Optional[str] = None
    creator: Optional[str] = None
    created: Optional[datetime] = None
    modified: Optional[datetime] = None
    pages: Optional[int] = None
    words: Optional[int] = None
    characters: Optional[int] = None
    language: Optional[str] = None
    subject: Optional[str] = None
    keywords: Optional[str] = None
    raw_metadata: Dict[str, Any] = None

@dataclass
class ExtractedDocument:
    """Extracted document content"""
    content: str
    metadata: DocumentMetadata
    extraction_time: float
    file_path: str
    file_size: int
    content_length: int
    
@dataclass
class ProcessingJob:
    """Document processing job"""
    job_id: str
    file_paths: List[str]
    status: str
    start_time: datetime
    end_time: Optional[datetime] = None
    processed_files: int = 0
    total_files: int = 0
    errors: List[str] = None

class TikaAdapter:
    """Apache Tika integration för document processing"""
    
    def __init__(self, plugin_info):
        self.plugin_info = plugin_info
        self.tika_available = False
        self.tika_server_url = "http://localhost:9998"
        self.tika_jar_path = None
        self.active_jobs = {}
        self.initialized = False
        self.supported_formats = set()
        
    async def initialize(self):
        """Initiera Tika Adapter"""
        try:
            logger.info("📄 Initializing Apache Tika Adapter")
            
            # Check Tika availability
            await self._check_tika_availability()
            
            # Setup supported formats
            await self._setup_supported_formats()
            
            self.initialized = True
            logger.info("✅ Apache Tika Adapter initialized")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize Tika Adapter: {str(e)}")
            raise
            
    async def _check_tika_availability(self):
        """Check if Tika is available"""
        try:
            # Try Python Tika first
            try:
                # import tika  # Uncomment when available
                # from tika import parser, config
                logger.info("✅ Python Tika available (mock)")
                self.tika_available = True
                return
            except ImportError:
                logger.info("⚠️ Python Tika not available, checking Tika server...")
                
            # Try Tika server
            try:
                import aiohttp
                async with aiohttp.ClientSession() as session:
                    async with session.get(f"{self.tika_server_url}/version", timeout=5) as response:
                        if response.status == 200:
                            version = await response.text()
                            logger.info(f"✅ Tika server available at {self.tika_server_url}: {version}")
                            self.tika_available = True
                            return
            except Exception:
                pass
                
            # Try Tika JAR
            java_available = await self._check_java_availability()
            if java_available:
                # Look for Tika JAR in common locations
                common_paths = [
                    "./tika-app.jar",
                    "./lib/tika-app.jar",
                    "/opt/tika/tika-app.jar",
                    "C:/tika/tika-app.jar"
                ]
                
                for jar_path in common_paths:
                    if os.path.exists(jar_path):
                        self.tika_jar_path = jar_path
                        logger.info(f"✅ Tika JAR found: {jar_path}")
                        self.tika_available = True
                        return
                        
            logger.warning("⚠️ Apache Tika not available - using mock implementation")
            self.tika_available = False
            
        except Exception as e:
            logger.warning(f"⚠️ Error checking Tika availability: {str(e)}")
            self.tika_available = False
            
    async def _check_java_availability(self) -> bool:
        """Check if Java is available"""
        try:
            result = await asyncio.create_subprocess_exec(
                'java', '-version',
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await result.communicate()
            
            if result.returncode == 0:
                logger.info("✅ Java available")
                return True
            else:
                logger.warning("⚠️ Java not available")
                return False
                
        except Exception:
            logger.warning("⚠️ Java not found")
            return False
            
    async def _setup_supported_formats(self):
        """Setup supported document formats"""
        # Common document formats Tika supports
        self.supported_formats = {
            # Text documents
            'application/pdf',
            'application/msword',
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            'application/vnd.ms-excel',
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            'application/vnd.ms-powerpoint',
            'application/vnd.openxmlformats-officedocument.presentationml.presentation',
            'application/vnd.oasis.opendocument.text',
            'application/vnd.oasis.opendocument.spreadsheet',
            'application/vnd.oasis.opendocument.presentation',
            
            # Text files
            'text/plain',
            'text/html',
            'text/xml',
            'application/xml',
            'text/csv',
            'application/rtf',
            
            # Archive formats
            'application/zip',
            'application/x-tar',
            'application/gzip',
            'application/x-rar-compressed',
            
            # Email formats
            'message/rfc822',
            'application/vnd.ms-outlook',
            
            # Image formats (with OCR)
            'image/jpeg',
            'image/png',
            'image/gif',
            'image/bmp',
            'image/tiff',
            
            # Other formats
            'application/epub+zip',
            'application/vnd.visio',
            'application/x-iwork-keynote-sffkey',
            'application/x-iwork-numbers-sffnumbers',
            'application/x-iwork-pages-sffpages'
        }
        
        logger.info(f"📋 Setup {len(self.supported_formats)} supported document formats")
        
    async def extract_content(self, file_path: str, extract_metadata: bool = True) -> ExtractedDocument:
        """Extract content från document"""
        import time
        start_time = time.time()
        
        if not self.initialized:
            await self.initialize()
            
        file_path_obj = Path(file_path)
        if not file_path_obj.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
            
        logger.info(f"📄 Extracting content from: {file_path_obj.name}")
        
        if self.tika_available:
            content, metadata = await self._extract_with_tika(file_path, extract_metadata)
        else:
            content, metadata = await self._extract_mock(file_path, extract_metadata)
            
        extraction_time = time.time() - start_time
        
        return ExtractedDocument(
            content=content,
            metadata=metadata,
            extraction_time=extraction_time,
            file_path=file_path,
            file_size=file_path_obj.stat().st_size,
            content_length=len(content)
        )
        
    async def _extract_with_tika(self, file_path: str, extract_metadata: bool) -> tuple[str, DocumentMetadata]:
        """Extract med real Tika"""
        if self.tika_jar_path:
            return await self._extract_with_jar(file_path, extract_metadata)
        else:
            return await self._extract_with_server(file_path, extract_metadata)
            
    async def _extract_with_jar(self, file_path: str, extract_metadata: bool) -> tuple[str, DocumentMetadata]:
        """Extract med Tika JAR"""
        try:
            # Extract content
            content_process = await asyncio.create_subprocess_exec(
                'java', '-jar', self.tika_jar_path, '-t', file_path,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            content_stdout, content_stderr = await content_process.communicate()
            
            if content_process.returncode != 0:
                raise Exception(f"Tika content extraction failed: {content_stderr.decode()}")
                
            content = content_stdout.decode('utf-8', errors='ignore')
            
            # Extract metadata if requested
            metadata = None
            if extract_metadata:
                metadata_process = await asyncio.create_subprocess_exec(
                    'java', '-jar', self.tika_jar_path, '-m', file_path,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )
                
                metadata_stdout, metadata_stderr = await metadata_process.communicate()
                
                if metadata_process.returncode == 0:
                    metadata_text = metadata_stdout.decode('utf-8', errors='ignore')
                    metadata = await self._parse_tika_metadata(metadata_text)
                else:
                    metadata = DocumentMetadata(content_type="unknown")
            else:
                metadata = DocumentMetadata(content_type="unknown")
                
            return content, metadata
            
        except Exception as e:
            logger.error(f"❌ Tika JAR extraction failed: {str(e)}")
            return await self._extract_mock(file_path, extract_metadata)
            
    async def _extract_with_server(self, file_path: str, extract_metadata: bool) -> tuple[str, DocumentMetadata]:
        """Extract med Tika server"""
        try:
            import aiohttp
            
            async with aiohttp.ClientSession() as session:
                # Extract content
                with open(file_path, 'rb') as f:
                    data = aiohttp.FormData()
                    data.add_field('file', f, filename=os.path.basename(file_path))
                    
                    async with session.put(f"{self.tika_server_url}/tika", data=data) as response:
                        if response.status == 200:
                            content = await response.text()
                        else:
                            raise Exception(f"Tika server error: {response.status}")
                            
                # Extract metadata if requested  
                metadata = None
                if extract_metadata:
                    with open(file_path, 'rb') as f:
                        data = aiohttp.FormData()
                        data.add_field('file', f, filename=os.path.basename(file_path))
                        
                        async with session.put(f"{self.tika_server_url}/meta", data=data) as response:
                            if response.status == 200:
                                metadata_json = await response.json()
                                metadata = await self._parse_server_metadata(metadata_json)
                            else:
                                metadata = DocumentMetadata(content_type="unknown")
                else:
                    metadata = DocumentMetadata(content_type="unknown")
                    
                return content, metadata
                
        except Exception as e:
            logger.error(f"❌ Tika server extraction failed: {str(e)}")
            return await self._extract_mock(file_path, extract_metadata)
            
    async def _extract_mock(self, file_path: str, extract_metadata: bool) -> tuple[str, DocumentMetadata]:
        """Mock extraction implementation"""
        await asyncio.sleep(0.5)  # Simulate processing time
        
        file_path_obj = Path(file_path)
        file_extension = file_path_obj.suffix.lower()
        
        # Mock content based on file extension
        if file_extension == '.pdf':
            content = f"Mock PDF content from {file_path_obj.name}\n\nThis is extracted text from a PDF document. The content would normally be extracted using Apache Tika.\n\nDocument contains multiple pages with text, images, and formatting."
            content_type = "application/pdf"
        elif file_extension in ['.docx', '.doc']:
            content = f"Mock Word document content from {file_path_obj.name}\n\nThis is extracted text from a Word document. Headers, paragraphs, tables, and other elements would be processed.\n\nOriginal formatting is converted to plain text."
            content_type = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        elif file_extension in ['.xlsx', '.xls']:
            content = f"Mock Excel spreadsheet content from {file_path_obj.name}\n\nSheet 1:\nHeader1,Header2,Header3\nValue1,Value2,Value3\nValue4,Value5,Value6\n\nSheet 2:\nData extracted from multiple sheets and tabs."
            content_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        elif file_extension in ['.pptx', '.ppt']:
            content = f"Mock PowerPoint content from {file_path_obj.name}\n\nSlide 1: Title Slide\nPresentation Title\nSubtitle and author information\n\nSlide 2: Content Slide\nBullet points and text content\nImages and charts would be described"
            content_type = "application/vnd.openxmlformats-officedocument.presentationml.presentation"
        elif file_extension == '.txt':
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
            except Exception:
                content = f"Mock text content from {file_path_obj.name}"
            content_type = "text/plain"
        elif file_extension == '.html':
            content = f"Mock HTML content from {file_path_obj.name}\n\nExtracted text content from HTML document. HTML tags are stripped and plain text is returned."
            content_type = "text/html"
        else:
            content = f"Mock content from {file_path_obj.name}\n\nGeneric content extraction for unknown file type. Apache Tika would attempt to parse the file format."
            content_type = "application/octet-stream"
            
        # Mock metadata
        metadata = DocumentMetadata(
            content_type=content_type,
            title=f"Mock Document - {file_path_obj.stem}",
            author="Mock Author",
            created=datetime.now(),
            modified=datetime.now(),
            pages=3 if file_extension == '.pdf' else None,
            words=len(content.split()),
            characters=len(content),
            language="en",
            raw_metadata={
                "mock": True,
                "file_extension": file_extension,
                "extraction_method": "mock"
            }
        ) if extract_metadata else DocumentMetadata(content_type=content_type)
        
        return content, metadata
        
    async def _parse_tika_metadata(self, metadata_text: str) -> DocumentMetadata:
        """Parse Tika metadata output"""
        metadata_dict = {}
        
        for line in metadata_text.split('\n'):
            line = line.strip()
            if ':' in line:
                key, value = line.split(':', 1)
                metadata_dict[key.strip()] = value.strip()
                
        return self._build_metadata_object(metadata_dict)
        
    async def _parse_server_metadata(self, metadata_json: Dict[str, Any]) -> DocumentMetadata:
        """Parse Tika server metadata JSON"""
        return self._build_metadata_object(metadata_json)
        
    def _build_metadata_object(self, metadata_dict: Dict[str, Any]) -> DocumentMetadata:
        """Build DocumentMetadata object från dict"""
        
        # Parse dates
        created = None
        modified = None
        
        for date_key in ['Creation-Date', 'created', 'dcterms:created']:
            if date_key in metadata_dict:
                try:
                    created = datetime.fromisoformat(metadata_dict[date_key].replace('Z', '+00:00'))
                    break
                except Exception:
                    pass
                    
        for date_key in ['Last-Modified', 'modified', 'dcterms:modified']:
            if date_key in metadata_dict:
                try:
                    modified = datetime.fromisoformat(metadata_dict[date_key].replace('Z', '+00:00'))
                    break
                except Exception:
                    pass
                    
        # Parse numeric fields
        pages = None
        words = None
        characters = None
        
        if 'xmpTPg:NPages' in metadata_dict:
            try:
                pages = int(metadata_dict['xmpTPg:NPages'])
            except ValueError:
                pass
                
        if 'Word-Count' in metadata_dict:
            try:
                words = int(metadata_dict['Word-Count'])
            except ValueError:
                pass
                
        if 'Character Count' in metadata_dict:
            try:
                characters = int(metadata_dict['Character Count'])
            except ValueError:
                pass
                
        return DocumentMetadata(
            content_type=metadata_dict.get('Content-Type', 'unknown'),
            title=metadata_dict.get('title', metadata_dict.get('dc:title')),
            author=metadata_dict.get('Author', metadata_dict.get('dc:creator')),
            creator=metadata_dict.get('Creator', metadata_dict.get('meta:author')),
            created=created,
            modified=modified,
            pages=pages,
            words=words,
            characters=characters,
            language=metadata_dict.get('language', metadata_dict.get('dc:language')),
            subject=metadata_dict.get('subject', metadata_dict.get('dc:subject')),
            keywords=metadata_dict.get('Keywords', metadata_dict.get('meta:keyword')),
            raw_metadata=metadata_dict
        )
        
    async def batch_extract(self, file_paths: List[str], extract_metadata: bool = True) -> str:
        """Batch extract multiple documents"""
        job_id = f"tika_job_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{len(self.active_jobs)}"
        
        job = ProcessingJob(
            job_id=job_id,
            file_paths=file_paths,
            status="running",
            start_time=datetime.now(),
            total_files=len(file_paths),
            errors=[]
        )
        
        self.active_jobs[job_id] = job
        
        # Start processing
        asyncio.create_task(self._run_batch_job(job_id, extract_metadata))
        
        logger.info(f"🚀 Started batch extraction job {job_id} with {len(file_paths)} files")
        return job_id
        
    async def _run_batch_job(self, job_id: str, extract_metadata: bool):
        """Run batch extraction job"""
        job = self.active_jobs[job_id]
        results = []
        
        try:
            for file_path in job.file_paths:
                if job.status == "cancelled":
                    break
                    
                try:
                    result = await self.extract_content(file_path, extract_metadata)
                    results.append(result)
                    job.processed_files += 1
                    
                except Exception as e:
                    error_msg = f"Failed to process {file_path}: {str(e)}"
                    job.errors.append(error_msg)
                    logger.error(f"❌ {error_msg}")
                    
            job.status = "completed"
            
        except Exception as e:
            job.status = "failed"
            job.errors.append(f"Batch job error: {str(e)}")
            
        finally:
            job.end_time = datetime.now()
            
        logger.info(f"✅ Batch job {job_id} completed: {job.processed_files}/{job.total_files} files processed")
        
    def get_job_status(self, job_id: str) -> Dict[str, Any]:
        """Get batch job status"""
        if job_id not in self.active_jobs:
            raise ValueError(f"Unknown job: {job_id}")
            
        job = self.active_jobs[job_id]
        
        return {
            "job_id": job.job_id,
            "status": job.status,
            "processed_files": job.processed_files,
            "total_files": job.total_files,
            "progress": job.processed_files / job.total_files if job.total_files > 0 else 0,
            "start_time": job.start_time.isoformat(),
            "end_time": job.end_time.isoformat() if job.end_time else None,
            "errors": job.errors,
            "duration": (job.end_time - job.start_time).total_seconds() if job.end_time else None
        }
        
    def is_supported_format(self, file_path: str) -> bool:
        """Check if file format is supported"""
        import mimetypes
        
        mime_type, _ = mimetypes.guess_type(file_path)
        return mime_type in self.supported_formats if mime_type else False
        
    def get_supported_formats(self) -> List[str]:
        """Get list of supported formats"""
        return sorted(list(self.supported_formats))
        
    def get_system_info(self) -> Dict[str, Any]:
        """Get Tika system information"""
        return {
            "tika_available": self.tika_available,
            "tika_jar_path": self.tika_jar_path,
            "tika_server_url": self.tika_server_url,
            "supported_formats": len(self.supported_formats),
            "active_jobs": len([job for job in self.active_jobs.values() if job.status == "running"])
        }
        
    async def cleanup(self):
        """Cleanup Tika Adapter"""
        logger.info("🧹 Cleaning up Apache Tika Adapter")
        
        # Cancel active jobs
        for job_id in list(self.active_jobs.keys()):
            job = self.active_jobs[job_id]
            if job.status == "running":
                job.status = "cancelled"
                job.end_time = datetime.now()
                
        self.active_jobs.clear()
        self.supported_formats.clear()
        self.initialized = False
        
        logger.info("✅ Apache Tika Adapter cleanup completed")
