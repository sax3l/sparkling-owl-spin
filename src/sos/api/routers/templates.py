from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from ...db import crud
from ...schemas import templates as s
from ..deps import get_db

router = APIRouter(prefix="/templates", tags=["templates"])

@router.post("", response_model=s.TemplateOut)
async def create_template(payload: s.TemplateCreate, db: AsyncSession = Depends(get_db)):
    t = await crud.create_template(db, payload.name, payload.yaml)
    return t

@router.get("", response_model=list[s.TemplateOut])
async def list_templates(db: AsyncSession = Depends(get_db)):
    return await crud.list_templates(db)
