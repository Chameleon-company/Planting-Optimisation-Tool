import json

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
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
@limiter.limit("10/minute", key_func=get_user_id)
async def get_sapling_estimation(
    request: Request,
    response: Response,
    data: SaplingEstimationRequest,
    db: AsyncSession = Depends(get_db_session),
    current_user: UserRead = Depends(require_role(Role.OFFICER)),
):
    """- Estimates sapling planting capacity for one or many farms.

    Inputs:
    - farm_ids: IDs of the farms to estimate
    - spacing_x: horizontal spacing between saplings
    - spacing_y: vertical spacing between saplings
    - max_slope: maximum allowed slope

    Returns a batch-shaped payload:
    - status
    - farm_count: number of farms processed
    - results: per-farm items, each with farm_id, status, an optional message
      on failure and on success, pre_slope_count,
      - aligned_count: total suitable planting capacity before baseline trees
      - baseline_tree_count: established trees already on the farm
      - additional_sapling_count: remaining capacity after baseline trees
        optimal_angle, rotation_average, rotation_std_dev

    Requires OFFICER role or higher.
    """
    if current_user.role == Role.OFFICER:
        user_id_filter = current_user.id
    else:
        user_id_filter = None

    farms = await farm_service.get_farm_by_id(db, data.farm_ids, user_id=user_id_filter)
    found_ids = {farm.id for farm in farms}
    missing = [farm_id for farm_id in data.farm_ids if farm_id not in found_ids]
    if not found_ids:
        raise HTTPException(
            status_code=404,
            detail=f"Farm(s) not found or not owned: {', '.join(map(str, missing))}",
        )
    if missing:
        response.status_code = status.HTTP_207_MULTI_STATUS

    service = sapling_estimation_service.SaplingEstimationService()
    estimation_data = await service.run_estimation(
        db,
        farm_ids=data.farm_ids,
        spacing_x=data.spacing_x,
        spacing_y=data.spacing_y,
        max_slope=data.max_slope,
    )

    for farm_id in data.farm_ids:
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
