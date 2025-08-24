"""
Production Database Backend for Sparkling Owl Spin Platform
Complete database layer with SQLAlchemy models, repository pattern, and advanced features.
"""

import asyncio
import json
import hashlib
from typing import List, Dict, Any, Optional, Union, Tuple, AsyncGenerator
from datetime import datetime, timedelta
from contextlib import asynccontextmanager

import asyncpg
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, DateTime, Text, JSON, Boolean, Float, ForeignKey, Index
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
from sqlalchemy import select, update, delete, and_, or_

from ..utils.logger import get_logger

logger = get_logger(__name__)

# Database Models
Base = declarative_base()

class CrawlJob(Base):
    """Represents a crawling job"""
    __tablename__ = 'crawl_jobs'
    
    id = Column(UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid())
    name = Column(String(255), nullable=False)
    description = Column(Text)
    status = Column(String(50), default='pending')  # pending, running, completed, failed, stopped
    strategy = Column(String(50), default='bfs')  # bfs, dfs, intelligent, priority
    
    # Configuration
    start_urls = Column(JSONB, nullable=False)
    max_pages = Column(Integer, default=10000)
    max_depth = Column(Integer, default=10)
    max_concurrent = Column(Integer, default=20)
    delay_between_requests = Column(Float, default=1.0)
    respect_robots_txt = Column(Boolean, default=True)
    follow_external_links = Column(Boolean, default=False)
    
    # Filtering
    allowed_domains = Column(JSONB)
    blocked_domains = Column(JSONB)
    url_patterns = Column(JSONB)
    
    # Timestamps
    created_at = Column(DateTime, server_default=func.now())
    started_at = Column(DateTime)
    completed_at = Column(DateTime)
    updated_at = Column(DateTime, onupdate=func.now())
    
    # Statistics
    total_discovered = Column(Integer, default=0)
    total_crawled = Column(Integer, default=0)
    total_failed = Column(Integer, default=0)
    pages_per_second = Column(Float, default=0.0)
    
    # Relationships
    crawled_pages = relationship("CrawledPage", back_populates="job")
    discovered_links = relationship("DiscoveredLink", back_populates="job")
    
    # Indexes
    __table_args__ = (
        Index('idx_crawl_jobs_status', 'status'),
        Index('idx_crawl_jobs_created_at', 'created_at'),
    )

class CrawledPage(Base):
    """Represents a crawled page with all extracted data"""
    __tablename__ = 'crawled_pages'
    
    id = Column(UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid())
    job_id = Column(UUID(as_uuid=True), ForeignKey('crawl_jobs.id'), nullable=False)
    
    # URL and basic info
    url = Column(String(2048), nullable=False)
    url_hash = Column(String(64), nullable=False, unique=True)
    parent_url = Column(String(2048))
    depth = Column(Integer, default=0)
    
    # HTTP response data
    status_code = Column(Integer)
    content_type = Column(String(255))
    content_length = Column(Integer)
    response_time = Column(Float)
    
    # Content
    html_content = Column(Text)
    raw_headers = Column(JSONB)
    
    # Extracted data
    extracted_data = Column(JSONB)
    links_found = Column(JSONB)
    page_metadata = Column(JSONB)  # Renamed to avoid conflict with SQLAlchemy
    
    # Processing info
    crawled_at = Column(DateTime, server_default=func.now())
    processing_time = Column(Float)
    error_message = Column(Text)
    retry_count = Column(Integer, default=0)
    
    # AI Analysis
    content_type_detected = Column(String(100))  # article, product, listing, etc.
    language_detected = Column(String(10))
    sentiment_score = Column(Float)
    key_topics = Column(JSONB)
    
    # SEO data
    title = Column(String(500))
    meta_description = Column(Text)
    h1_tags = Column(JSONB)
    images = Column(JSONB)
    
    # Relationships
    job = relationship("CrawlJob", back_populates="crawled_pages")
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if self.url and not self.url_hash:
            self.url_hash = hashlib.sha256(self.url.encode()).hexdigest()
    
    # Indexes
    __table_args__ = (
        Index('idx_crawled_pages_job_id', 'job_id'),
        Index('idx_crawled_pages_url_hash', 'url_hash'),
        Index('idx_crawled_pages_crawled_at', 'crawled_at'),
        Index('idx_crawled_pages_status_code', 'status_code'),
        Index('idx_crawled_pages_depth', 'depth'),
    )

