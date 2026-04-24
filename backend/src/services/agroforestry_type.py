from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models import AgroforestryType


async def get_all_agroforestry_types(db: AsyncSession):
    result = await db.execute(select(AgroforestryType))
    return result.scalars().all()
