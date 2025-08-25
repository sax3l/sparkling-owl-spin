"""
Scraper router for managing data extraction operations.
"""
from typing import List, Optional, Dict, Any, Union
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks, UploadFile, File
from fastapi.responses import JSONResponse, FileResponse
from pydantic import BaseModel, HttpUrl, Field, validator
from sqlalchemy.orm import Session
from enum import Enum
import json
import yaml
import asyncio

from ..deps import (
    get_database,
    get_current_active_user,
    get_admin_user,
    RateLimiter
)

router = APIRouter()

# Enums
class ScrapeStatus(str, Enum):
    """Scrape status enumeration."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    RETRYING = "retrying"

class ScrapeType(str, Enum):
    """Scrape type enumeration."""
    SINGLE_URL = "single_url"
    BATCH_URLS = "batch_urls"
    TEMPLATE_BASED = "template_based"
    FORM_FLOW = "form_flow"

class DataFormat(str, Enum):
    """Data extraction format."""
    JSON = "json"
    CSV = "csv"
    XML = "xml"
    YAML = "yaml"

class BrowserType(str, Enum):
    """Browser type for scraping."""
    CHROME = "chrome"
    FIREFOX = "firefox"
    EDGE = "edge"
    PLAYWRIGHT = "playwright"

# Pydantic models
class ScrapeConfig(BaseModel):
    """Scrape configuration model."""
    browser_type: BrowserType = BrowserType.CHROME
    headless: bool = True
    javascript_enabled: bool = True
    wait_for_load: float = Field(default=3.0, ge=0.1, le=60.0)
    screenshot: bool = False
    full_page_screenshot: bool = False
    custom_headers: Optional[Dict[str, str]] = Field(default_factory=dict)
    cookies: Optional[Dict[str, str]] = Field(default_factory=dict)
    user_agent: Optional[str] = None
    viewport_width: int = Field(default=1920, ge=320, le=4096)
    viewport_height: int = Field(default=1080, ge=240, le=4096)
    timeout: int = Field(default=30, ge=5, le=300)
    retry_count: int = Field(default=3, ge=0, le=10)
    retry_delay: float = Field(default=5.0, ge=1.0, le=60.0)
    proxy_enabled: bool = False
    anti_bot_enabled: bool = True

class ExtractionRule(BaseModel):
    """Data extraction rule model."""
    name: str = Field(max_length=100)
    selector: str = Field(max_length=1000)
    attribute: Optional[str] = Field(default="text", max_length=50)
    transform: Optional[str] = Field(default=None, max_length=100)
    required: bool = True
    multiple: bool = False
    default_value: Optional[str] = None

class ScrapeTemplate(BaseModel):
    """Scrape template model."""
    name: str = Field(max_length=255)
    description: Optional[str] = Field(default=None, max_length=1000)
    url_pattern: str = Field(max_length=500)
    extraction_rules: List[ExtractionRule] = Field(min_items=1)
    pagination_selector: Optional[str] = None
    max_pages: int = Field(default=1, ge=1, le=100)
    tags: Optional[List[str]] = Field(default_factory=list)

class ScrapeRequest(BaseModel):
    """Scrape request model."""
    name: str = Field(max_length=255)
    urls: List[HttpUrl] = Field(min_items=1, max_items=1000)
    scrape_type: ScrapeType = ScrapeType.SINGLE_URL
    template_id: Optional[int] = None
    template_content: Optional[ScrapeTemplate] = None
    config: ScrapeConfig = Field(default_factory=ScrapeConfig)
    output_format: DataFormat = DataFormat.JSON
    scheduled_at: Optional[datetime] = None
    callback_url: Optional[HttpUrl] = None
    tags: Optional[List[str]] = Field(default_factory=list)

class ScrapeUpdate(BaseModel):
    """Scrape update model."""
    name: Optional[str] = Field(default=None, max_length=255)
    config: Optional[ScrapeConfig] = None
    scheduled_at: Optional[datetime] = None
    callback_url: Optional[HttpUrl] = None

class ScrapeResponse(BaseModel):
    """Scrape response model."""
    id: int
    name: str
    urls: List[str]
    scrape_type: str
    status: str
    config: Dict[str, Any]
    output_format: str
    created_at: datetime
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    urls_processed: int
    urls_successful: int
    urls_failed: int
    data_extracted_count: int
    error_message: Optional[str]
    result_file_url: Optional[str]
    tags: List[str]

class ExtractedData(BaseModel):
    """Extracted data model."""
    id: int
    scrape_id: int
    url: str
    extracted_at: datetime
    data: Dict[str, Any]
    screenshot_url: Optional[str]
    page_title: Optional[str]
    processing_time: float

class TemplateResponse(BaseModel):
    """Template response model."""
    id: int
    name: str
    description: Optional[str]
    url_pattern: str
    extraction_rules: List[Dict[str, Any]]
    created_at: datetime
    updated_at: Optional[datetime]
    usage_count: int
    tags: List[str]

# Services
class ScraperService:
    """Scraper management service."""
    
    def __init__(self, db: Session):
        self.db = db
    
    async def create_scrape(self, user_id: int, scrape_request: ScrapeRequest) -> "ScrapeJob":
        """Create a new scrape job."""
        # Convert URLs to strings
        urls = [str(url) for url in scrape_request.urls]
        
        # Validate template if provided
        if scrape_request.template_id:
            template = self.db.query(ScrapeTemplateModel).filter(
                ScrapeTemplateModel.id == scrape_request.template_id,
                ScrapeTemplateModel.user_id == user_id
            ).first()
            
            if not template:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Template not found"
                )
        
        # Create scrape job
        scrape_job = ScrapeJob(
            user_id=user_id,
            name=scrape_request.name,
            urls=urls,
            scrape_type=scrape_request.scrape_type,
            template_id=scrape_request.template_id,
            template_content=scrape_request.template_content.dict() if scrape_request.template_content else None,
            config=scrape_request.config.dict(),
            output_format=scrape_request.output_format,
            status=ScrapeStatus.PENDING,
            scheduled_at=scrape_request.scheduled_at,
            callback_url=str(scrape_request.callback_url) if scrape_request.callback_url else None,
            tags=scrape_request.tags or [],
            created_at=datetime.utcnow()
        )
        
        self.db.add(scrape_job)
        self.db.commit()
        self.db.refresh(scrape_job)
        
        # Schedule scrape if not scheduled for later
        if not scrape_request.scheduled_at or scrape_request.scheduled_at <= datetime.utcnow():
            await self._schedule_scrape(scrape_job)
        
        return scrape_job
    
    async def start_scrape(self, scrape_id: int, user_id: int) -> "ScrapeJob":
        """Start a scrape job."""
        scrape_job = self.db.query(ScrapeJob).filter(
            ScrapeJob.id == scrape_id,
            ScrapeJob.user_id == user_id
        ).first()
        
        if not scrape_job:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Scrape job not found"
            )
        
        if scrape_job.status != ScrapeStatus.PENDING:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot start scrape in {scrape_job.status} status"
            )
        
        # Update status and start scraping
        scrape_job.status = ScrapeStatus.RUNNING
        scrape_job.started_at = datetime.utcnow()
        self.db.commit()
        
        # Start actual scraping process
        await self._schedule_scrape(scrape_job)
        
        return scrape_job
    
    async def cancel_scrape(self, scrape_id: int, user_id: int) -> "ScrapeJob":
        """Cancel a scrape job."""
        scrape_job = self.db.query(ScrapeJob).filter(
            ScrapeJob.id == scrape_id,
            ScrapeJob.user_id == user_id
        ).first()
        
        if not scrape_job:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Scrape job not found"
            )
        
        if scrape_job.status in [ScrapeStatus.COMPLETED, ScrapeStatus.CANCELLED]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Scrape is already finished"
            )
        
        scrape_job.status = ScrapeStatus.CANCELLED
        scrape_job.completed_at = datetime.utcnow()
        self.db.commit()
        
        # Signal scraper to stop
        await self._signal_scraper(scrape_id, "cancel")
        
        return scrape_job
    
    def get_scrape_results(
        self, 
        scrape_id: int, 
        user_id: int, 
        skip: int = 0, 
        limit: int = 100
    ) -> List["ExtractedDataRecord"]:
        """Get scrape results."""
        # Verify ownership
        scrape_job = self.db.query(ScrapeJob).filter(
            ScrapeJob.id == scrape_id,
            ScrapeJob.user_id == user_id
        ).first()
        
        if not scrape_job:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Scrape job not found"
            )
        
        return self.db.query(ExtractedDataRecord).filter(
            ExtractedDataRecord.scrape_id == scrape_id
        ).offset(skip).limit(limit).all()
    
    def create_template(self, user_id: int, template: ScrapeTemplate) -> "ScrapeTemplateModel":
        """Create a scrape template."""
        template_model = ScrapeTemplateModel(
            user_id=user_id,
            name=template.name,
            description=template.description,
            url_pattern=template.url_pattern,
            extraction_rules=[rule.dict() for rule in template.extraction_rules],
            pagination_selector=template.pagination_selector,
            max_pages=template.max_pages,
            tags=template.tags or [],
            created_at=datetime.utcnow()
        )
        
        self.db.add(template_model)
        self.db.commit()
        self.db.refresh(template_model)
        
        return template_model
    
    def get_user_templates(
        self, 
        user_id: int, 
        skip: int = 0, 
        limit: int = 100
    ) -> List["ScrapeTemplateModel"]:
        """Get user's scrape templates."""
        return self.db.query(ScrapeTemplateModel).filter(
            ScrapeTemplateModel.user_id == user_id
        ).offset(skip).limit(limit).all()
    
    def validate_template(self, template: ScrapeTemplate) -> Dict[str, Any]:
        """Validate scrape template."""
        # Validate selectors
        validation_results = {
            "valid": True,
            "warnings": [],
            "errors": []
        }
        
        for rule in template.extraction_rules:
            # Basic CSS selector validation
            if not rule.selector.strip():
                validation_results["errors"].append(f"Empty selector for rule '{rule.name}'")
                validation_results["valid"] = False
            
            # Check for potentially problematic selectors
            if rule.selector.startswith("//"):
                validation_results["warnings"].append(f"XPath selector detected for rule '{rule.name}' - consider CSS selectors")
            
            # Validate attribute
            if rule.attribute and rule.attribute not in ["text", "href", "src", "value", "data-*", "class", "id"]:
                validation_results["warnings"].append(f"Uncommon attribute '{rule.attribute}' for rule '{rule.name}'")
        
        return validation_results
    
    async def _schedule_scrape(self, scrape_job: "ScrapeJob"):
        """Schedule scrape job for execution."""
        # This would integrate with your task queue
        from ..scraper.manager import ScraperManager
        
        scraper_manager = ScraperManager()
        await scraper_manager.schedule_scrape(scrape_job)
    
    async def _signal_scraper(self, scrape_id: int, signal: str):
        """Send signal to running scraper."""
        # This would send signals through Redis/message queue
        pass

