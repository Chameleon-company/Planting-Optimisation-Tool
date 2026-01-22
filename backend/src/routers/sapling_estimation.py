from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from src.database import get_db_session
from src.services.sapling_estimation import SaplingEstimationService
from src.schemas.sapling_estimation import SaplingEstimationResponse

router = APIRouter(prefix="/sapling_estimation", tags=["Sapling Calculator"])


@router.get(
    "/{farm_id}",
    response_model=SaplingEstimationResponse,
    response_model_exclude_none=True,
)
async def get_sapling_estimation(
    farm_id: int, db: AsyncSession = Depends(get_db_session)
):
    """
    Estimates the number of saplings that can be planted on farm.

    - **farm_id**: The ID of the farm (must have an existing boundary)
    - **Returns**: id, sapling_count, optimal_angle.
    """
    service = SaplingEstimationService()
    estimation_data = await service.run_estimation(db, farm_id)

    if not estimation_data:
        raise HTTPException(
            status_code=404, detail=f"Farm boundary not found for farm_id: {farm_id}"
        )

    return estimation_data
