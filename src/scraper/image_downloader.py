"""
This module will handle the downloading of media files like images and PDFs.
It will include features like rate limiting, checksum validation (hashing),
deduplication, and storing files in an object storage (e.g., S3/GCS),
with references stored in the database.

This corresponds to the requirements outlined in "Media & filer" (Kapitel 6.9).
"""
"""
Image and file downloading logic.

Provides comprehensive downloading capabilities for images,
documents, and other files with proper handling of metadata,
validation, and storage organization.
"""

import os
import hashlib
import mimetypes
import time
from typing import Dict, List, Optional, Any, Set, Tuple
from urllib.parse import urljoin, urlparse
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
import aiohttp
import asyncio
from PIL import Image, ImageFile
import magic

from src.utils.logger import get_logger

logger = get_logger(__name__)
ImageFile.LOAD_TRUNCATED_IMAGES = True

@dataclass
class DownloadResult:
    """Result of a download operation"""
    url: str
    local_path: Optional[str] = None
    file_size: int = 0
    content_type: Optional[str] = None
    file_hash: Optional[str] = None
    status: str = "pending"
    error: Optional[str] = None
    metadata: Dict[str, Any] = None
    downloaded_at: Optional[datetime] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}

class ImageDownloader:
    """
    Advanced image and file downloader.
    
    Features:
    - Async/concurrent downloads
    - File type validation
    - Duplicate detection
    - Image processing and metadata extraction
    - Organized storage structure
    - Progress tracking
    - Error handling and retries
    """
    
    def __init__(self,
                 download_dir: str = "data/downloads",
                 max_concurrent: int = 10,
                 max_file_size: int = 50 * 1024 * 1024,  # 50MB
                 allowed_extensions: Optional[Set[str]] = None,
                 user_agent: Optional[str] = None,
                 timeout: int = 30):
        
        self.download_dir = Path(download_dir)
        self.max_concurrent = max_concurrent
        self.max_file_size = max_file_size
        self.timeout = timeout
        
        # Default allowed extensions
        if allowed_extensions is None:
            self.allowed_extensions = {
                # Images
                '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp', '.svg',
                # Documents
                '.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx', '.txt',
                # Media
                '.mp4', '.avi', '.mov', '.mp3', '.wav', '.flac',
                # Archives
                '.zip', '.rar', '.tar', '.gz', '.7z'
            }
        else:
            self.allowed_extensions = allowed_extensions
        
        self.user_agent = user_agent or (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        
        # Create directory structure
        self._create_directories()
        
        # Downloaded files tracking
        self.downloaded_files: Dict[str, DownloadResult] = {}
        self.file_hashes: Set[str] = set()
        
        # Load existing files
        self._load_existing_files()
    
    def _create_directories(self):
        """Create organized directory structure"""
        subdirs = [
            'images', 'documents', 'media', 'archives', 'other'
        ]
        
        for subdir in subdirs:
            (self.download_dir / subdir).mkdir(parents=True, exist_ok=True)
    
    def _load_existing_files(self):
        """Load information about existing downloaded files"""
        if not self.download_dir.exists():
            return
        
        for file_path in self.download_dir.rglob('*'):
            if file_path.is_file():
                try:
                    file_hash = self._calculate_file_hash(file_path)
                    self.file_hashes.add(file_hash)
                    
                    result = DownloadResult(
                        url="",  # Unknown for existing files
                        local_path=str(file_path),
                        file_size=file_path.stat().st_size,
                        file_hash=file_hash,
                        status="existing"
                    )
                    
                    self.downloaded_files[str(file_path)] = result
                    
                except Exception as e:
                    logger.warning(f"Failed to process existing file {file_path}: {e}")
    
    async def download_file(self,
                           url: str,
                           filename: Optional[str] = None,
                           headers: Optional[Dict[str, str]] = None) -> DownloadResult:
        """
        Download a single file.
        
        Args:
            url: URL to download
            filename: Custom filename (optional)
            headers: Additional headers
            
        Returns:
            Download result
        """
        result = DownloadResult(url=url)
        
        try:
            # Validate URL
            if not self._is_valid_url(url):
                result.status = "error"
                result.error = "Invalid URL"
                return result
            
            # Prepare headers
            request_headers = {"User-Agent": self.user_agent}
            if headers:
                request_headers.update(headers)
            
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=self.timeout)) as session:
                # Get file info first
                async with session.head(url, headers=request_headers) as response:
                    if response.status >= 400:
                        result.status = "error"
                        result.error = f"HTTP {response.status}"
                        return result
                    
                    content_type = response.headers.get('content-type', '')
                    content_length = int(response.headers.get('content-length', 0))
                    
                    # Check file size
                    if content_length > self.max_file_size:
                        result.status = "error"
                        result.error = f"File too large: {content_length} bytes"
                        return result
                
                # Download the file
                async with session.get(url, headers=request_headers) as response:
                    if response.status >= 400:
                        result.status = "error"
                        result.error = f"HTTP {response.status}"
                        return result
                    
                    content = await response.read()
                    
                    # Validate content
                    if len(content) > self.max_file_size:
                        result.status = "error"
                        result.error = f"Content too large: {len(content)} bytes"
                        return result
                    
                    # Calculate hash to check for duplicates
                    file_hash = hashlib.md5(content).hexdigest()
                    
                    if file_hash in self.file_hashes:
                        result.status = "duplicate"
                        result.file_hash = file_hash
                        return result
                    
                    # Determine file extension and category
                    file_extension, category = self._determine_file_type(url, content_type, content)
                    
                    # Check if extension is allowed
                    if file_extension not in self.allowed_extensions:
                        result.status = "error"
                        result.error = f"File type not allowed: {file_extension}"
                        return result
                    
                    # Generate filename
                    if not filename:
                        filename = self._generate_filename(url, file_extension, file_hash)
                    
                    # Determine save path
                    save_path = self.download_dir / category / filename
                    save_path.parent.mkdir(parents=True, exist_ok=True)
                    
                    # Save file
                    with open(save_path, 'wb') as f:
                        f.write(content)
                    
                    # Extract metadata
                    metadata = await self._extract_metadata(save_path, content_type)
                    
                    # Update result
                    result.local_path = str(save_path)
                    result.file_size = len(content)
                    result.content_type = content_type
                    result.file_hash = file_hash
                    result.status = "success"
                    result.metadata = metadata
                    result.downloaded_at = datetime.utcnow()
                    
                    # Track downloaded file
                    self.downloaded_files[url] = result
                    self.file_hashes.add(file_hash)
                    
                    logger.info(f"Downloaded: {url} -> {save_path}")
                    
        except asyncio.TimeoutError:
            result.status = "error"
            result.error = "Download timeout"
        except Exception as e:
            result.status = "error"
            result.error = str(e)
            logger.error(f"Failed to download {url}: {e}")
        
        return result
    
    async def download_multiple(self,
                               urls: List[str],
                               progress_callback: Optional[callable] = None) -> List[DownloadResult]:
        """
        Download multiple files concurrently.
        
        Args:
            urls: List of URLs to download
            progress_callback: Optional progress callback function
            
        Returns:
            List of download results
        """
        semaphore = asyncio.Semaphore(self.max_concurrent)
        
        async def download_with_semaphore(url: str, index: int) -> DownloadResult:
            async with semaphore:
                result = await self.download_file(url)
                
                if progress_callback:
                    progress_callback(index + 1, len(urls), result)
                
                return result
        
        tasks = [download_with_semaphore(url, i) for i, url in enumerate(urls)]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Handle exceptions
        final_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                error_result = DownloadResult(
                    url=urls[i],
                    status="error",
                    error=str(result)
                )
                final_results.append(error_result)
            else:
                final_results.append(result)
        
        return final_results
    
    def _is_valid_url(self, url: str) -> bool:
        """Validate URL format"""
        try:
            parsed = urlparse(url)
            return bool(parsed.scheme and parsed.netloc)
        except Exception:
            return False
    
    def _determine_file_type(self, url: str, content_type: str, content: bytes) -> Tuple[str, str]:
        """Determine file extension and category"""
        # Try to get extension from URL
        parsed_url = urlparse(url)
        url_extension = os.path.splitext(parsed_url.path)[1].lower()
        
        # Try to get extension from content type
        content_extension = mimetypes.guess_extension(content_type.split(';')[0])
        
        # Use magic to detect file type from content
        try:
            magic_mime = magic.from_buffer(content, mime=True)
            magic_extension = mimetypes.guess_extension(magic_mime)
        except Exception:
            magic_extension = None
        
        # Determine best extension
        extension = url_extension or content_extension or magic_extension or '.bin'
        
        # Determine category
        if extension in {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp', '.svg'}:
            category = 'images'
        elif extension in {'.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx', '.txt'}:
            category = 'documents'
        elif extension in {'.mp4', '.avi', '.mov', '.mp3', '.wav', '.flac'}:
            category = 'media'
        elif extension in {'.zip', '.rar', '.tar', '.gz', '.7z'}:
            category = 'archives'
        else:
            category = 'other'
        
        return extension, category
    
    def _generate_filename(self, url: str, extension: str, file_hash: str) -> str:
        """Generate a unique filename"""
        parsed_url = urlparse(url)
        
        # Try to extract filename from URL
        url_filename = os.path.basename(parsed_url.path)
        
        if url_filename and not url_filename.startswith('.'):
            # Use URL filename with hash prefix for uniqueness
            base_name = os.path.splitext(url_filename)[0]
            return f"{file_hash[:8]}_{base_name}{extension}"
        else:
            # Generate filename from hash and timestamp
            timestamp = int(time.time())
            return f"{file_hash[:8]}_{timestamp}{extension}"
    
    def _calculate_file_hash(self, file_path: Path) -> str:
        """Calculate MD5 hash of a file"""
        hash_md5 = hashlib.md5()
        
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        
        return hash_md5.hexdigest()
    
    async def _extract_metadata(self, file_path: Path, content_type: str) -> Dict[str, Any]:
        """Extract metadata from downloaded file"""
        metadata = {
            'file_size': file_path.stat().st_size,
            'content_type': content_type,
            'downloaded_at': datetime.utcnow().isoformat()
        }
        
        try:
            # Extract image metadata
            if content_type.startswith('image/'):
                metadata.update(self._extract_image_metadata(file_path))
            
            # Add file system metadata
            stat = file_path.stat()
            metadata.update({
                'created_at': datetime.fromtimestamp(stat.st_ctime).isoformat(),
                'modified_at': datetime.fromtimestamp(stat.st_mtime).isoformat(),
                'file_extension': file_path.suffix.lower()
            })
            
        except Exception as e:
            logger.warning(f"Failed to extract metadata for {file_path}: {e}")
        
        return metadata
    
    def _extract_image_metadata(self, file_path: Path) -> Dict[str, Any]:
        """Extract metadata from image files"""
        metadata = {}
        
        try:
            with Image.open(file_path) as img:
                metadata.update({
                    'width': img.width,
                    'height': img.height,
                    'format': img.format,
                    'mode': img.mode
                })
                
                # Extract EXIF data if available
                if hasattr(img, '_getexif') and img._getexif():
                    exif_data = img._getexif()
                    if exif_data:
                        # Extract common EXIF tags
                        metadata['exif'] = {
                            str(key): str(value) for key, value in exif_data.items()
                            if isinstance(value, (str, int, float))
                        }
        
        except Exception as e:
            logger.warning(f"Failed to extract image metadata: {e}")
        
        return metadata
    
    def get_download_stats(self) -> Dict[str, Any]:
        """Get download statistics"""
        total_files = len(self.downloaded_files)
        successful = sum(1 for r in self.downloaded_files.values() if r.status == "success")
        duplicates = sum(1 for r in self.downloaded_files.values() if r.status == "duplicate")
        errors = sum(1 for r in self.downloaded_files.values() if r.status == "error")
        
        total_size = sum(r.file_size for r in self.downloaded_files.values() if r.file_size)
        
        # Category breakdown
        categories = {}
        for result in self.downloaded_files.values():
            if result.local_path:
                category = Path(result.local_path).parent.name
                categories[category] = categories.get(category, 0) + 1
        
        return {
            'total_files': total_files,
            'successful': successful,
            'duplicates': duplicates,
            'errors': errors,
            'total_size_bytes': total_size,
            'total_size_mb': round(total_size / (1024 * 1024), 2),
            'categories': categories
        }
    
    def get_download_results(self) -> List[DownloadResult]:
        """Get all download results"""
        return list(self.downloaded_files.values())
    
    def find_duplicates(self) -> List[Tuple[str, List[str]]]:
        """Find duplicate files by hash"""
        hash_to_files = {}
        
        for result in self.downloaded_files.values():
            if result.file_hash and result.local_path:
                if result.file_hash not in hash_to_files:
                    hash_to_files[result.file_hash] = []
                hash_to_files[result.file_hash].append(result.local_path)
        
        duplicates = [(h, files) for h, files in hash_to_files.items() if len(files) > 1]
        return duplicates
    
    def cleanup_duplicates(self, keep_strategy: str = "first") -> int:
        """
        Remove duplicate files.
        
        Args:
            keep_strategy: Strategy for which file to keep ("first", "last", "largest")
            
        Returns:
            Number of files removed
        """
        duplicates = self.find_duplicates()
        removed_count = 0
        
        for file_hash, file_paths in duplicates:
            if keep_strategy == "first":
                files_to_remove = file_paths[1:]
            elif keep_strategy == "last":
                files_to_remove = file_paths[:-1]
            elif keep_strategy == "largest":
                # Keep the largest file
                files_with_sizes = [(p, Path(p).stat().st_size) for p in file_paths]
                files_with_sizes.sort(key=lambda x: x[1], reverse=True)
                files_to_remove = [p for p, _ in files_with_sizes[1:]]
            else:
                continue
            
            for file_path in files_to_remove:
                try:
                    Path(file_path).unlink()
                    removed_count += 1
                    logger.info(f"Removed duplicate file: {file_path}")
                except Exception as e:
                    logger.error(f"Failed to remove {file_path}: {e}")
        
        return removed_count