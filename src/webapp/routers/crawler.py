"""
Crawler router for managing web crawling operations.
"""
from typing import List, Optional, Dict, Any, Union
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel, HttpUrl, Field, validator
from sqlalchemy.orm import Session
from enum import Enum
import asyncio
import json

from ..deps import (
    get_database,
    get_current_active_user,
    get_admin_user,
    RateLimiter
)

router = APIRouter()

# Enums
class CrawlStatus(str, Enum):
    """Crawl status enumeration."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    PAUSED = "paused"

class CrawlType(str, Enum):
    """Crawl type enumeration."""
    SINGLE_PAGE = "single_page"
    SITE_CRAWL = "site_crawl"
    DEEP_CRAWL = "deep_crawl"
    TARGETED_CRAWL = "targeted_crawl"

class LinkDiscoveryMode(str, Enum):
    """Link discovery modes."""
    SAME_DOMAIN = "same_domain"
    SAME_SITE = "same_site"
    ALL_LINKS = "all_links"
    PATTERN_MATCH = "pattern_match"

# Pydantic models
class CrawlConfig(BaseModel):
    """Crawl configuration model."""
    max_depth: int = Field(default=3, ge=1, le=10)
    max_pages: int = Field(default=100, ge=1, le=10000)
    delay_between_requests: float = Field(default=1.0, ge=0.1, le=60.0)
    concurrent_requests: int = Field(default=1, ge=1, le=10)
    follow_redirects: bool = True
    ignore_robots_txt: bool = False
    user_agent: Optional[str] = None
    custom_headers: Optional[Dict[str, str]] = Field(default_factory=dict)
    cookies: Optional[Dict[str, str]] = Field(default_factory=dict)
    javascript_enabled: bool = False
    screenshot_enabled: bool = False
    extract_links: bool = True
    link_discovery_mode: LinkDiscoveryMode = LinkDiscoveryMode.SAME_DOMAIN
    allowed_domains: Optional[List[str]] = None
    blocked_domains: Optional[List[str]] = None
    url_patterns: Optional[List[str]] = None
    content_types: List[str] = Field(default=["text/html"])
    
    @validator('custom_headers')
    def validate_headers(cls, v):
        if v and len(v) > 50:
            raise ValueError("Too many custom headers (max 50)")
        return v

class CrawlRequest(BaseModel):
    """Crawl request model."""
    name: str = Field(max_length=255)
    start_urls: List[HttpUrl] = Field(min_items=1, max_items=100)
    crawl_type: CrawlType = CrawlType.SITE_CRAWL
    config: CrawlConfig = Field(default_factory=CrawlConfig)
    scheduled_at: Optional[datetime] = None
    tags: Optional[List[str]] = Field(default_factory=list)
    callback_url: Optional[HttpUrl] = None
    
    @validator('tags')
    def validate_tags(cls, v):
        if v and len(v) > 20:
            raise ValueError("Too many tags (max 20)")
        return v

class CrawlUpdate(BaseModel):
    """Crawl update model."""
    name: Optional[str] = Field(default=None, max_length=255)
    config: Optional[CrawlConfig] = None
    scheduled_at: Optional[datetime] = None
    tags: Optional[List[str]] = None
    callback_url: Optional[HttpUrl] = None

class CrawlResponse(BaseModel):
    """Crawl response model."""
    id: int
    name: str
    start_urls: List[str]
    crawl_type: str
    status: str
    config: Dict[str, Any]
    created_at: datetime
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    pages_discovered: int
    pages_crawled: int
    pages_failed: int
    data_size_bytes: int
    error_message: Optional[str]
    tags: List[str]
    callback_url: Optional[str]

class CrawlStats(BaseModel):
    """Crawl statistics model."""
    total_requests: int
    successful_requests: int
    failed_requests: int
    avg_response_time: float
    data_extracted_mb: float
    links_discovered: int
    unique_domains: int
    status_codes: Dict[str, int]
    error_types: Dict[str, int]

class PageResult(BaseModel):
    """Crawled page result model."""
    id: int
    crawl_id: int
    url: str
    status_code: int
    content_type: str
    content_length: int
    response_time: float
    discovered_at: datetime
    crawled_at: Optional[datetime]
    title: Optional[str]
    meta_description: Optional[str]
    links_found: int
    error_message: Optional[str]
    screenshot_url: Optional[str]

class LinkInfo(BaseModel):
    """Link information model."""
    source_url: str
    target_url: str
    link_text: str
    link_type: str  # 'internal', 'external', 'file'
    discovered_at: datetime

# Services
class CrawlerService:
    """Crawler management service."""
    
    def __init__(self, db: Session):
        self.db = db
    
    async def create_crawl(self, user_id: int, crawl_request: CrawlRequest) -> "CrawlJob":
        """Create a new crawl job."""
        # Convert URLs to strings
        start_urls = [str(url) for url in crawl_request.start_urls]
        
        # Create crawl job
        crawl_job = CrawlJob(
            user_id=user_id,
            name=crawl_request.name,
            start_urls=start_urls,
            crawl_type=crawl_request.crawl_type,
            config=crawl_request.config.dict(),
            status=CrawlStatus.PENDING,
            scheduled_at=crawl_request.scheduled_at,
            tags=crawl_request.tags or [],
            callback_url=str(crawl_request.callback_url) if crawl_request.callback_url else None,
            created_at=datetime.utcnow()
        )
        
        self.db.add(crawl_job)
        self.db.commit()
        self.db.refresh(crawl_job)
        
        # Schedule crawl if not scheduled for later
        if not crawl_request.scheduled_at or crawl_request.scheduled_at <= datetime.utcnow():
            await self._schedule_crawl(crawl_job)
        
        return crawl_job
    
    async def start_crawl(self, crawl_id: int, user_id: int) -> "CrawlJob":
        """Start a crawl job."""
        crawl_job = self.db.query(CrawlJob).filter(
            CrawlJob.id == crawl_id,
            CrawlJob.user_id == user_id
        ).first()
        
        if not crawl_job:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Crawl job not found"
            )
        
        if crawl_job.status not in [CrawlStatus.PENDING, CrawlStatus.PAUSED]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot start crawl in {crawl_job.status} status"
            )
        
        # Update status and start crawling
        crawl_job.status = CrawlStatus.RUNNING
        crawl_job.started_at = datetime.utcnow()
        self.db.commit()
        
        # Start actual crawling process
        await self._schedule_crawl(crawl_job)
        
        return crawl_job
    
    async def pause_crawl(self, crawl_id: int, user_id: int) -> "CrawlJob":
        """Pause a running crawl job."""
        crawl_job = self.db.query(CrawlJob).filter(
            CrawlJob.id == crawl_id,
            CrawlJob.user_id == user_id
        ).first()
        
        if not crawl_job:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Crawl job not found"
            )
        
        if crawl_job.status != CrawlStatus.RUNNING:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Can only pause running crawls"
            )
        
        crawl_job.status = CrawlStatus.PAUSED
        self.db.commit()
        
        # Signal crawler to pause
        await self._signal_crawler(crawl_id, "pause")
        
        return crawl_job
    
    async def cancel_crawl(self, crawl_id: int, user_id: int) -> "CrawlJob":
        """Cancel a crawl job."""
        crawl_job = self.db.query(CrawlJob).filter(
            CrawlJob.id == crawl_id,
            CrawlJob.user_id == user_id
        ).first()
        
        if not crawl_job:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Crawl job not found"
            )
        
        if crawl_job.status in [CrawlStatus.COMPLETED, CrawlStatus.CANCELLED]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Crawl is already finished"
            )
        
        crawl_job.status = CrawlStatus.CANCELLED
        crawl_job.completed_at = datetime.utcnow()
        self.db.commit()
        
        # Signal crawler to stop
        await self._signal_crawler(crawl_id, "cancel")
        
        return crawl_job
    
    def get_crawl_stats(self, crawl_id: int, user_id: int) -> CrawlStats:
        """Get crawl statistics."""
        # Verify ownership
        crawl_job = self.db.query(CrawlJob).filter(
            CrawlJob.id == crawl_id,
            CrawlJob.user_id == user_id
        ).first()
        
        if not crawl_job:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Crawl job not found"
            )
        
        # Get page results
        pages = self.db.query(CrawledPage).filter(
            CrawledPage.crawl_id == crawl_id
        ).all()
        
        # Calculate statistics
        total_requests = len(pages)
        successful_requests = len([p for p in pages if 200 <= p.status_code < 300])
        failed_requests = total_requests - successful_requests
        
        avg_response_time = sum(p.response_time for p in pages) / total_requests if total_requests > 0 else 0
        data_extracted_mb = sum(p.content_length or 0 for p in pages) / (1024 * 1024)
        
        # Status code distribution
        status_codes = {}
        for page in pages:
            status_code = str(page.status_code)
            status_codes[status_code] = status_codes.get(status_code, 0) + 1
        
        # Error type distribution
        error_types = {}
        for page in pages:
            if page.error_message:
                error_type = page.error_message.split(':')[0]
                error_types[error_type] = error_types.get(error_type, 0) + 1
        
        # Count unique domains
        unique_domains = len(set(self._extract_domain(p.url) for p in pages))
        
        # Count discovered links
        links_discovered = self.db.query(DiscoveredLink).filter(
            DiscoveredLink.crawl_id == crawl_id
        ).count()
        
        return CrawlStats(
            total_requests=total_requests,
            successful_requests=successful_requests,
            failed_requests=failed_requests,
            avg_response_time=avg_response_time,
            data_extracted_mb=data_extracted_mb,
            links_discovered=links_discovered,
            unique_domains=unique_domains,
            status_codes=status_codes,
            error_types=error_types
        )
    
    def get_crawl_pages(
        self, 
        crawl_id: int, 
        user_id: int, 
        skip: int = 0, 
        limit: int = 100,
        status_filter: Optional[str] = None
    ) -> List["CrawledPage"]:
        """Get crawled pages for a job."""
        # Verify ownership
        crawl_job = self.db.query(CrawlJob).filter(
            CrawlJob.id == crawl_id,
            CrawlJob.user_id == user_id
        ).first()
        
        if not crawl_job:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Crawl job not found"
            )
        
        query = self.db.query(CrawledPage).filter(CrawledPage.crawl_id == crawl_id)
        
        if status_filter:
            if status_filter == "success":
                query = query.filter(CrawledPage.status_code.between(200, 299))
            elif status_filter == "error":
                query = query.filter(~CrawledPage.status_code.between(200, 299))
        
        return query.offset(skip).limit(limit).all()
    
    def get_discovered_links(
        self,
        crawl_id: int,
        user_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> List["DiscoveredLink"]:
        """Get discovered links for a crawl."""
        # Verify ownership
        crawl_job = self.db.query(CrawlJob).filter(
            CrawlJob.id == crawl_id,
            CrawlJob.user_id == user_id
        ).first()
        
        if not crawl_job:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Crawl job not found"
            )
        
        return self.db.query(DiscoveredLink).filter(
            DiscoveredLink.crawl_id == crawl_id
        ).offset(skip).limit(limit).all()
    
    async def _schedule_crawl(self, crawl_job: "CrawlJob"):
        """Schedule crawl job for execution."""
        # This would integrate with your task queue (Celery, RQ, etc.)
        # For now, we'll simulate scheduling
        from ..crawler.manager import CrawlerManager
        
        crawler_manager = CrawlerManager()
        await crawler_manager.schedule_crawl(crawl_job)
    
    async def _signal_crawler(self, crawl_id: int, signal: str):
        """Send signal to running crawler."""
        # This would send signals through Redis/message queue
        pass
    
    def _extract_domain(self, url: str) -> str:
        """Extract domain from URL."""
        from urllib.parse import urlparse
        return urlparse(url).netloc

crawler_service_instance = None

def get_crawler_service(db: Session = Depends(get_database)) -> CrawlerService:
    """Get crawler service instance."""
    global crawler_service_instance
    if not crawler_service_instance:
        crawler_service_instance = CrawlerService(db)
    return crawler_service_instance

# Routes
@router.post("/", response_model=CrawlResponse, status_code=status.HTTP_201_CREATED)
async def create_crawl(
    crawl_request: CrawlRequest,
    background_tasks: BackgroundTasks,
    current_user = Depends(get_current_active_user),
    crawler_service: CrawlerService = Depends(get_crawler_service),
    rate_limit: dict = Depends(RateLimiter("20/hour"))
):
    """Create a new crawl job."""
    crawl_job = await crawler_service.create_crawl(current_user.id, crawl_request)
    return CrawlResponse.from_orm(crawl_job)

@router.get("/", response_model=List[CrawlResponse])
async def list_crawls(
    skip: int = 0,
    limit: int = 100,
    status: Optional[CrawlStatus] = None,
    current_user = Depends(get_current_active_user),
    db: Session = Depends(get_database)
):
    """List user's crawl jobs."""
    query = db.query(CrawlJob).filter(CrawlJob.user_id == current_user.id)
    
    if status:
        query = query.filter(CrawlJob.status == status)
    
    crawls = query.order_by(CrawlJob.created_at.desc()).offset(skip).limit(limit).all()
    return [CrawlResponse.from_orm(crawl) for crawl in crawls]

