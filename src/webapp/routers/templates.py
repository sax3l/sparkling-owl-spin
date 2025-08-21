"""
Router for template management operations.
"""

import yaml
from datetime import datetime
from typing import Dict, List, Optional, Any
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File, BackgroundTasks
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field, validator

from ..database import get_db
from ..models import User, ScrapeJob
from ..schemas.common import StatusResponse, PaginatedResponse
from ..dependencies import get_current_user, require_permissions
from ..services.template_service import TemplateService
from ..utils.rate_limiting import rate_limit
from ..utils.validation import validate_template

router = APIRouter(prefix="/templates", tags=["templates"])


class TemplateCreate(BaseModel):
    """Schema for creating templates."""
    name: str = Field(..., min_length=1, max_length=100, description="Template name")
    description: str = Field(..., max_length=500, description="Template description")
    version: str = Field("1.0", description="Template version")
    category: str = Field(..., description="Template category")
    selectors: Dict[str, Any] = Field(..., description="CSS/XPath selectors")
    transformations: Optional[Dict[str, Any]] = Field(None, description="Data transformations")
    validation_rules: Optional[Dict[str, Any]] = Field(None, description="Validation rules")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")
    is_public: bool = Field(False, description="Make template public")
    
    @validator('name')
    def validate_name(cls, v):
        # Ensure template name is valid for file system
        import re
        if not re.match(r'^[a-zA-Z0-9_-]+$', v):
            raise ValueError('Template name can only contain letters, numbers, hyphens, and underscores')
        return v


class TemplateUpdate(BaseModel):
    """Schema for updating templates."""
    description: Optional[str] = Field(None, max_length=500, description="Template description")
    selectors: Optional[Dict[str, Any]] = Field(None, description="CSS/XPath selectors")
    transformations: Optional[Dict[str, Any]] = Field(None, description="Data transformations")
    validation_rules: Optional[Dict[str, Any]] = Field(None, description="Validation rules")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")
    is_public: Optional[bool] = Field(None, description="Make template public")
    is_active: Optional[bool] = Field(None, description="Template active status")


class TemplateTest(BaseModel):
    """Schema for testing templates."""
    template_name: str = Field(..., description="Template to test")
    test_urls: List[str] = Field(..., min_items=1, max_items=10, description="URLs to test")
    timeout_seconds: int = Field(30, ge=5, le=300, description="Test timeout")


class TemplateValidation(BaseModel):
    """Schema for template validation results."""
    is_valid: bool = Field(..., description="Whether template is valid")
    errors: List[str] = Field(default_factory=list, description="Validation errors")
    warnings: List[str] = Field(default_factory=list, description="Validation warnings")
    score: float = Field(..., description="Quality score (0.0 to 1.0)")


