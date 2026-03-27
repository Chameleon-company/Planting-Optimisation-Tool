from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_db_session
from src.dependencies import get_user_id, limiter, require_role
from src.schemas.sapling_estimation import SaplingEstimationResponse
from src.schemas.user import Role, UserRead
from src.services import farm as farm_service
from src.services import sapling_estimation as sapling_estimation_service

router = APIRouter(prefix="/sapling_estimation", tags=["Sapling Calculator"])


@router.get(
    "/{farm_id}",
    response_model=SaplingEstimationResponse,
    response_model_exclude_none=True,
)
@limiter.limit("10/minute", key_func=get_user_id)
async def get_sapling_estimation(
    request: Request,
    farm_id: int,
    db: AsyncSession = Depends(get_db_session),
    current_user: UserRead = Depends(require_role(Role.OFFICER)),
):
    """- Estimates the number of saplings that can be planted on farm.

    - **farm_id**: The ID of the farm (must have an existing boundary)
    - **Returns**: id, sapling_count, optimal_angle.


    Estimates sapling count for a farm based on boundary area.
    Requires OFFICER role or higher.
    """
    if current_user.role == Role.OFFICER:
        user_id_filter = current_user.id
    else:
        user_id_filter = None

    farms = await farm_service.get_farm_by_id(db, [farm_id], user_id=user_id_filter)
    if not farms:
        raise HTTPException(status_code=404, detail=f"Farm with ID {farm_id} not found.")

    service = sapling_estimation_service.SaplingEstimationService()
    estimation_data = await service.run_estimation(db, farm_id)

    if not estimation_data:
        raise HTTPException(status_code=404, detail=f"Farm boundary not found for farm_id: {farm_id}")

    return estimation_data