scraper_service_instance = None

def get_scraper_service(db: Session = Depends(get_database)) -> ScraperService:
    """Get scraper service instance."""
    global scraper_service_instance
    if not scraper_service_instance:
        scraper_service_instance = ScraperService(db)
    return scraper_service_instance

# Routes
@router.post("/", response_model=ScrapeResponse, status_code=status.HTTP_201_CREATED)
async def create_scrape(
    scrape_request: ScrapeRequest,
    background_tasks: BackgroundTasks,
    current_user = Depends(get_current_active_user),
    scraper_service: ScraperService = Depends(get_scraper_service),
    rate_limit: dict = Depends(RateLimiter("50/hour"))
):
    """Create a new scrape job."""
    scrape_job = await scraper_service.create_scrape(current_user.id, scrape_request)
    return ScrapeResponse.from_orm(scrape_job)

@router.get("/", response_model=List[ScrapeResponse])
async def list_scrapes(
    skip: int = 0,
    limit: int = 100,
    status: Optional[ScrapeStatus] = None,
    current_user = Depends(get_current_active_user),
    db: Session = Depends(get_database)
):
    """List user's scrape jobs."""
    query = db.query(ScrapeJob).filter(ScrapeJob.user_id == current_user.id)
    
    if status:
        query = query.filter(ScrapeJob.status == status)
    
    scrapes = query.order_by(ScrapeJob.created_at.desc()).offset(skip).limit(limit).all()
    return [ScrapeResponse.from_orm(scrape) for scrape in scrapes]

