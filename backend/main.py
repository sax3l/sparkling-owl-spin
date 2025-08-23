"""
Main FastAPI server integrating all crawler components
"""
from fastapi import FastAPI, WebSocket, HTTPException, BackgroundTasks, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from typing import Dict, List, Optional, Any
from datetime import datetime
import asyncio
import json
import logging
import uuid

# Import our core modules
from core.scheduler import SchedulerService, CrawlJob, JobStatus, JobPriority
from core.proxy_manager import ProxyPool, Proxy, AntiBotService
from core.crawler_engine import CrawlerEngine, CrawlTemplate, TemplateWizard, ExtractionRule
from core.data_processor import DataProcessor, DataExporter, ExportConfig, ExportFormat
from core.monitoring import CrawlMonitor, RealTimeNotifier, Alert, AlertLevel

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize core services
scheduler = SchedulerService()
proxy_pool = ProxyPool()
anti_bot = AntiBotService()
crawler_engine = CrawlerEngine()
template_wizard = TemplateWizard()
data_processor = DataProcessor()
data_exporter = DataExporter()
crawl_monitor = CrawlMonitor()
notifier = RealTimeNotifier()

# FastAPI app
app = FastAPI(
    title="Advanced Web Scraping Platform",
    description="Enterprise-grade web scraping with AI-powered extraction",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer()

# Pydantic models
class JobCreateRequest(BaseModel):
    name: str
    template_id: str
    target_urls: List[str]
    schedule_config: Dict[str, Any] = {}
    proxy_config: Dict[str, Any] = {}
    priority: str = "normal"

class TemplateCreateRequest(BaseModel):
    name: str
    description: str
    target_patterns: List[str]
    extraction_rules: List[Dict[str, Any]]
    crawl_strategy: str = "smart_crawl"

class ProxyAddRequest(BaseModel):
    host: str
    port: int
    username: Optional[str] = None
    password: Optional[str] = None
    proxy_type: str = "http"
    location: Optional[str] = None

class ExportRequest(BaseModel):
    job_id: str
    format: str
    destination: Optional[str] = None
    compression: Optional[str] = None
    filter_rules: List[Dict] = []

# Authentication dependency
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Simple token validation - replace with proper auth"""
    # For demo purposes, accept any token
    return {"user_id": "demo_user"}

# WebSocket endpoint for real-time updates
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    await notifier.subscribe_websocket(websocket)
    
    try:
        while True:
            # Keep connection alive
            await asyncio.sleep(30)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
    finally:
        await notifier.unsubscribe_websocket(websocket)

# Job management endpoints
@app.post("/api/jobs", response_model=Dict[str, str])
async def create_job(
    request: JobCreateRequest,
    background_tasks: BackgroundTasks,
    user: dict = Depends(get_current_user)
):
    """Create a new crawl job"""
    try:
        job = CrawlJob(
            id=str(uuid.uuid4()),
            name=request.name,
            template_id=request.template_id,
            target_urls=request.target_urls,
            selectors={},  # Will be populated from template
            proxy_config=request.proxy_config,
            schedule_config=request.schedule_config,
            priority=JobPriority[request.priority.upper()],
            created_at=datetime.now()
        )
        
        # Start monitoring
        await crawl_monitor.start_job_monitoring(job.id)
        
        # Submit job
        job_id = await scheduler.submit_job(job)
        
        # Start job execution in background
        background_tasks.add_task(execute_job_background, job_id)
        
        return {"job_id": job_id, "status": "submitted"}
    
    except Exception as e:
        logger.error(f"Failed to create job: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/jobs/{job_id}")
async def get_job_status(job_id: str, user: dict = Depends(get_current_user)):
    """Get job status and progress"""
    job = await scheduler.get_job_status(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    return {
        "id": job.id,
        "name": job.name,
        "status": job.status.value,
        "progress": job.progress,
        "results_count": job.results_count,
        "created_at": job.created_at.isoformat() if job.created_at else None,
        "error_message": job.error_message
    }

@app.get("/api/jobs")
async def list_jobs(user: dict = Depends(get_current_user)):
    """List all jobs with status"""
    stats = await scheduler.get_job_stats()
    return stats

@app.post("/api/jobs/{job_id}/cancel")
async def cancel_job(job_id: str, user: dict = Depends(get_current_user)):
    """Cancel a running job"""
    success = await scheduler.cancel_job(job_id)
    if success:
        crawl_monitor.complete_job_monitoring(job_id, success=False)
        return {"message": "Job cancelled successfully"}
    else:
        raise HTTPException(status_code=400, detail="Job cannot be cancelled")

# Template management endpoints
@app.post("/api/templates")
async def create_template(
    request: TemplateCreateRequest,
    user: dict = Depends(get_current_user)
):
    """Create a new crawl template"""
    try:
        # Convert request to template
        extraction_rules = []
        for rule_data in request.extraction_rules:
            rule = ExtractionRule(
                name=rule_data['name'],
                selector=rule_data['selector'],
                extraction_method=rule_data['extraction_method'],
                data_type=rule_data.get('data_type', 'text'),
                required=rule_data.get('required', True)
            )
            extraction_rules.append(rule)
        
        template = CrawlTemplate(
            id=str(uuid.uuid4()),
            name=request.name,
            description=request.description,
            target_patterns=request.target_patterns,
            extraction_rules=extraction_rules,
            pagination_config={},
            crawl_strategy=request.crawl_strategy,
            anti_bot_config={'enabled': True},
            validation_rules=[],
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        # Store template (implement persistence)
        return {"template_id": template.id, "message": "Template created successfully"}
    
    except Exception as e:
        logger.error(f"Failed to create template: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/templates/wizard")
async def create_template_with_wizard(
    example_url: str,
    sample_data: Dict[str, Any],
    user: dict = Depends(get_current_user)
):
    """Create template using AI wizard"""
    try:
        template = await template_wizard.create_template_from_example(example_url, sample_data)
        return {
            "template_id": template.id,
            "name": template.name,
            "extraction_rules": [
                {
                    "name": rule.name,
                    "selector": rule.selector,
                    "data_type": rule.data_type
                }
                for rule in template.extraction_rules
            ]
        }
    except Exception as e:
        logger.error(f"Template wizard failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Proxy management endpoints
@app.post("/api/proxies")
async def add_proxy(request: ProxyAddRequest, user: dict = Depends(get_current_user)):
    """Add a proxy to the pool"""
    try:
        proxy = Proxy(
            id=str(uuid.uuid4()),
            host=request.host,
            port=request.port,
            username=request.username,
            password=request.password,
            proxy_type=request.proxy_type,
            location=request.location
        )
        
        success = await proxy_pool.add_proxy(proxy)
        if success:
            return {"message": "Proxy added successfully", "proxy_id": proxy.id}
        else:
            return {"message": "Proxy added but failed initial test", "proxy_id": proxy.id}
    
    except Exception as e:
        logger.error(f"Failed to add proxy: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/proxies/stats")
async def get_proxy_stats(user: dict = Depends(get_current_user)):
    """Get proxy pool statistics"""
    return proxy_pool.get_stats()

@app.post("/api/proxies/health-check")
async def proxy_health_check(user: dict = Depends(get_current_user)):
    """Perform health check on all proxies"""
    await proxy_pool.health_check()
    return {"message": "Health check completed"}

# Data export endpoints
@app.post("/api/export")
async def export_data(request: ExportRequest, user: dict = Depends(get_current_user)):
    """Export crawl data in specified format"""
    try:
        # Get job results (implement data storage/retrieval)
        job_results = []  # Placeholder
        
        config = ExportConfig(
            format=ExportFormat[request.format.upper()],
            destination=request.destination,
            compression=request.compression,
            filter_rules=request.filter_rules
        )
        
        export_result = await data_exporter.export_data(job_results, config)
        return {"export_path": export_result, "message": "Export completed successfully"}
    
    except Exception as e:
        logger.error(f"Export failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Monitoring endpoints
@app.get("/api/monitoring/dashboard")
async def get_dashboard_data(user: dict = Depends(get_current_user)):
    """Get real-time dashboard data"""
    dashboard_data = crawl_monitor.get_dashboard_data()
    return dashboard_data

@app.get("/api/monitoring/health")
async def get_system_health():
    """Get system health status"""
    health_data = await crawl_monitor.monitor_system_health()
    return health_data

@app.get("/api/monitoring/alerts")
async def get_alerts(user: dict = Depends(get_current_user)):
    """Get recent alerts"""
    return [
        {
            "id": alert.id,
            "level": alert.level.value,
            "title": alert.title,
            "message": alert.message,
            "timestamp": alert.timestamp.isoformat(),
            "resolved": alert.resolved
        }
        for alert in crawl_monitor.alerts[-50:]  # Last 50 alerts
    ]

# Background task execution
async def execute_job_background(job_id: str):
    """Execute crawl job in background"""
    try:
        job = await scheduler.get_job_status(job_id)
        if not job:
            logger.error(f"Job {job_id} not found")
            return
        
        # Get template (implement template storage)
        template = None  # Placeholder
        
        if not template:
            logger.error(f"Template not found for job {job_id}")
            crawl_monitor.complete_job_monitoring(job_id, success=False)
            return
        
        # Execute crawl
        config = {
            'proxy_enabled': job.proxy_config.get('enabled', True),
            'rate_limit': job.proxy_config.get('rate_limit', 1.0),
            'anti_bot': True
        }
        
        results = await crawler_engine.execute_crawl(template, job.target_urls, config)
        
        # Update progress
        for i, result in enumerate(results):
            crawl_monitor.update_job_progress(
                job_id,
                pages_crawled=1 if result.success else 0,
                pages_failed=0 if result.success else 1,
                data_extracted=len(result.data)
            )
            
            # Update job progress
            progress = (i + 1) / len(job.target_urls)
            job.progress = progress
            job.results_count = sum(1 for r in results[:i+1] if r.success)
        
        # Process results
        processed_results = await data_processor.process_crawl_results(
            [result.data for result in results],
            {'validation_level': 'moderate'}
        )
        
        # Mark job as completed
        job.status = JobStatus.COMPLETED
        crawl_monitor.complete_job_monitoring(job_id, success=True)
        
        # Send notification
        await notifier.broadcast_update('job_completed', {
            'job_id': job_id,
            'results_count': len(processed_results),
            'success_rate': sum(1 for r in results if r.success) / len(results)
        })
        
        logger.info(f"Job {job_id} completed successfully")
    
    except Exception as e:
        logger.error(f"Job {job_id} failed: {e}")
        crawl_monitor.complete_job_monitoring(job_id, success=False)
        
        # Update job status
        job = await scheduler.get_job_status(job_id)
        if job:
            job.status = JobStatus.FAILED
            job.error_message = str(e)

# Health check endpoint
@app.get("/health")
async def health_check():
    """Basic health check"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    }

# Serve static files (for frontend)
app.mount("/static", StaticFiles(directory="static"), name="static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
