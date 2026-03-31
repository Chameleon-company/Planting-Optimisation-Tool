from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_db_session
from src.dependencies import require_role
from src.schemas.ahp import AhpCalculationRequest, AhpResponse
from src.schemas.user import Role, UserRead
from src.services.ahp_service import AhpService

router = APIRouter(prefix="/ahp", tags=["AHP Calculator"])


@router.post(
    "/calculate-and-save",
    response_model=AhpResponse,
    response_model_exclude_none=True,
)
async def calculate_weights(
    payload: AhpCalculationRequest,
    db: AsyncSession = Depends(get_db_session),
    current_user: UserRead = Depends(require_role(Role.ADMIN)),
):
    """Calculate, validate, and persist AHP weights for a species.

    Args:
        payload: Request payload containing the comparison matrix and species ID.
        db: Async database session dependency.
        current_user: Authenticated user, restricted to ADMIN role.

    Returns:
        AhpResponse: Calculated AHP weights and related consistency metadata.

    Raises:
        HTTPException: Raised with status code 400 when the matrix validation fails.
    """
    # Instantiate the service
    service = AhpService()

    try:
        # Pass the DB session and payload to the service
        result_data = await service.calculate_and_save_ahp_weights(db=db, matrix=payload.matrix, species_id=payload.species_id)
        return result_data

    except ValueError as ve:
        # The service throws a ValueError if the matrix size is wrong
        raise HTTPException(status_code=400, detail=str(ve))
