from fastapi import APIRouter, HTTPException, Depends, Header, Request, status
from sqlalchemy.orm import Session
from uuid import UUID
from typing import List, Optional, Dict, Any
from src.database.models import Template, TemplateCreate, TemplateRead, TemplateUpdate
from src.database.manager import get_db
from src.webapp.security import get_current_tenant_id, authorize_with_scopes
import logging
import hashlib
import json

router = APIRouter()
logger = logging.getLogger(__name__)

def _generate_etag(template: Template) -> str:
    """Generates an ETag for a template based on its content and version."""
    content_hash = hashlib.sha256(json.dumps(template.dsl, sort_keys=True).encode()).hexdigest()
    return f'"{content_hash}-{template.version}"'

@router.post("/templates", response_model=TemplateRead, status_code=201, dependencies=[Depends(authorize_with_scopes(["templates:write"]))])
async def create_template(
    template: TemplateCreate, 
    tenant_id: UUID = Depends(get_current_tenant_id),
    db: Session = Depends(get_db),
    idempotency_key: Optional[str] = Header(None)
):
    """Creates a new scraping template."""
    logger.info(f"Creating template: {template.name}", extra={"idempotency_key": idempotency_key, "tenant_id": str(tenant_id)})
    
    db_template = db.query(Template).filter(Template.name == template.name, Template.tenant_id == tenant_id).first()
    if db_template:
        raise HTTPException(status_code=409, detail="Template with this name already exists for this tenant.")
        
    new_template = Template(tenant_id=tenant_id, **template.model_dump())
    db.add(new_template)
    db.commit()
    db.refresh(new_template)
    
    # Add ETag to the response model
    template_read = TemplateRead.from_orm(new_template)
    template_read.etag = _generate_etag(new_template)
    return template_read

@router.get("/templates", response_model=List[TemplateRead], dependencies=[Depends(authorize_with_scopes(["templates:read"]))])
async def get_all_templates(
    tenant_id: UUID = Depends(get_current_tenant_id),
    db: Session = Depends(get_db)
):
    """Retrieves all templates for the authenticated tenant."""
    templates = db.query(Template).filter(Template.tenant_id == tenant_id).all()
    return [TemplateRead.from_orm(t).copy(update={"etag": _generate_etag(t)}) for t in templates]

@router.get("/templates/{template_id}", response_model=TemplateRead, dependencies=[Depends(authorize_with_scopes(["templates:read"]))])
async def get_template(
    template_id: UUID, 
    tenant_id: UUID = Depends(get_current_tenant_id),
    db: Session = Depends(get_db)
):
    """Retrieves a specific template by its ID."""
    db_template = db.query(Template).filter(Template.id == template_id, Template.tenant_id == tenant_id).first()
    if not db_template:
        raise HTTPException(status_code=404, detail="Template not found")
    
    template_read = TemplateRead.from_orm(db_template)
    template_read.etag = _generate_etag(db_template)
    return template_read

@router.put("/templates/{template_id}", response_model=TemplateRead, dependencies=[Depends(authorize_with_scopes(["templates:write"]))])
async def update_template(
    template_id: UUID, 
    template_update: TemplateUpdate, 
    tenant_id: UUID = Depends(get_current_tenant_id),
    db: Session = Depends(get_db),
    if_match: str = Header(..., description="ETag of the template for optimistic concurrency control.") # Made required
):
    """Updates an existing template."""
    db_template = db.query(Template).filter(Template.id == template_id, Template.tenant_id == tenant_id).first()
    if not db_template:
        raise HTTPException(status_code=404, detail="Template not found")
    
    # Optimistic concurrency check
    expected_etag = _generate_etag(db_template)
    if if_match != expected_etag: # if_match is now guaranteed to be present
        raise HTTPException(
            status_code=status.HTTP_412_PRECONDITION_FAILED,
            detail="Precondition Failed: ETag mismatch. The resource has been modified.",
            headers={"ETag": expected_etag}
        )

    update_data = template_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_template, key, value)
    
    db_template.version += 1 # Increment version on update
    db.commit()
    db.refresh(db_template)
    
    template_read = TemplateRead.from_orm(db_template)
    template_read.etag = _generate_etag(db_template)
    return template_read

@router.delete("/templates/{template_id}", status_code=204, dependencies=[Depends(authorize_with_scopes(["templates:write"]))])
async def delete_template(
    template_id: UUID, 
    tenant_id: UUID = Depends(get_current_tenant_id),
    db: Session = Depends(get_db)
):
    """Deletes a template."""
    db_template = db.query(Template).filter(Template.id == template_id, Template.tenant_id == tenant_id).first()
    if not db_template:
        raise HTTPException(status_code=404, detail="Template not found")
    
    db.delete(db_template)
    db.commit()
    return None

@router.patch("/templates/{template_id}/status", response_model=TemplateRead, dependencies=[Depends(authorize_with_scopes(["templates:write"]))])
async def update_template_status(
    template_id: UUID,
    status_update: Dict[str, Any], # Expecting {"status": "active" | "inactive" | "draft"}
    tenant_id: UUID = Depends(get_current_tenant_id),
    db: Session = Depends(get_db)
):
    """
    Updates the status of a template (e.g., active, inactive, draft).
    This can be used for canary deployments or A/B testing of templates.
    """
    db_template = db.query(Template).filter(Template.id == template_id, Template.tenant_id == tenant_id).first()
    if not db_template:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Template not found")

    new_status = status_update.get("status")
    if not new_status or new_status not in ["active", "inactive", "draft"]:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid status provided. Must be 'active', 'inactive', or 'draft'.")

    db_template.status = new_status
    db_template.updated_at = datetime.datetime.utcnow()
    db.commit()
    db.refresh(db_template)

    template_read = TemplateRead.from_orm(db_template)
    template_read.etag = _generate_etag(db_template)
    return template_read