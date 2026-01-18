from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.schemas.farm import FarmCreate, FarmRead
from src.schemas.user import UserRead
from src.dependencies import CurrentActiveUser
from src.database import get_db_session

from src.services import farm as farm_service
from src.services.farm import get_farm_by_id
from src.models.user import User

# The router instance
router = APIRouter(prefix="/farms", tags=["Farms"])


@router.post(
    "",
    response_model=FarmRead,  # Response to the user
    status_code=201,
)
async def create_farm_endpoint(
    # Validates the data against the pydantic model
    farm_data: FarmCreate,
    # 2. Inject the authenticated user
    current_user: UserRead = CurrentActiveUser,
    # 3. Inject the REAL database session
    db: AsyncSession = Depends(get_db_session),
):
    """
    Handles the POST request to create a new farm record.

    Requires: Authentication (via CurrentActiveUser), and validated Farm data (FarmCreate).
    """

    # Pass validated Pydantic data, secure user ID, AND THE DB SESSION to the service layer
    new_farm_data = await farm_service.create_farm_record(
        db=db, farm_data=farm_data, user_id=current_user.id
    )

    # FastAPI serializes the returned ORM object into the FarmRead contract.
    return new_farm_data


@router.get("/{farm_id}", response_model=FarmRead)
async def read_farm_endpoint(
    farm_id: int,
    db: AsyncSession = Depends(get_db_session),
    # Assuming CurrentActiveUser is configured to return the User ORM object (src.models.user.User)
    current_user: User = CurrentActiveUser,
):
    """
    Retrieves a single farm by ID, ensuring the requesting user is the owner.
    """
    farm = await get_farm_by_id(db, farm_id=farm_id, user_id=current_user.id)

    if not farm:
        # A 404 is appropriate here, as it doesn't leak whether the resource
        # exists but is unauthorized, or simply doesn't exist.
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Farm with ID {farm_id} not found.",
        )

    return farm