class DiscoveredLink(Base):
    """Represents a discovered link that may be crawled later"""
    __tablename__ = 'discovered_links'
    
    id = Column(UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid())
    job_id = Column(UUID(as_uuid=True), ForeignKey('crawl_jobs.id'), nullable=False)
    
    url = Column(String(2048), nullable=False)
    url_hash = Column(String(64), nullable=False)
    source_url = Column(String(2048), nullable=False)  # Page where link was found
    
    # Queue information
    priority = Column(Integer, default=5)
    depth = Column(Integer, default=0)
    discovered_at = Column(DateTime, server_default=func.now())
    queued_at = Column(DateTime)
    crawled_at = Column(DateTime)
    
    # Link analysis
    link_text = Column(String(500))  # Anchor text
    link_context = Column(Text)  # Surrounding text
    estimated_value = Column(Float, default=0.0)
    link_type = Column(String(50))  # internal, external, download, etc.
    
    # Status tracking
    status = Column(String(50), default='discovered')  # discovered, queued, crawling, crawled, failed, skipped
    error_message = Column(Text)
    
    # Relationships
    job = relationship("CrawlJob", back_populates="discovered_links")
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if self.url and not self.url_hash:
            self.url_hash = hashlib.sha256(self.url.encode()).hexdigest()
    
    # Indexes
    __table_args__ = (
        Index('idx_discovered_links_job_id', 'job_id'),
        Index('idx_discovered_links_url_hash', 'url_hash'),
        Index('idx_discovered_links_status', 'status'),
        Index('idx_discovered_links_priority', 'priority'),
        Index('idx_discovered_links_discovered_at', 'discovered_at'),
    )

class ExtractionRule(Base):
    """Represents data extraction rules"""
    __tablename__ = 'extraction_rules'
    
    id = Column(UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid())
    name = Column(String(255), nullable=False)
    description = Column(Text)
    
    # Rule definition
    domain_pattern = Column(String(255))  # Domain this rule applies to
    url_pattern = Column(String(500))  # URL pattern this rule applies to
    content_type = Column(String(100))  # article, product, listing, etc.
    
    # Extraction selectors
    selectors = Column(JSONB, nullable=False)  # CSS/XPath selectors
    field_mappings = Column(JSONB)  # Field name mappings
    validation_rules = Column(JSONB)  # Data validation rules
    
    # Metadata
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    is_active = Column(Boolean, default=True)
    priority = Column(Integer, default=5)
    
    # Usage statistics
    times_used = Column(Integer, default=0)
    success_rate = Column(Float, default=0.0)
    
    # Indexes
    __table_args__ = (
        Index('idx_extraction_rules_domain_pattern', 'domain_pattern'),
        Index('idx_extraction_rules_content_type', 'content_type'),
        Index('idx_extraction_rules_is_active', 'is_active'),
    )

class CrawlTemplate(Base):
    """Represents crawling templates/configurations"""
    __tablename__ = 'crawl_templates'
    
    id = Column(UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid())
    name = Column(String(255), nullable=False)
    description = Column(Text)
    category = Column(String(100))  # ecommerce, news, social, etc.
    
    # Template configuration
    template_config = Column(JSONB, nullable=False)
    default_settings = Column(JSONB)
    extraction_rules = Column(JSONB)
    
    # Metadata
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    created_by = Column(String(255))
    is_public = Column(Boolean, default=False)
    
    # Usage statistics
    times_used = Column(Integer, default=0)
    avg_success_rate = Column(Float, default=0.0)
    
    # Indexes
    __table_args__ = (
        Index('idx_crawl_templates_category', 'category'),
        Index('idx_crawl_templates_is_public', 'is_public'),
        Index('idx_crawl_templates_created_at', 'created_at'),
    )