@router.get("/", response_model=PaginatedResponse)
async def list_templates(
    category: Optional[str] = Query(None, description="Filter by category"),
    public_only: bool = Query(False, description="Show only public templates"),
    search: Optional[str] = Query(None, description="Search templates"),
    limit: int = Query(50, le=100, description="Number of templates"),
    offset: int = Query(0, ge=0, description="Offset"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List available templates."""
    
    template_service = TemplateService()
    
    templates = await template_service.list_templates(
        user_id=str(current_user.id) if not public_only else None,
        category=category,
        search=search,
        public_only=public_only,
        limit=limit,
        offset=offset
    )
    
    total = await template_service.count_templates(
        user_id=str(current_user.id) if not public_only else None,
        category=category,
        search=search,
        public_only=public_only
    )
    
    return PaginatedResponse(
        items=templates,
        total=total,
        page=offset // limit + 1,
        size=limit,
        pages=(total + limit - 1) // limit,
        has_next=offset + limit < total,
        has_prev=offset > 0
    )


@router.post("/", response_model=StatusResponse)
@rate_limit(requests=10, window=3600)  # 10 template creations per hour
async def create_template(
    template: TemplateCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new scraping template."""
    
    template_service = TemplateService()
    
    # Check if template name already exists for user
    existing = await template_service.get_template(
        template.name,
        str(current_user.id)
    )
    
    if existing:
        raise HTTPException(
            status_code=409,
            detail="Template with this name already exists"
        )
    
    # Validate template structure
    validation_result = await template_service.validate_template(template.dict())
    
    if not validation_result.is_valid:
        raise HTTPException(
            status_code=400,
            detail=f"Template validation failed: {', '.join(validation_result.errors)}"
        )
    
    # Create template
    created_template = await template_service.create_template(
        user_id=str(current_user.id),
        template_data=template.dict()
    )
    
    return StatusResponse(
        success=True,
        message="Template created successfully",
        data={"template_id": created_template.id, "name": created_template.name}
    )


@router.get("/{template_name}")
async def get_template(
    template_name: str,
    version: str = Query("latest", description="Template version"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific template."""
    
    template_service = TemplateService()
    template = await template_service.get_template(
        template_name,
        str(current_user.id),
        version=version
    )
    
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    
    return template


@router.put("/{template_name}", response_model=StatusResponse)
async def update_template(
    template_name: str,
    updates: TemplateUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update an existing template."""
    
    template_service = TemplateService()
    
    # Check if template exists and user owns it
    existing = await template_service.get_template(
        template_name,
        str(current_user.id)
    )
    
    if not existing:
        raise HTTPException(status_code=404, detail="Template not found")
    
    if existing.user_id != str(current_user.id):
        raise HTTPException(status_code=403, detail="Not authorized to update this template")
    
    # Validate updated template if selectors changed
    if updates.selectors:
        update_dict = updates.dict(exclude_unset=True)
        merged_template = {**existing.to_dict(), **update_dict}
        
        validation_result = await template_service.validate_template(merged_template)
        if not validation_result.is_valid:
            raise HTTPException(
                status_code=400,
                detail=f"Template validation failed: {', '.join(validation_result.errors)}"
            )
    
    # Update template
    success = await template_service.update_template(
        template_name,
        str(current_user.id),
        updates.dict(exclude_unset=True)
    )
    
    if not success:
        raise HTTPException(status_code=500, detail="Failed to update template")
    
    return StatusResponse(
        success=True,
        message="Template updated successfully"
    )


@router.delete("/{template_name}", response_model=StatusResponse)
async def delete_template(
    template_name: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a template."""
    
    template_service = TemplateService()
    
    # Check if template exists and user owns it
    existing = await template_service.get_template(
        template_name,
        str(current_user.id)
    )
    
    if not existing:
        raise HTTPException(status_code=404, detail="Template not found")
    
    if existing.user_id != str(current_user.id):
        raise HTTPException(status_code=403, detail="Not authorized to delete this template")
    
    # Check if template is being used by active jobs
    active_jobs = db.query(ScrapeJob).filter(
        and_(
            ScrapeJob.template_name == template_name,
            ScrapeJob.user_id == current_user.id,
            ScrapeJob.status.in_(["pending", "queued", "running"])
        )
    ).count()
    
    if active_jobs > 0:
        raise HTTPException(
            status_code=409,
            detail=f"Template is being used by {active_jobs} active jobs"
        )
    
    # Delete template
    success = await template_service.delete_template(
        template_name,
        str(current_user.id)
    )
    
    if not success:
        raise HTTPException(status_code=500, detail="Failed to delete template")
    
    return StatusResponse(
        success=True,
        message="Template deleted successfully"
    )


@router.post("/validate", response_model=TemplateValidation)
async def validate_template_endpoint(
    template_data: dict,
    current_user: User = Depends(get_current_user)
):
    """Validate a template structure."""
    
    template_service = TemplateService()
    validation_result = await template_service.validate_template(template_data)
    
    return validation_result


@router.post("/{template_name}/test", response_model=StatusResponse)
@rate_limit(requests=5, window=300)  # 5 tests per 5 minutes
async def test_template(
    template_name: str,
    test_request: TemplateTest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Test a template against real URLs."""
    
    template_service = TemplateService()
    
    # Get template
    template = await template_service.get_template(
        template_name,
        str(current_user.id)
    )
    
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    
    # Start background test
    test_id = f"test_{template_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    background_tasks.add_task(
        template_service.test_template,
        template,
        test_request.test_urls,
        test_id,
        str(current_user.id),
        test_request.timeout_seconds
    )
    
    return StatusResponse(
        success=True,
        message="Template test started",
        data={"test_id": test_id}
    )


@router.get("/{template_name}/test/{test_id}")
async def get_test_results(
    template_name: str,
    test_id: str,
    current_user: User = Depends(get_current_user)
):
    """Get template test results."""
    
    template_service = TemplateService()
    results = await template_service.get_test_results(
        test_id,
        str(current_user.id)
    )
    
    if not results:
        raise HTTPException(status_code=404, detail="Test results not found")
    
    return results


@router.post("/upload", response_model=StatusResponse)
@rate_limit(requests=5, window=3600)  # 5 uploads per hour
async def upload_template(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user)
):
    """Upload a template from YAML file."""
    
    if not file.filename.endswith(('.yml', '.yaml')):
        raise HTTPException(
            status_code=400,
            detail="File must be a YAML file (.yml or .yaml)"
        )
    
    try:
        content = await file.read()
        template_data = yaml.safe_load(content.decode('utf-8'))
    except yaml.YAMLError as e:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid YAML file: {str(e)}"
        )
    except UnicodeDecodeError:
        raise HTTPException(
            status_code=400,
            detail="File must be UTF-8 encoded"
        )
    
    template_service = TemplateService()
    
    # Validate template
    validation_result = await template_service.validate_template(template_data)
    if not validation_result.is_valid:
        raise HTTPException(
            status_code=400,
            detail=f"Template validation failed: {', '.join(validation_result.errors)}"
        )
    
    # Create template
    template_name = template_data.get('name') or Path(file.filename).stem
    
    existing = await template_service.get_template(
        template_name,
        str(current_user.id)
    )
    
    if existing:
        raise HTTPException(
            status_code=409,
            detail="Template with this name already exists"
        )
    
    created_template = await template_service.create_template(
        user_id=str(current_user.id),
        template_data=template_data
    )
    
    return StatusResponse(
        success=True,
        message="Template uploaded successfully",
        data={"template_name": created_template.name}
    )


@router.get("/{template_name}/download")
async def download_template(
    template_name: str,
    version: str = Query("latest", description="Template version"),
    format: str = Query("yaml", description="Download format"),
    current_user: User = Depends(get_current_user)
):
    """Download a template as YAML file."""
    
    template_service = TemplateService()
    template = await template_service.get_template(
        template_name,
        str(current_user.id),
        version=version
    )
    
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    
    # Generate file content
    if format.lower() == "yaml":
        content = yaml.dump(template.to_dict(), default_flow_style=False, allow_unicode=True)
        media_type = "application/x-yaml"
        filename = f"{template_name}.yml"
    elif format.lower() == "json":
        import json
        content = json.dumps(template.to_dict(), indent=2, ensure_ascii=False)
        media_type = "application/json"
        filename = f"{template_name}.json"
    else:
        raise HTTPException(status_code=400, detail="Unsupported format")
    
    # Create temporary file
    import tempfile
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix=f".{format}") as tmp_file:
        tmp_file.write(content)
        tmp_file_path = tmp_file.name
    
    return FileResponse(
        tmp_file_path,
        media_type=media_type,
        filename=filename,
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )


@router.post("/{template_name}/clone", response_model=StatusResponse)
async def clone_template(
    template_name: str,
    new_name: str = Query(..., description="Name for cloned template"),
    current_user: User = Depends(get_current_user)
):
    """Clone an existing template."""
    
    template_service = TemplateService()
    
    # Get source template
    source_template = await template_service.get_template(
        template_name,
        str(current_user.id)
    )
    
    if not source_template:
        raise HTTPException(status_code=404, detail="Source template not found")
    
    # Check if new name already exists
    existing = await template_service.get_template(
        new_name,
        str(current_user.id)
    )
    
    if existing:
        raise HTTPException(
            status_code=409,
            detail="Template with new name already exists"
        )
    
    # Clone template
    cloned_template = await template_service.clone_template(
        template_name,
        new_name,
        str(current_user.id)
    )
    
    return StatusResponse(
        success=True,
        message="Template cloned successfully",
        data={"new_template_name": cloned_template.name}
    )


@router.get("/categories")
async def get_template_categories():
    """Get available template categories."""
    
    return {
        "categories": [
            {"name": "e-commerce", "description": "Online stores and marketplaces"},
            {"name": "news", "description": "News websites and blogs"},
            {"name": "social-media", "description": "Social media platforms"},
            {"name": "real-estate", "description": "Property and real estate sites"},
            {"name": "job-boards", "description": "Job listing websites"},
            {"name": "directories", "description": "Business and service directories"},
            {"name": "forums", "description": "Discussion forums and communities"},
            {"name": "government", "description": "Government and public data sites"},
            {"name": "academic", "description": "Academic and research sites"},
            {"name": "finance", "description": "Financial and investment sites"},
            {"name": "travel", "description": "Travel and booking sites"},
            {"name": "other", "description": "Other types of websites"}
        ]
    }


@router.get("/{template_name}/usage-stats")
async def get_template_usage_stats(
    template_name: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get usage statistics for a template."""
    
    template_service = TemplateService()
    template = await template_service.get_template(
        template_name,
        str(current_user.id)
    )
    
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    
    # Get usage stats from database
    total_jobs = db.query(ScrapeJob).filter(
        and_(
            ScrapeJob.template_name == template_name,
            ScrapeJob.user_id == current_user.id
        )
    ).count()
    
    successful_jobs = db.query(ScrapeJob).filter(
        and_(
            ScrapeJob.template_name == template_name,
            ScrapeJob.user_id == current_user.id,
            ScrapeJob.status == "completed"
        )
    ).count()
    
    return {
        "template_name": template_name,
        "total_jobs": total_jobs,
        "successful_jobs": successful_jobs,
        "success_rate": (successful_jobs / total_jobs * 100) if total_jobs > 0 else 0,
        "last_used": template.last_used.isoformat() if template.last_used else None
    }
