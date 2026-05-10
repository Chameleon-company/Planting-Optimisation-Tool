from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_db_session
from src.dependencies import get_current_user, require_role
from src.schemas.farm import FarmBoundaryResponse, FarmCreate, FarmRead, FarmUpdate
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
    current_user: UserRead = Depends(require_role(Role.ADMIN)),
    # Inject the real database session
    db: AsyncSession = Depends(get_db_session),
):
    """Creates a new farm record with validated data.
    Requires ADMIN.
    """

    return await farm_service.create_farm_record(db=db, farm_data=farm_data, user_id=current_user.id)


# NOTE: When a farm boundary update endpoint is added, invalidate cached results for that farm:
#   await cache.invalidate(f"profile:{farm_id}", f"sapling:{farm_id}", f"rec:{farm_id}")


@router.get("/{farm_id}/boundary", response_model=FarmBoundaryResponse)
async def get_farm_boundary(
    farm_id: int,
    db: AsyncSession = Depends(get_db_session),
    current_user: UserRead = Depends(get_current_user),
):
    """
    Returns the farm boundary as a GeoJSON Feature. Requires any authenticated role.

    TODO: Officer-level ownership filtering is not applied here due to problems with the RBAC
    implementation.
    Officers are not directly associated with farms as owners in the current implementation.
    Restrict to owned farms once the RBAC implementation is complete.
    """
    boundary = await farm_service.get_farm_boundary(db, farm_id)
    if boundary is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Boundary not found for farm {farm_id}.")
    return boundary


@router.get("/{farm_id}", response_model=FarmRead)
async def read_farm(
    farm_id: int,
    db: AsyncSession = Depends(get_db_session),
    current_user: UserRead = Depends(get_current_user),
):
    """Retrieves a farm by ID.

    ADMIN: can read any farm
    SUPERVISOR: can read any farm
    OFFICER: can read only their own farm
    """

    farms = await farm_service.get_farm_by_id(db, farm_ids=[farm_id])

    if not farms:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Farm with ID {farm_id} not found.",
        )

    farm = farms[0]

    # ADMIN → allowed
    if current_user.role == Role.ADMIN:
        return farm

    # SUPERVISOR → allowed
    if current_user.role == Role.SUPERVISOR:
        return farm

    # OFFICER → only own farm
    if current_user.role == Role.OFFICER:
        if farm.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Farm not found.",
            )
        return farm


@router.put("/{farm_id}", response_model=FarmRead)
async def update_farm(
    farm_id: int,
    farm_data: FarmUpdate,
    db: AsyncSession = Depends(get_db_session),
    current_user: UserRead = Depends(get_current_user),
):
    """Updates a farm by ID.

    ADMIN: can update any farm
    SUPERVISOR: can update only their own farm
    OFFICER: cannot update farms
    """
    if current_user.role == Role.OFFICER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="The user does not have adequate permissions.",
        )

    existing_farms = await farm_service.get_farm_by_id(db, farm_ids=[farm_id])

    if not existing_farms:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Farm with ID {farm_id} not found.",
        )

    existing_farm = existing_farms[0]

    if current_user.role == Role.SUPERVISOR and existing_farm.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="The user does not have adequate permissions.",
        )

    updated_farm = await farm_service.update_farm_record(
        db=db,
        farm_id=farm_id,
        farm_data=farm_data,
    )

    return updated_farm


@router.delete("/{farm_id}", status_code=204)
async def delete_farm(
    farm_id: int,
    db: AsyncSession = Depends(get_db_session),
    current_user: UserRead = Depends(require_role(Role.ADMIN)),
):
    """Deletes a farm by ID.
    Requires ADMIN role.
    """
    deleted = await farm_service.delete_farm_record(db, farm_id)

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Farm with ID {farm_id} not found.",
        )

    return
