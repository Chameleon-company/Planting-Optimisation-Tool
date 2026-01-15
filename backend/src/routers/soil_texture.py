from fastapi import APIRouter, Depends
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession

from src.schemas.soil_texture import SoilTextureRead
from src.services.soil_texture import get_all_textures  # Import the service function
from src.database import get_db_session  # Import the database dependency

router = APIRouter(
    prefix="/soil-textures",
    tags=["Soil Textures"],
)


@router.get(
    "",
    response_model=List[SoilTextureRead],
    summary="Retrieve all available soil texture types.",
)
# Inject the database session using Depends(get_db)
async def read_soil_textures(db: AsyncSession = Depends(get_db_session)):
    """
    Returns a list of all soil texture types used for foreign key lookups.
    """
    # Call the service layer function
    db_textures = await get_all_textures(db)

    # FastAPI automatically serializes the list of ORM objects
    # (db_textures) using the SoilTextureRead Pydantic schema.
    return db_textures
