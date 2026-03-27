from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_db_session
from src.dependencies import get_user_id, limiter, require_role
from src.schemas.environmental_profile import FarmProfileResponse
from src.schemas.user import Role, UserRead
from src.services import environmental_profile as environmental_profile_service
from src.services import farm as farm_service

router = APIRouter(prefix="/profile", tags=["Environmental Profile"])


@router.get(
    "/{farm_id}",
    response_model=FarmProfileResponse,
    response_model_exclude_none=True,
)
@limiter.limit("10/minute", key_func=get_user_id)
async def get_farm_profile(
    request: Request,
    farm_id: int,
    db: AsyncSession = Depends(get_db_session),
    current_user: UserRead = Depends(require_role(Role.OFFICER)),
):
    """- Fetch environmental data from Google Earth Engine to build environmental profile for farm.

    - **farm_id**: The ID of the farm (must have an existing boundary)
    - **Returns**: id, rainfall_mm, temperature_celsius, elevation_m, ph, soil_texture_id, area_ha,
     latitude, longitude, coastal, slope.

    Fetches environmental data from Google Earth Engine for a farm.
    Requires OFFICER role or higher.
    """
    if current_user.role == Role.OFFICER:
        user_id_filter = current_user.id
    else:
        user_id_filter = None

    farms = await farm_service.get_farm_by_id(db, [farm_id], user_id=user_id_filter)
    if not farms:
        raise HTTPException(status_code=404, detail=f"Farm with ID {farm_id} not found.")

    service = environmental_profile_service.EnvironmentalProfileService()
    profile_data = await service.run_environmental_profile(db, farm_id)

    if not profile_data:
        raise HTTPException(status_code=404, detail=f"Farm boundary not found for farm_id: {farm_id}")

    return profile_data