@router.get("/{crawl_id}", response_model=CrawlResponse)
async def get_crawl(
    crawl_id: int,
    current_user = Depends(get_current_active_user),
    db: Session = Depends(get_database)
):
    """Get a specific crawl job."""
    crawl_job = db.query(CrawlJob).filter(
        CrawlJob.id == crawl_id,
        CrawlJob.user_id == current_user.id
    ).first()
    
    if not crawl_job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Crawl job not found"
        )
    
    return CrawlResponse.from_orm(crawl_job)

@router.put("/{crawl_id}", response_model=CrawlResponse)
async def update_crawl(
    crawl_id: int,
    crawl_update: CrawlUpdate,
    current_user = Depends(get_current_active_user),
    db: Session = Depends(get_database)
):
    """Update a crawl job (only if not started)."""
    crawl_job = db.query(CrawlJob).filter(
        CrawlJob.id == crawl_id,
        CrawlJob.user_id == current_user.id
    ).first()
    
    if not crawl_job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Crawl job not found"
        )
    
    if crawl_job.status not in [CrawlStatus.PENDING, CrawlStatus.PAUSED]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot update crawl in current status"
        )
    
    # Update fields
    update_dict = crawl_update.dict(exclude_unset=True)
    for field, value in update_dict.items():
        if field == "config" and value:
            # Merge config
            current_config = crawl_job.config or {}
            current_config.update(value.dict())
            setattr(crawl_job, field, current_config)
        elif field == "callback_url" and value:
            setattr(crawl_job, field, str(value))
        else:
            setattr(crawl_job, field, value)
    
    db.commit()
    db.refresh(crawl_job)
    
    return CrawlResponse.from_orm(crawl_job)

