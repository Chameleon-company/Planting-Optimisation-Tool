from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_db_session
from src.dependencies import get_user_id, limiter, require_role
from src.schemas.batch_estimation import SaplingBatchEstimationRequest, SaplingBatchEstimationResponse
from src.schemas.user import Role, UserRead
from src.services.batch_estimation import SaplingBatchEstimationService

router = APIRouter(prefix="/sapling_estimation", tags=["Sapling Calculator"])


@router.post(
    "/batch_calculate",
    response_model=SaplingBatchEstimationResponse,
    response_model_exclude_none=True,
)
@limiter.limit("10/minute", key_func=get_user_id)
async def get_batch_estimation(
    request: Request,
    data: SaplingBatchEstimationRequest,
    db: AsyncSession = Depends(get_db_session),
    current_user: UserRead = Depends(require_role(Role.OFFICER)),
):
    """- Batch estimates sapling planting capacity for all farms owned by the authenticated user.

    Inputs:
    - spacing_x: horizontal spacing between saplings
    - spacing_y: vertical spacing between saplings
    - max_slope: maximum allowed slope

    Returns:
    - status
    - farm_count: total number of farms processed
    - results: a list of estimations/results for a single farm:
        - farm_id
        - status
        - pre_slope_count
        - aligned_count
        - optimal_angle (if applicable)

    Requires OFFICER role or higher.
    """
    service = SaplingBatchEstimationService()

    return await service.run_batch_estimation(
        db=db,
        user_id=current_user.id,
        spacing_x=data.spacing_x,
        spacing_y=data.spacing_y,
        max_slope=data.max_slope,
    )
