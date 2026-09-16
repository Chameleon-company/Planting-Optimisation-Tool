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
    """Runs sapling estimation for all farms owned by the authenticated user."""
    service = SaplingBatchEstimationService()
    return await service.run_batch_estimation(
        db=db,
        user_id=current_user.id,
        spacing_x=data.spacing_x,
        spacing_y=data.spacing_y,
        max_slope=data.max_slope,
    )
