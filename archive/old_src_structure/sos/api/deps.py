from fastapi import Depends
from ..db.session import get_session
from sqlalchemy.ext.asyncio import AsyncSession

async def get_db(session: AsyncSession = Depends(get_session)):
    return session