# Repository Classes for Data Access
class BaseRepository:
    """Base repository with common database operations"""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def commit(self):
        """Commit the current transaction"""
        await self.session.commit()
    
    async def rollback(self):
        """Rollback the current transaction"""
        await self.session.rollback()

class CrawlJobRepository(BaseRepository):
    """Repository for crawl job operations"""
    
    async def create_job(self, **kwargs) -> CrawlJob:
        """Create a new crawl job"""
        job = CrawlJob(**kwargs)
        self.session.add(job)
        await self.session.flush()
        return job
    
    async def get_job_by_id(self, job_id: str) -> Optional[CrawlJob]:
        """Get job by ID"""
        result = await self.session.execute(
            select(CrawlJob).where(CrawlJob.id == job_id)
        )
        return result.scalar_one_or_none()
    
    async def update_job_status(self, job_id: str, status: str, **kwargs) -> bool:
        """Update job status and other fields"""
        update_data = {'status': status, 'updated_at': datetime.utcnow()}
        update_data.update(kwargs)
        
        result = await self.session.execute(
            update(CrawlJob)
            .where(CrawlJob.id == job_id)
            .values(**update_data)
        )
        return result.rowcount > 0
    
    async def get_jobs_by_status(self, status: str, limit: int = 100) -> List[CrawlJob]:
        """Get jobs by status"""
        result = await self.session.execute(
            select(CrawlJob)
            .where(CrawlJob.status == status)
            .order_by(CrawlJob.created_at.desc())
            .limit(limit)
        )
        return list(result.scalars().all())
    
    async def get_running_jobs(self) -> List[CrawlJob]:
        """Get currently running jobs"""
        result = await self.session.execute(
            select(CrawlJob)
            .where(CrawlJob.status.in_(['running', 'pending']))
            .order_by(CrawlJob.started_at.desc())
        )
        return list(result.scalars().all())
    
    async def update_job_stats(self, job_id: str, stats: Dict[str, Any]) -> bool:
        """Update job statistics"""
        result = await self.session.execute(
            update(CrawlJob)
            .where(CrawlJob.id == job_id)
            .values(**stats, updated_at=datetime.utcnow())
        )
        return result.rowcount > 0

class CrawledPageRepository(BaseRepository):
    """Repository for crawled page operations"""
    
    async def save_page(self, **kwargs) -> CrawledPage:
        """Save a crawled page"""
        page = CrawledPage(**kwargs)
        self.session.add(page)
        await self.session.flush()
        return page
    
    async def get_page_by_url(self, job_id: str, url: str) -> Optional[CrawledPage]:
        """Get page by URL"""
        url_hash = hashlib.sha256(url.encode()).hexdigest()
        
        result = await self.session.execute(
            select(CrawledPage)
            .where(and_(
                CrawledPage.job_id == job_id,
                CrawledPage.url_hash == url_hash
            ))
        )
        return result.scalar_one_or_none()
    
    async def get_pages_by_job(self, job_id: str, limit: int = 100, offset: int = 0) -> List[CrawledPage]:
        """Get pages by job ID with pagination"""
        result = await self.session.execute(
            select(CrawledPage)
            .where(CrawledPage.job_id == job_id)
            .order_by(CrawledPage.crawled_at.desc())
            .limit(limit)
            .offset(offset)
        )
        return list(result.scalars().all())
    
    async def get_pages_by_status_code(self, job_id: str, status_code: int) -> List[CrawledPage]:
        """Get pages by HTTP status code"""
        result = await self.session.execute(
            select(CrawledPage)
            .where(and_(
                CrawledPage.job_id == job_id,
                CrawledPage.status_code == status_code
            ))
            .order_by(CrawledPage.crawled_at.desc())
        )
        return list(result.scalars().all())
    
    async def search_pages_by_content(self, job_id: str, query: str) -> List[CrawledPage]:
        """Search pages by content"""
        result = await self.session.execute(
            select(CrawledPage)
            .where(and_(
                CrawledPage.job_id == job_id,
                or_(
                    CrawledPage.title.ilike(f'%{query}%'),
                    CrawledPage.html_content.ilike(f'%{query}%'),
                    CrawledPage.meta_description.ilike(f'%{query}%')
                )
            ))
            .order_by(CrawledPage.crawled_at.desc())
        )
        return list(result.scalars().all())
    
    async def get_page_count_by_job(self, job_id: str) -> int:
        """Get total page count for a job"""
        result = await self.session.execute(
            select(func.count(CrawledPage.id))
            .where(CrawledPage.job_id == job_id)
        )
        return result.scalar() or 0

