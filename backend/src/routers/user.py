"""User Management Router

CRUD endpoints for user management with role-based access control.
All business logic is delegated to services.user.
"""

from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_db_session
from src.dependencies import get_current_user, require_ownership_or_admin, require_role
from src.models.user import User
from src.schemas.user import Role, UserApprove, UserCreate, UserRead, UserUpdate
from src.services import authentication as authentication_service
from src.services import user as user_service

router = APIRouter(prefix="/users", tags=["users"])


def mask_name(user: User, viewer_id: int, *, reveal: bool = False) -> UserRead:
    data = UserRead.model_validate(user)
    if not reveal and user.id != viewer_id:
        return data.model_copy(update={"name": None})
    return data


@router.post("/", response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def create_user(
    user: UserCreate,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(require_role(Role.ADMIN)),
):
    try:
        db_user = await user_service.create_user(db, user)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    await authentication_service.log_audit_event(
        db=db,
        user_id=current_user.id,
        event_type="user_create",
        details=f"User {current_user.email} created user {db_user.email} with role {db_user.role}",
    )
    return db_user


@router.get("/", response_model=List[UserRead])
async def read_users(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(require_role(Role.SUPERVISOR)),
):
    users = await user_service.list_users(db, skip, limit)
    return [mask_name(u, current_user.id) for u in users]


@router.get("/pending", response_model=List[UserRead])
async def read_pending_users(
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(require_role(Role.ADMIN)),
):
    """Returns all users awaiting admin approval."""
    users = await user_service.list_pending_users(db)
    return [mask_name(u, current_user.id) for u in users]


@router.get("/{user_id}", response_model=UserRead)
async def read_user(
    user_id: int,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
):
    require_ownership_or_admin(current_user, user_id)

    db_user = await user_service.get_user_by_id(db, user_id)
    if db_user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return mask_name(db_user, current_user.id)


@router.put("/{user_id}", response_model=UserRead)
async def update_user(
    user_id: int,
    user: UserUpdate,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(require_role(Role.ADMIN)),
):
    try:
        db_user = await user_service.update_user(db, user_id, user)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    if db_user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return db_user


@router.post("/{user_id}/approve", response_model=UserRead)
async def approve_user(
    user_id: int,
    payload: UserApprove,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(require_role(Role.ADMIN)),
):
    """Approves a pending registration and assigns the effective role."""
    db_user = await user_service.get_user_by_id(db, user_id)
    if db_user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    if db_user.is_approved:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User is already approved",
        )

    db_user = await user_service.approve_user(db, user_id, payload.role)

    await authentication_service.log_audit_event(
        db=db,
        user_id=current_user.id,
        event_type="user_approve",
        details=f"User {current_user.email} approved {db_user.email} with role {db_user.role}",
    )
    return db_user


@router.post("/{user_id}/reject", status_code=status.HTTP_204_NO_CONTENT)
async def reject_user(
    user_id: int,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(require_role(Role.ADMIN)),
):
    """Rejects a pending registration by deleting the record.

    Refuses to act on an already-approved account; use DELETE for those.
    """
    db_user = await user_service.get_user_by_id(db, user_id)
    if db_user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    if db_user.is_approved:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot reject an already-approved user; use delete instead",
        )

    rejected_email = db_user.email
    await user_service.delete_user(db, user_id)

    await authentication_service.log_audit_event(
        db=db,
        user_id=current_user.id,
        event_type="user_reject",
        details=f"User {current_user.email} rejected registration for {rejected_email}",
    )


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: int,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(require_role(Role.ADMIN)),
):
    deleted = await user_service.delete_user(db, user_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
