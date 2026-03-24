from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_db_session
from src.dependencies import require_role
from src.schemas.species import SpeciesCreate
from src.schemas.user import Role, UserRead
from src.services import species as species_service

router = APIRouter(prefix="/species", tags=["Species"])


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_species(
    payload: SpeciesCreate,
    db: AsyncSession = Depends(get_db_session),
    current_user: UserRead = Depends(require_role(Role.SUPERVISOR)),
):
    """Creates a new species with characteristics and parameters.
    Requires SUPERVISOR role or higher.
    """
    return await species_service.create_species(db, payload)
