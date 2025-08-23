"""
Simplified FastAPI server for demo purposes
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, List, Optional, Any
from datetime import datetime
import asyncio
import json
import logging
import uuid

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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

# In-memory storage for demo
jobs = {}
templates = {}
proxies = {}

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

# Job management endpoints
@app.post("/api/jobs", response_model=Dict[str, str])
async def create_job(request: JobCreateRequest):
    """Create a new crawl job"""
    try:
        job_id = str(uuid.uuid4())
        job = {
            "id": job_id,
            "name": request.name,
            "template_id": request.template_id,
            "target_urls": request.target_urls,
            "status": "running",
            "progress": 0.0,
            "results_count": 0,
            "created_at": datetime.now().isoformat(),
            "error_message": None
        }
        
        jobs[job_id] = job
        
        # Simulate job progress
        asyncio.create_task(simulate_job_progress(job_id))
        
        return {"job_id": job_id, "status": "submitted"}
    
    except Exception as e:
        logger.error(f"Failed to create job: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/jobs/{job_id}")
async def get_job_status(job_id: str):
    """Get job status and progress"""
    job = jobs.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    return job

@app.get("/api/jobs")
async def list_jobs():
    """List all jobs with status"""
    return {
        "total_jobs": len(jobs),
        "by_status": {
            "running": len([j for j in jobs.values() if j["status"] == "running"]),
            "completed": len([j for j in jobs.values() if j["status"] == "completed"]),
            "failed": len([j for j in jobs.values() if j["status"] == "failed"])
        }
    }

@app.post("/api/jobs/{job_id}/cancel")
async def cancel_job(job_id: str):
    """Cancel a running job"""
    job = jobs.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    job["status"] = "cancelled"
    return {"message": "Job cancelled successfully"}

# Template management endpoints
@app.post("/api/templates")
async def create_template(request: TemplateCreateRequest):
    """Create a new crawl template"""
    try:
        template_id = str(uuid.uuid4())
        template = {
            "id": template_id,
            "name": request.name,
            "description": request.description,
            "target_patterns": request.target_patterns,
            "extraction_rules": request.extraction_rules,
            "created_at": datetime.now().isoformat()
        }
        
        templates[template_id] = template
        return {"template_id": template_id, "message": "Template created successfully"}
    
    except Exception as e:
        logger.error(f"Failed to create template: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/templates/wizard")
async def create_template_with_wizard(example_url: str, sample_data: Dict[str, Any]):
    """Create template using AI wizard"""
    try:
        template_id = str(uuid.uuid4())
        
        # Generate extraction rules from sample data
        extraction_rules = []
        for field_name, sample_value in sample_data.items():
            rule = {
                "name": field_name,
                "selector": f".{field_name}, #{field_name}",
                "extraction_method": "css_selector",
                "data_type": "text" if isinstance(sample_value, str) else "number",
                "required": True
            }
            extraction_rules.append(rule)
        
        template = {
            "id": template_id,
            "name": f"Auto-generated template for {example_url}",
            "description": "Template created using AI wizard",
            "target_patterns": [example_url],
            "extraction_rules": extraction_rules,
            "created_at": datetime.now().isoformat()
        }
        
        templates[template_id] = template
        
        return {
            "template_id": template_id,
            "name": template["name"],
            "extraction_rules": extraction_rules
        }
    except Exception as e:
        logger.error(f"Template wizard failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Proxy management endpoints
@app.post("/api/proxies")
async def add_proxy(request: ProxyAddRequest):
    """Add a proxy to the pool"""
    try:
        proxy_id = str(uuid.uuid4())
        proxy = {
            "id": proxy_id,
            "host": request.host,
            "port": request.port,
            "username": request.username,
            "password": request.password,
            "proxy_type": request.proxy_type,
            "location": request.location,
            "status": "active",
            "success_rate": 0.95,
            "response_time": 0.5
        }
        
        proxies[proxy_id] = proxy
        
        return {"message": "Proxy added successfully", "proxy_id": proxy_id}
    
    except Exception as e:
        logger.error(f"Failed to add proxy: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/proxies/stats")
async def get_proxy_stats():
    """Get proxy pool statistics"""
    active_proxies = len([p for p in proxies.values() if p["status"] == "active"])
    return {
        "total_proxies": len(proxies),
        "by_status": {
            "active": active_proxies,
            "inactive": len(proxies) - active_proxies
        },
        "avg_success_rate": 0.95,
        "avg_response_time": 0.5
    }

# Monitoring endpoints
@app.get("/api/monitoring/dashboard")
async def get_dashboard_data():
    """Get real-time dashboard data"""
    import psutil
    
    active_jobs_dict = {
        job_id: {
            "id": job_id,
            "name": job["name"],
            "status": job["status"],
            "progress": job["progress"],
            "runtime": (datetime.now() - datetime.fromisoformat(job["created_at"])).total_seconds(),
            "success_rate": 0.95
        }
        for job_id, job in jobs.items()
        if job["status"] in ["running", "pending"]
    }
    
    return {
        "active_jobs": active_jobs_dict,
        "system_metrics": {
            "cpu_usage": psutil.cpu_percent() if 'psutil' in globals() else 45.0,
            "memory_usage": psutil.virtual_memory().percent if 'psutil' in globals() else 60.0,
            "disk_usage": psutil.disk_usage('/').percent if 'psutil' in globals() else 25.0,
            "active_jobs_count": len(active_jobs_dict)
        },
        "performance_metrics": {},
        "recent_alerts": [],
        "timestamp": datetime.now().isoformat()
    }

@app.get("/api/monitoring/health")
async def get_system_health():
    """Get system health status"""
    return {
        "status": "healthy",
        "cpu_usage": 45.0,
        "memory_usage": 60.0,
        "disk_usage": 25.0,
        "timestamp": datetime.now().isoformat()
    }

@app.get("/api/monitoring/alerts")
async def get_alerts():
    """Get recent alerts"""
    return []

# Data export endpoint
@app.post("/api/export")
async def export_data(job_id: str, format: str = "json"):
    """Export crawl data in specified format"""
    job = jobs.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    # Mock export data
    export_data = {
        "job_id": job_id,
        "exported_at": datetime.now().isoformat(),
        "format": format,
        "data": [
            {"title": "Sample Data 1", "price": "$99.99", "url": "https://example.com/1"},
            {"title": "Sample Data 2", "price": "$149.99", "url": "https://example.com/2"}
        ]
    }
    
    return {"export_path": f"/exports/{job_id}.{format}", "data": export_data}

# Health check endpoint
@app.get("/health")
async def health_check():
    """Basic health check"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    }

# Simulate job progress for demo
async def simulate_job_progress(job_id: str):
    """Simulate job progress for demonstration"""
    job = jobs.get(job_id)
    if not job:
        return
    
    for progress in range(0, 101, 10):
        if job["status"] == "cancelled":
            break
        
        job["progress"] = progress
        job["results_count"] = progress * 2
        
        if progress == 100:
            job["status"] = "completed"
        
        await asyncio.sleep(2)  # Update every 2 seconds

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