class DiscoveredLinkRepository(BaseRepository):
    """Repository for discovered link operations"""
    
    async def save_link(self, **kwargs) -> DiscoveredLink:
        """Save a discovered link"""
        link = DiscoveredLink(**kwargs)
        self.session.add(link)
        await self.session.flush()
        return link
    
    async def save_links_batch(self, links_data: List[Dict[str, Any]]) -> int:
        """Save multiple discovered links in batch"""
        links = [DiscoveredLink(**data) for data in links_data]
        self.session.add_all(links)
        await self.session.flush()
        return len(links)
    
    async def get_next_links_to_crawl(self, job_id: str, limit: int = 100) -> List[DiscoveredLink]:
        """Get next links to crawl, ordered by priority"""
        result = await self.session.execute(
            select(DiscoveredLink)
            .where(and_(
                DiscoveredLink.job_id == job_id,
                DiscoveredLink.status == 'discovered'
            ))
            .order_by(DiscoveredLink.priority.asc(), DiscoveredLink.discovered_at.asc())
            .limit(limit)
        )
        return list(result.scalars().all())
    
    async def mark_links_as_queued(self, link_ids: List[str]) -> int:
        """Mark links as queued for crawling"""
        result = await self.session.execute(
            update(DiscoveredLink)
            .where(DiscoveredLink.id.in_(link_ids))
            .values(status='queued', queued_at=datetime.utcnow())
        )
        return result.rowcount

# Database Manager
class DatabaseManager:
    """Central database manager with connection pooling and migrations"""
    
    def __init__(self, database_url: str, echo: bool = False):
        self.database_url = database_url
        self.engine = create_async_engine(
            database_url,
            echo=echo,
            pool_size=20,
            max_overflow=30,
            pool_recycle=3600,
            pool_pre_ping=True
        )
        self.async_session = async_sessionmaker(
            self.engine, 
            expire_on_commit=False
        )
    
    @asynccontextmanager
    async def get_session(self) -> AsyncGenerator[AsyncSession, None]:
        """Get a database session with automatic cleanup"""
        async with self.async_session() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise
            finally:
                await session.close()
    
    async def create_tables(self):
        """Create all database tables"""
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Database tables created successfully")
    
    async def drop_tables(self):
        """Drop all database tables (use with caution)"""
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
        logger.info("Database tables dropped")
    
    async def close(self):
        """Close database connections"""
        await self.engine.dispose()
        logger.info("Database connections closed")
    
    # Repository factories
    def get_crawl_job_repository(self, session: AsyncSession) -> CrawlJobRepository:
        return CrawlJobRepository(session)
    
    def get_crawled_page_repository(self, session: AsyncSession) -> CrawledPageRepository:
        return CrawledPageRepository(session)
    
    def get_discovered_link_repository(self, session: AsyncSession) -> DiscoveredLinkRepository:
        return DiscoveredLinkRepository(session)

