from typing import List

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_db_session
from src.dependencies import get_user_id, limiter, require_role
from src.schemas.parameters import ParameterCreate, ParameterRead, ParameterUpdate
from src.schemas.user import Role, UserRead
from src.services import parameters as parameters_service

router = APIRouter(prefix="/parameters", tags=["Parameters"])


@router.get("", response_model=List[ParameterRead])
@limiter.limit("30/minute", key_func=get_user_id)
async def list_parameters(
    request: Request,
    db: AsyncSession = Depends(get_db_session),
    current_user: UserRead = Depends(require_role(Role.ADMIN)),
):
    """Returns all scoring parameters across all species.
    Requires ADMIN role.
    """
    return await parameters_service.get_all_parameters(db)


@router.get("/species/{species_id}", response_model=List[ParameterRead])
@limiter.limit("30/minute", key_func=get_user_id)
async def list_parameters_by_species(
    request: Request,
    species_id: int,
    db: AsyncSession = Depends(get_db_session),
    current_user: UserRead = Depends(require_role(Role.ADMIN)),
):
    """Returns all scoring parameters for a specific species.
    Requires ADMIN role.
    """
    return await parameters_service.get_parameters_by_species(db, species_id)


@router.get("/{parameter_id}", response_model=ParameterRead)
@limiter.limit("30/minute", key_func=get_user_id)
async def get_parameter(
    request: Request,
    parameter_id: int,
    db: AsyncSession = Depends(get_db_session),
    current_user: UserRead = Depends(require_role(Role.ADMIN)),
):
    """Returns a single scoring parameter by ID.
    Requires ADMIN role.
    """
    param = await parameters_service.get_parameter_by_id(db, parameter_id)

    if param is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Parameter not found",
        )

    return param


@router.post("", response_model=ParameterRead, status_code=status.HTTP_201_CREATED)
@limiter.limit("10/minute", key_func=get_user_id)
async def create_parameter(
    request: Request,
    payload: ParameterCreate,
    db: AsyncSession = Depends(get_db_session),
    current_user: UserRead = Depends(require_role(Role.ADMIN)),
):
    """Creates a new scoring parameter for a species.
    Requires ADMIN role.
    """
    try:
        return await parameters_service.create_parameter(db, payload)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=str(exc),
        ) from exc


@router.put("/{parameter_id}", response_model=ParameterRead)
@limiter.limit("10/minute", key_func=get_user_id)
async def update_parameter(
    request: Request,
    parameter_id: int,
    payload: ParameterUpdate,
    db: AsyncSession = Depends(get_db_session),
    current_user: UserRead = Depends(require_role(Role.ADMIN)),
):
    """Updates an existing scoring parameter.
    Requires ADMIN role.
    """
    try:
        param = await parameters_service.update_parameter(db, parameter_id, payload)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=str(exc),
        ) from exc

    if param is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Parameter not found",
        )

    return param


@router.delete("/{parameter_id}", status_code=status.HTTP_204_NO_CONTENT)
@limiter.limit("10/minute", key_func=get_user_id)
async def delete_parameter(
    request: Request,
    parameter_id: int,
    db: AsyncSession = Depends(get_db_session),
    current_user: UserRead = Depends(require_role(Role.ADMIN)),
):
    """Deletes a scoring parameter by ID.
    Requires ADMIN role.
    """
    deleted = await parameters_service.delete_parameter(db, parameter_id)

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Parameter not found",
        )

    return