@router.get("/{scrape_id}", response_model=ScrapeResponse)
async def get_scrape(
    scrape_id: int,
    current_user = Depends(get_current_active_user),
    db: Session = Depends(get_database)
):
    """Get a specific scrape job."""
    scrape_job = db.query(ScrapeJob).filter(
        ScrapeJob.id == scrape_id,
        ScrapeJob.user_id == current_user.id
    ).first()
    
    if not scrape_job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Scrape job not found"
        )
    
    return ScrapeResponse.from_orm(scrape_job)

@router.post("/{scrape_id}/start", response_model=ScrapeResponse)
async def start_scrape(
    scrape_id: int,
    current_user = Depends(get_current_active_user),
    scraper_service: ScraperService = Depends(get_scraper_service)
):
    """Start a scrape job."""
    scrape_job = await scraper_service.start_scrape(scrape_id, current_user.id)
    return ScrapeResponse.from_orm(scrape_job)

@router.post("/{scrape_id}/cancel", response_model=ScrapeResponse)
async def cancel_scrape(
    scrape_id: int,
    current_user = Depends(get_current_active_user),
    scraper_service: ScraperService = Depends(get_scraper_service)
):
    """Cancel a scrape job."""
    scrape_job = await scraper_service.cancel_scrape(scrape_id, current_user.id)
    return ScrapeResponse.from_orm(scrape_job)