@router.post("/{crawl_id}/start", response_model=CrawlResponse)
async def start_crawl(
    crawl_id: int,
    current_user = Depends(get_current_active_user),
    crawler_service: CrawlerService = Depends(get_crawler_service)
):
    """Start a crawl job."""
    crawl_job = await crawler_service.start_crawl(crawl_id, current_user.id)
    return CrawlResponse.from_orm(crawl_job)

@router.post("/{crawl_id}/pause", response_model=CrawlResponse)
async def pause_crawl(
    crawl_id: int,
    current_user = Depends(get_current_active_user),
    crawler_service: CrawlerService = Depends(get_crawler_service)
):
    """Pause a running crawl job."""
    crawl_job = await crawler_service.pause_crawl(crawl_id, current_user.id)
    return CrawlResponse.from_orm(crawl_job)

@router.post("/{crawl_id}/cancel", response_model=CrawlResponse)
async def cancel_crawl(
    crawl_id: int,
    current_user = Depends(get_current_active_user),
    crawler_service: CrawlerService = Depends(get_crawler_service)
):
    """Cancel a crawl job."""
    crawl_job = await crawler_service.cancel_crawl(crawl_id, current_user.id)
    return CrawlResponse.from_orm(crawl_job)

@router.delete("/{crawl_id}")
async def delete_crawl(
    crawl_id: int,
    current_user = Depends(get_current_active_user),
    db: Session = Depends(get_database)
):
    """Delete a crawl job and all associated data."""
    crawl_job = db.query(CrawlJob).filter(
        CrawlJob.id == crawl_id,
        CrawlJob.user_id == current_user.id
    ).first()
    
    if not crawl_job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Crawl job not found"
        )
    
    if crawl_job.status == CrawlStatus.RUNNING:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete running crawl job"
        )
    
    # Delete associated data
    db.query(CrawledPage).filter(CrawledPage.crawl_id == crawl_id).delete()
    db.query(DiscoveredLink).filter(DiscoveredLink.crawl_id == crawl_id).delete()
    db.delete(crawl_job)
    db.commit()
    
    return {"message": "Crawl job deleted successfully"}

