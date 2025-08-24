from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from .models import Template, Job, Result

async def create_template(session: AsyncSession, name: str, yaml_text: str) -> Template:
    t = Template(name=name, yaml=yaml_text)
    session.add(t)
    await session.commit()
    await session.refresh(t)
    return t

async def get_template(session: AsyncSession, template_id: int) -> Template | None:
    res = await session.execute(select(Template).where(Template.id == template_id))
    return res.scalar_one_or_none()

async def list_templates(session: AsyncSession) -> list[Template]:
    res = await session.execute(select(Template).order_by(Template.id.desc()))
    return list(res.scalars())

async def create_job(session: AsyncSession, template_id: int, params: dict | None = None) -> Job:
    job = Job(template_id=template_id, params=params or {}, status="queued")
    session.add(job)
    await session.commit()
    await session.refresh(job)
    return job

async def get_job(session: AsyncSession, job_id: int) -> Job | None:
    res = await session.execute(select(Job).where(Job.id == job_id))
    return res.scalar_one_or_none()

async def update_job_status(session: AsyncSession, job_id: int, **kwargs) -> None:
    await session.execute(update(Job).where(Job.id == job_id).values(**kwargs))
    await session.commit()

async def add_result(session: AsyncSession, job_id: int, url: str, data: dict) -> Result:
    r = Result(job_id=job_id, url=url, data=data)
    session.add(r)
    await session.commit()
    await session.refresh(r)
    return r

async def list_results(session: AsyncSession, job_id: int) -> list[Result]:
    res = await session.execute(select(Result).where(Result.job_id == job_id))
    return list(res.scalars())