@router.get("/{scrape_id}/results", response_model=List[ExtractedData])
async def get_scrape_results(
    scrape_id: int,
    skip: int = 0,
    limit: int = 100,
    current_user = Depends(get_current_active_user),
    scraper_service: ScraperService = Depends(get_scraper_service)
):
    """Get scrape results."""
    results = scraper_service.get_scrape_results(scrape_id, current_user.id, skip, limit)
    return [ExtractedData.from_orm(result) for result in results]

@router.get("/{scrape_id}/download")
async def download_scrape_results(
    scrape_id: int,
    format: DataFormat = DataFormat.JSON,
    current_user = Depends(get_current_active_user),
    db: Session = Depends(get_database)
):
    """Download scrape results in specified format."""
    # Verify ownership
    scrape_job = db.query(ScrapeJob).filter(
        ScrapeJob.id == scrape_id,
        ScrapeJob.user_id == current_user.id
    ).first()
    
    if not scrape_job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Scrape job not found"
        )
    
    # Get results
    results = db.query(ExtractedDataRecord).filter(
        ExtractedDataRecord.scrape_id == scrape_id
    ).all()
    
    if not results:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No results found"
        )
    
    # Format data
    data = [result.data for result in results]
    
    if format == DataFormat.JSON:
        import tempfile
        import json
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(data, f, indent=2, default=str)
            temp_file = f.name
        
        return FileResponse(
            temp_file,
            filename=f"scrape_{scrape_id}_results.json",
            media_type="application/json"
        )
    
    elif format == DataFormat.CSV:
        import tempfile
        import pandas as pd
        
        # Flatten nested data
        flattened_data = []
        for item in data:
            flat_item = {}
            for key, value in item.items():
                if isinstance(value, (dict, list)):
                    flat_item[key] = json.dumps(value)
                else:
                    flat_item[key] = value
            flattened_data.append(flat_item)
        
        df = pd.DataFrame(flattened_data)
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            df.to_csv(f.name, index=False)
            temp_file = f.name
        
        return FileResponse(
            temp_file,
            filename=f"scrape_{scrape_id}_results.csv",
            media_type="text/csv"
        )
    
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported format: {format}"
        )

# Template management
@router.post("/templates", response_model=TemplateResponse, status_code=status.HTTP_201_CREATED)
async def create_template(
    template: ScrapeTemplate,
    current_user = Depends(get_current_active_user),
    scraper_service: ScraperService = Depends(get_scraper_service)
):
    """Create a scrape template."""
    template_model = scraper_service.create_template(current_user.id, template)
    return TemplateResponse.from_orm(template_model)

