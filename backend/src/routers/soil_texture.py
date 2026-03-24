from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_db_session
from src.schemas.soil_texture import SoilTextureRead
from src.services import soil_texture as soil_texture_service

router = APIRouter(
    prefix="/soil-textures",
    tags=["Soil Textures"],
)


@router.get(
    "",
    response_model=List[SoilTextureRead],
    summary="Retrieve all available soil texture types.",
)
async def read_soil_textures(
    db: AsyncSession = Depends(get_db_session),
):
    """Returns all available soil texture types.
    Public endpoint - no authentication required.
    """
    # Call the service layer function
    db_textures = await soil_texture_service.get_all_textures(db)

    # FastAPI automatically serializes the list of ORM objects
    # (db_textures) using the SoilTextureRead Pydantic schema.
    return db_textures
