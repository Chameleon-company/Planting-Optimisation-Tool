from typing import List

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_db_session
from src.dependencies import require_role
from src.schemas.species import SpeciesCreate, SpeciesDropdownRead
from src.schemas.user import Role, UserRead
from src.services import species as species_service
from src.services.species import get_recommendation_features, get_species_for_dropdown

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


@router.get("/dropdown", response_model=List[SpeciesDropdownRead])
async def get_species_list(
    db: AsyncSession = Depends(get_db_session),
    current_user: UserRead = Depends(require_role(Role.OFFICER)),
):
    """
    Returns a lightweight list of species (id, scientific name, common name)
    designed for populating frontend UI elements like dropdowns.
    """
    species_list = await get_species_for_dropdown(db)
    return species_list


@router.get("/features", response_model=List[str])
async def read_recommendation_features():
    """
    Returns a list of feature short names (e.g., ['RF', 'Temp'])
    used for the suitability scoring UI.
    """
    return get_recommendation_features()