@router.get("/templates", response_model=List[TemplateResponse])
async def list_templates(
    skip: int = 0,
    limit: int = 100,
    current_user = Depends(get_current_active_user),
    scraper_service: ScraperService = Depends(get_scraper_service)
):
    """List user's scrape templates."""
    templates = scraper_service.get_user_templates(current_user.id, skip, limit)
    return [TemplateResponse.from_orm(template) for template in templates]

@router.get("/templates/{template_id}", response_model=TemplateResponse)
async def get_template(
    template_id: int,
    current_user = Depends(get_current_active_user),
    db: Session = Depends(get_database)
):
    """Get a specific template."""
    template = db.query(ScrapeTemplateModel).filter(
        ScrapeTemplateModel.id == template_id,
        ScrapeTemplateModel.user_id == current_user.id
    ).first()
    
    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Template not found"
        )
    
    return TemplateResponse.from_orm(template)

@router.post("/templates/validate")
async def validate_template(
    template: ScrapeTemplate,
    current_user = Depends(get_current_active_user),
    scraper_service: ScraperService = Depends(get_scraper_service)
):
    """Validate a scrape template."""
    validation_result = scraper_service.validate_template(template)
    return validation_result

@router.post("/templates/import")
async def import_template(
    file: UploadFile = File(...),
    current_user = Depends(get_current_active_user),
    scraper_service: ScraperService = Depends(get_scraper_service)
):
    """Import template from YAML/JSON file."""
    content = await file.read()
    
    try:
        if file.filename.endswith('.yaml') or file.filename.endswith('.yml'):
            template_data = yaml.safe_load(content)
        else:
            template_data = json.loads(content)
        
        template = ScrapeTemplate(**template_data)
        template_model = scraper_service.create_template(current_user.id, template)
        
        return TemplateResponse.from_orm(template_model)
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid template file: {str(e)}"
        )

# Quick scrape endpoint
@router.post("/quick", response_model=ExtractedData)
async def quick_scrape(
    url: HttpUrl,
    selectors: Dict[str, str],
    config: Optional[ScrapeConfig] = None,
    current_user = Depends(get_current_active_user),
    rate_limit: dict = Depends(RateLimiter("10/minute"))
):
    """Quick scrape of a single URL with simple selectors."""
    if len(selectors) > 20:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Too many selectors (max 20)"
        )
    
    # Create temporary template
    extraction_rules = [
        ExtractionRule(name=name, selector=selector)
        for name, selector in selectors.items()
    ]
    
    template = ScrapeTemplate(
        name="Quick Scrape",
        url_pattern=str(url),
        extraction_rules=extraction_rules
    )
    
    # Create quick scrape request
    scrape_request = ScrapeRequest(
        name=f"Quick scrape: {url}",
        urls=[url],
        scrape_type=ScrapeType.SINGLE_URL,
        template_content=template,
        config=config or ScrapeConfig()
    )
    
    scraper_service = get_scraper_service()
    scrape_job = await scraper_service.create_scrape(current_user.id, scrape_request)
    
    # Wait for completion (for quick scrapes only)
    timeout = 60  # 1 minute timeout
    start_time = datetime.utcnow()
    
    while (datetime.utcnow() - start_time).total_seconds() < timeout:
        await asyncio.sleep(1)
        
        db = next(get_database())
        updated_job = db.query(ScrapeJob).filter(ScrapeJob.id == scrape_job.id).first()
        
        if updated_job.status == ScrapeStatus.COMPLETED:
            results = db.query(ExtractedDataRecord).filter(
                ExtractedDataRecord.scrape_id == scrape_job.id
            ).first()
            
            if results:
                return ExtractedData.from_orm(results)
            break
        
        elif updated_job.status in [ScrapeStatus.FAILED, ScrapeStatus.CANCELLED]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Scrape failed: {updated_job.error_message}"
            )
    
    raise HTTPException(
        status_code=status.HTTP_408_REQUEST_TIMEOUT,
        detail="Scrape timeout - check job status later"
    )

# Health check
@router.get("/health")
async def scraper_health_check():
    """Health check for scraper service."""
    return {
        "status": "healthy",
        "service": "scraper",
        "timestamp": datetime.utcnow().isoformat()
    }
