from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from src.database import get_db_session
from src.services.environmental_profile import EnvironmentalProfileService
from src.schemas.environmental_profile import FarmProfileResponse

router = APIRouter(prefix="/farms", tags=["Environmental Profile"])


@router.get("/{farm_id}/profile", response_model=FarmProfileResponse)
async def get_farm_profile(farm_id: int, db: AsyncSession = Depends(get_db_session)):
    """
    Fetch environmental data from Google Earth Engine to build environmental profile for farm.

    - **farm_id**: The ID of the farm (must have an existing boundary)
    - **Returns**: id, rainfall_mm, temperature_celsius, elevation_m, ph, soil_texture_id, area_ha,
     latitude, longitude, coastal, slope.
    """
    service = EnvironmentalProfileService()
    profile_data = await service.run_environmental_profile(db, farm_id)

    if not profile_data:
        raise HTTPException(
            status_code=404, detail=f"Farm boundary not found for farm_id: {farm_id}"
        )

    return profile_data
