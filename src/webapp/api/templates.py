from fastapi import APIRouter, HTTPException, Depends, Header
from sqlalchemy.orm import Session
from uuid import UUID
from typing import List, Optional
from src.database.models import Template, TemplateCreate, TemplateRead, TemplateUpdate
from src.database.manager import get_db
from src.webapp.security import get_api_key
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/templates", response_model=TemplateRead, status_code=201, dependencies=[Depends(get_api_key)])
async def create_template(
    template: TemplateCreate, 
    db: Session = Depends(get_db),
    idempotency_key: Optional[str] = Header(None)
):
    """Creates a new scraping template."""
    # Note: Full idempotency logic would check the key against a cache/DB.
    logger.info(f"Creating template: {template.name}", extra={"idempotency_key": idempotency_key})
    
    db_template = db.query(Template).filter(Template.name == template.name).first()
    if db_template:
        raise HTTPException(status_code=409, detail="Template with this name already exists")
        
    new_template = Template(**template.model_dump())
    db.add(new_template)
    db.commit()
    db.refresh(new_template)
    return new_template

@router.get("/templates", response_model=List[TemplateRead], dependencies=[Depends(get_api_key)])
async def get_all_templates(db: Session = Depends(get_db)):
    """Retrieves all templates."""
    return db.query(Template).all()

@router.get("/templates/{template_id}", response_model=TemplateRead, dependencies=[Depends(get_api_key)])
async def get_template(template_id: UUID, db: Session = Depends(get_db)):
    """Retrieves a specific template by its ID."""
    db_template = db.query(Template).filter(Template.id == template_id).first()
    if not db_template:
        raise HTTPException(status_code=404, detail="Template not found")
    return db_template

@router.put("/templates/{template_id}", response_model=TemplateRead, dependencies=[Depends(get_api_key)])
async def update_template(template_id: UUID, template: TemplateUpdate, db: Session = Depends(get_db)):
    """Updates an existing template."""
    db_template = db.query(Template).filter(Template.id == template_id).first()
    if not db_template:
        raise HTTPException(status_code=404, detail="Template not found")
    
    update_data = template.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_template, key, value)
    
    db_template.version += 1 # Increment version on update
    db.commit()
    db.refresh(db_template)
    return db_template

@router.delete("/templates/{template_id}", status_code=204, dependencies=[Depends(get_api_key)])
async def delete_template(template_id: UUID, db: Session = Depends(get_db)):
    """Deletes a template."""
    db_template = db.query(Template).filter(Template.id == template_id).first()
    if not db_template:
        raise HTTPException(status_code=404, detail="Template not found")
    
    db.delete(db_template)
    db.commit()
    return None