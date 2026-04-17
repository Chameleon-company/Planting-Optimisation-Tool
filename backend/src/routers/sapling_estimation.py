import json

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession

from src import cache
from src.database import get_db_session
from src.dependencies import get_user_id, limiter, require_role
from src.schemas.sapling_estimation import SaplingEstimationRequest, SaplingEstimationResponse
from src.schemas.user import Role, UserRead
from src.services import farm as farm_service
from src.services import sapling_estimation as sapling_estimation_service

router = APIRouter(prefix="/sapling_estimation", tags=["Sapling Calculator"])


@router.post(
    "/calculate",
    response_model=SaplingEstimationResponse,
    response_model_exclude_none=True,
)
@limiter.limit("10/minute", key_func=get_user_id)
async def get_sapling_estimation(
    request: Request,
    data: SaplingEstimationRequest,
    db: AsyncSession = Depends(get_db_session),
    current_user: UserRead = Depends(require_role(Role.OFFICER)),
):
    """- Estimates sapling planting capacity for a farm.

    Inputs:
    - farm_id: ID of the farm
    - spacing_x: horizontal spacing between saplings
    - spacing_y: vertical spacing between saplings
    - max_slope: maximum allowed slope

    Returns:
    - pre_slope_count
    - aligned_count
    - optimal_angle (if applicable)

    Requires OFFICER role or higher.
    """
    if current_user.role == Role.OFFICER:
        user_id_filter = current_user.id
    else:
        user_id_filter = None

    farm_id = data.farm_id
    spacing_x = data.spacing_x
    spacing_y = data.spacing_y
    max_slope = data.max_slope

    farms = await farm_service.get_farm_by_id(db, [farm_id], user_id=user_id_filter)
    if not farms:
        raise HTTPException(status_code=404, detail=f"Farm with ID {farm_id} not found.")

    cache_key = f"sapling:{farm_id}:{spacing_x}:{spacing_y}:{max_slope}"
    cached = await cache.get(cache_key)
    if cached:
        return SaplingEstimationResponse(**json.loads(cached))

    service = sapling_estimation_service.SaplingEstimationService()
    estimation_data = await service.run_estimation(db, farm_id, spacing_x=spacing_x, spacing_y=spacing_y, max_slope=max_slope)

    if not estimation_data:
        raise HTTPException(status_code=404, detail=f"Farm boundary not found for farm_id: {farm_id}")

    await cache.set(cache_key, json.dumps(estimation_data))
    return estimation_data