# Database Service Layer
class CrawlDatabaseService:
    """High-level database service for crawling operations"""
    
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
    
    async def create_crawl_job(self, 
                               name: str, 
                               start_urls: List[str],
                               config: Dict[str, Any] = None) -> str:
        """Create a new crawl job and return its ID"""
        
        config = config or {}
        
        async with self.db_manager.get_session() as session:
            repo = self.db_manager.get_crawl_job_repository(session)
            
            job = await repo.create_job(
                name=name,
                start_urls=start_urls,
                strategy=config.get('strategy', 'bfs'),
                max_pages=config.get('max_pages', 10000),
                max_depth=config.get('max_depth', 10),
                max_concurrent=config.get('max_concurrent', 20),
                delay_between_requests=config.get('delay_between_requests', 1.0),
                respect_robots_txt=config.get('respect_robots_txt', True),
                follow_external_links=config.get('follow_external_links', False),
                allowed_domains=config.get('allowed_domains'),
                blocked_domains=config.get('blocked_domains'),
                url_patterns=config.get('url_patterns')
            )
            
            await session.commit()
            logger.info(f"Created crawl job: {job.id} - {name}")
            return str(job.id)
    
    async def start_crawl_job(self, job_id: str) -> bool:
        """Mark a crawl job as started"""
        async with self.db_manager.get_session() as session:
            repo = self.db_manager.get_crawl_job_repository(session)
            
            success = await repo.update_job_status(
                job_id, 
                'running',
                started_at=datetime.utcnow()
            )
            
            if success:
                logger.info(f"Started crawl job: {job_id}")
            
            return success
    
    async def complete_crawl_job(self, job_id: str, stats: Dict[str, Any] = None) -> bool:
        """Mark a crawl job as completed with final statistics"""
        async with self.db_manager.get_session() as session:
            repo = self.db_manager.get_crawl_job_repository(session)
            
            update_data = {
                'status': 'completed',
                'completed_at': datetime.utcnow()
            }
            
            if stats:
                update_data.update({
                    'total_crawled': stats.get('total_crawled', 0),
                    'total_failed': stats.get('total_failed', 0), 
                    'total_discovered': stats.get('total_discovered', 0),
                    'pages_per_second': stats.get('pages_per_second', 0.0)
                })
            
            success = await repo.update_job_status(job_id, 'completed', **update_data)
            
            if success:
                logger.info(f"Completed crawl job: {job_id}")
            
            return success
    
    async def save_crawled_page(self, 
                                job_id: str,
                                url: str,
                                html_content: str,
                                extracted_data: Dict[str, Any] = None,
                                metadata: Dict[str, Any] = None) -> str:
        """Save a crawled page to the database"""
        
        async with self.db_manager.get_session() as session:
            repo = self.db_manager.get_crawled_page_repository(session)
            
            page = await repo.save_page(
                job_id=job_id,
                url=url,
                html_content=html_content,
                extracted_data=extracted_data or {},
                metadata=metadata or {},
                status_code=200,  # Default success
                crawled_at=datetime.utcnow()
            )
            
            await session.commit()
            return str(page.id)
    
    async def get_job_statistics(self, job_id: str) -> Dict[str, Any]:
        """Get comprehensive statistics for a crawl job"""
        
        async with self.db_manager.get_session() as session:
            job_repo = self.db_manager.get_crawl_job_repository(session)
            page_repo = self.db_manager.get_crawled_page_repository(session)
            link_repo = self.db_manager.get_discovered_link_repository(session)
            
            # Get job info
            job = await job_repo.get_job_by_id(job_id)
            if not job:
                return {}
            
            # Get page count
            total_pages = await page_repo.get_page_count_by_job(job_id)
            
            # Get pages by status code
            success_pages = await page_repo.get_pages_by_status_code(job_id, 200)
            
            # Calculate runtime
            runtime_seconds = 0
            if job.started_at:
                end_time = job.completed_at or datetime.utcnow()
                runtime_seconds = (end_time - job.started_at).total_seconds()
            
            return {
                'job_id': str(job.id),
                'name': job.name,
                'status': job.status,
                'strategy': job.strategy,
                'total_pages_crawled': total_pages,
                'successful_pages': len(success_pages),
                'runtime_seconds': runtime_seconds,
                'pages_per_second': job.pages_per_second,
                'start_urls': job.start_urls,
                'created_at': job.created_at.isoformat(),
                'started_at': job.started_at.isoformat() if job.started_at else None,
                'completed_at': job.completed_at.isoformat() if job.completed_at else None
            }

# Convenience functions
async def create_database_manager(database_url: str) -> DatabaseManager:
    """Create and initialize a database manager"""
    manager = DatabaseManager(database_url)
    await manager.create_tables()
    return manager

async def create_crawl_service(database_url: str) -> CrawlDatabaseService:
    """Create a complete crawl database service"""
    manager = await create_database_manager(database_url)
    return CrawlDatabaseService(manager)
