from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from ...db import crud
from ..deps import get_db
from ...schemas import jobs as s_jobs, results as s_results
from ...crawler.template_dsl import parse_template_yaml
from ...scheduler.scheduler import enqueue_job

router = APIRouter(prefix="/jobs", tags=["jobs"])

@router.post("", response_model=s_jobs.JobOut)
async def create_job(payload: s_jobs.JobCreate, db: AsyncSession = Depends(get_db)):
    tmpl = await crud.get_template(db, payload.template_id)
    if not tmpl:
        raise HTTPException(404, "Template not found")
    # validera DSL (snabb check)
    parse_template_yaml(tmpl.yaml)
    job = await crud.create_job(db, tmpl.id, payload.params or {})
    # enquea (inom process via scheduler)
    await enqueue_job(job.id)
    job = await crud.get_job(db, job.id)
    return job  # type: ignore

@router.get("/{job_id}", response_model=s_jobs.JobOut)
async def get_job(job_id: int, db: AsyncSession = Depends(get_db)):
    job = await crud.get_job(db, job_id)
    if not job:
        raise HTTPException(404)
    return job  # type: ignore

@router.get("/{job_id}/results", response_model=list[s_results.ResultOut])
async def get_results(job_id: int, db: AsyncSession = Depends(get_db)):
    return await crud.list_results(db, job_id)
