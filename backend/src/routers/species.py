from typing import List

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_db_session
from src.dependencies import get_user_id, limiter, require_role
from src.schemas.species import SpeciesCreate, SpeciesDropdownRead, SpeciesRead, SpeciesUpdate
from src.schemas.user import Role, UserRead
from src.services import species as species_service
from src.services.species import get_recommendation_features, get_species_for_dropdown

router = APIRouter(prefix="/species", tags=["Species"])


@router.post("", response_model=SpeciesRead, status_code=status.HTTP_201_CREATED)
@limiter.limit("10/minute", key_func=get_user_id)
async def create_species(
    request: Request,
    payload: SpeciesCreate,
    db: AsyncSession = Depends(get_db_session),
    current_user: UserRead = Depends(require_role(Role.ADMIN)),
):
    """Creates a new species with characteristics and parameters.
    Requires ADMIN role.
    """
    return await species_service.create_species(db, payload)


@router.put("/{species_id}", response_model=SpeciesRead)
@limiter.limit("10/minute", key_func=get_user_id)
async def update_species(
    request: Request,
    species_id: int,
    payload: SpeciesUpdate,
    db: AsyncSession = Depends(get_db_session),
    current_user: UserRead = Depends(require_role(Role.ADMIN)),
):
    """Updates an existing species.
    Requires ADMIN role.
    """
    try:
        species = await species_service.update_species(db, species_id, payload)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=str(exc),
        ) from exc

    if species is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Species not found",
        )

    return species


@router.delete("/{species_id}", status_code=status.HTTP_204_NO_CONTENT)
@limiter.limit("10/minute", key_func=get_user_id)
async def delete_species(
    request: Request,
    species_id: int,
    db: AsyncSession = Depends(get_db_session),
    current_user: UserRead = Depends(require_role(Role.ADMIN)),
):
    """Deletes an existing species.
    Requires ADMIN role.
    """
    deleted = await species_service.delete_species(db, species_id)

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Species not found",
        )

    return


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
