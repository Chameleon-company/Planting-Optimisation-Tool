from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_db_session
from src.dependencies import require_role
from src.schemas.farm import FarmCreate, FarmRead
from src.schemas.user import Role, UserRead
from src.services import farm as farm_service

# The router instance
router = APIRouter(prefix="/farms", tags=["Farms"])


@router.post(
    "",
    response_model=FarmRead,  # Response to the user
    status_code=201,
)
async def create_farm(
    # Validates the data against the pydantic model
    farm_data: FarmCreate,
    # Inject the authenticated user
    current_user: UserRead = Depends(require_role(Role.OFFICER)),
    # Inject the real database session
    db: AsyncSession = Depends(get_db_session),
):
    """Creates a new farm record with validated data.
    Requires OFFICER role or higher.
    """
    # Pass validated Pydantic data, secure user ID, AND THE DB SESSION to the service layer
    return await farm_service.create_farm_record(db=db, farm_data=farm_data, user_id=current_user.id)

    # FastAPI serializes the returned ORM object into the FarmRead contract.


@router.get("/{farm_id}", response_model=FarmRead)
async def read_farm(
    farm_id: int,
    db: AsyncSession = Depends(get_db_session),
    # Assuming CurrentActiveUser is configured to return the User ORM object (src.models.user.User)
    current_user: UserRead = Depends(require_role(Role.OFFICER)),
):
    """Retrieves a farm by ID.\n
    OFFICER role: see only own farms\n
    SUPERVISOR/ADMIN role: see all farms
    """
    if current_user.role == Role.OFFICER:
        user_id_filter = current_user.id
    else:
        user_id_filter = None

    farms = await farm_service.get_farm_by_id(db, farm_ids=[farm_id], user_id=user_id_filter)

    if not farms:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Farm with ID {farm_id} not found.",
        )

    return farms[0]
