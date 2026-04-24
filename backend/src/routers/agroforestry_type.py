from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_db_session
from src.schemas.agroforestry_type import AgroforestryTypeRead
from src.services import agroforestry_type as service

router = APIRouter(
    prefix="/agroforestry-types",
    tags=["Agroforestry Types"],
)


@router.get(
    "",
    response_model=List[AgroforestryTypeRead],
)
async def read_agroforestry_types(
    db: AsyncSession = Depends(get_db_session),
):
    return await service.get_all_agroforestry_types(db)
