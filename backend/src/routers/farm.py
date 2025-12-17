from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.schemas.farm import FarmCreate, FarmRead
from src.schemas.user import UserRead
from src.dependencies import CurrentActiveUser
from src.database import get_db_session

from src.services import farm as farm_service

# The router instance
router = APIRouter(prefix="/farms", tags=["Farms"])


@router.post(
    "/",
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
