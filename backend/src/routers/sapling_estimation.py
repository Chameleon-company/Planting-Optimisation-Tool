import json

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession

from src import cache
from src.database import get_db_session
from src.dependencies import get_user_id, limiter, require_role
from src.schemas.sapling_estimation import PlantingGridResponse, SaplingEstimationRequest, SaplingEstimationResponse
from src.schemas.user import Role, UserRead
from src.services import farm as farm_service
from src.services import sapling_estimation as sapling_estimation_service

router = APIRouter(prefix="/sapling_estimation", tags=["Sapling Calculator"])


@router.post(
    "/calculate",
    response_model=SaplingEstimationResponse,
    response_model_exclude_none=True,
)
@limiter.limit("20/minute", key_func=get_user_id)
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

    service = sapling_estimation_service.SaplingEstimationService()
    estimation_data = await service.run_estimation(db, farm_id, spacing_x=spacing_x, spacing_y=spacing_y, max_slope=max_slope)

    if not estimation_data:
        raise HTTPException(status_code=404, detail=f"Farm boundary not found for farm_id: {farm_id}")

    await cache.invalidate(f"grid:{farm_id}")
    return estimation_data


@router.get("/{farm_id}/grid", response_model=PlantingGridResponse)
@limiter.limit("10/minute", key_func=get_user_id)
async def get_planting_grid(
    request: Request,
    farm_id: int,
    db: AsyncSession = Depends(get_db_session),
    current_user: UserRead = Depends(require_role(Role.OFFICER)),
):
    """
    Returns saved planting estimate points for a farm as a GeoJSON FeatureCollection.

    TODO: Officer-level ownership filtering is not applied here due to problems with the RBAC
    implementation.
    Officers are not directly associated with farms as owners in the current implementation.
    Restrict to owned farms once the RBAC implementation is complete.
    """
    grid_cache_key = f"grid:{farm_id}"
    cached = await cache.get(grid_cache_key)
    if cached:
        return PlantingGridResponse(**json.loads(cached))

    grid = await sapling_estimation_service.get_planting_grid(db, farm_id)
    if not grid["features"]:
        raise HTTPException(status_code=404, detail=f"No planting estimates found for farm {farm_id}.")

    await cache.set(grid_cache_key, json.dumps(grid))
    return grid