@router.get("/{crawl_id}/stats", response_model=CrawlStats)
async def get_crawl_stats(
    crawl_id: int,
    current_user = Depends(get_current_active_user),
    crawler_service: CrawlerService = Depends(get_crawler_service)
):
    """Get crawl statistics."""
    return crawler_service.get_crawl_stats(crawl_id, current_user.id)

@router.get("/{crawl_id}/pages", response_model=List[PageResult])
async def get_crawl_pages(
    crawl_id: int,
    skip: int = 0,
    limit: int = 100,
    status_filter: Optional[str] = Query(None, regex="^(success|error)$"),
    current_user = Depends(get_current_active_user),
    crawler_service: CrawlerService = Depends(get_crawler_service)
):
    """Get crawled pages for a job."""
    pages = crawler_service.get_crawl_pages(
        crawl_id, current_user.id, skip, limit, status_filter
    )
    return [PageResult.from_orm(page) for page in pages]

@router.get("/{crawl_id}/links", response_model=List[LinkInfo])
async def get_discovered_links(
    crawl_id: int,
    skip: int = 0,
    limit: int = 100,
    current_user = Depends(get_current_active_user),
    crawler_service: CrawlerService = Depends(get_crawler_service)
):
    """Get discovered links for a crawl."""
    links = crawler_service.get_discovered_links(crawl_id, current_user.id, skip, limit)
    return [LinkInfo.from_orm(link) for link in links]

# Admin routes
@router.get("/admin/crawls", response_model=List[CrawlResponse])
async def admin_list_all_crawls(
    skip: int = 0,
    limit: int = 100,
    current_user = Depends(get_admin_user),
    db: Session = Depends(get_database)
):
    """List all crawl jobs (admin only)."""
    crawls = db.query(CrawlJob).offset(skip).limit(limit).all()
    return [CrawlResponse.from_orm(crawl) for crawl in crawls]

@router.post("/admin/crawls/{crawl_id}/force-stop")
async def admin_force_stop_crawl(
    crawl_id: int,
    current_user = Depends(get_admin_user),
    db: Session = Depends(get_database)
):
    """Force stop a crawl job (admin only)."""
    crawl_job = db.query(CrawlJob).filter(CrawlJob.id == crawl_id).first()
    
    if not crawl_job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Crawl job not found"
        )
    
    crawl_job.status = CrawlStatus.CANCELLED
    crawl_job.completed_at = datetime.utcnow()
    crawl_job.error_message = "Force stopped by admin"
    
    db.commit()
    
    return {"message": "Crawl job force stopped"}

# Health check
@router.get("/health")
async def crawler_health_check():
    """Health check for crawler service."""
    return {
        "status": "healthy",
        "service": "crawler",
        "timestamp": datetime.utcnow().isoformat()
    }
