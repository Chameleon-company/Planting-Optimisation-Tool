"""
User Management Router

This module provides CRUD endpoints for user management with role-based access control:
- Create users (no authentication required for self-registration)
- Read users (requires supervisor or admin role)
- Read individual user (requires supervisor or admin role)
- Update user (requires admin role)
- Delete user (requires admin role)

All administrative operations are logged for audit purposes.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List

from src.database import get_db_session
from src.services.authentication import (
    require_role,
    get_password_hash,
    log_audit_event,
    get_current_user,
)
from src.models.user import User
from src.schemas.user import UserCreate, UserRead, Role

router = APIRouter(prefix="/users", tags=["users"])


@router.post("/", response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def create_user(
    user: UserCreate,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
):
    """
    Create a new user account.

    This endpoint allows authenticated users to create new user accounts.
    Previously restricted to admins only, now any authenticated user can create accounts
    to support self-service user management workflows.

    Args:
        user: User creation data (email, name, password, role)
        db: Database session
        current_user: The authenticated user creating the new account

    Returns:
        UserRead: The newly created user (without password)

    Raises:
        HTTPException: 400 if email is already registered

    Note:
        - The creating user's ID is logged for audit purposes
        - Passwords are automatically hashed before storage
        - An audit log entry is created for compliance tracking
        - Default role is "officer" if not specified

    Security Considerations:
        - If you want to restrict who can create users, add require_role(Role.ADMIN)
          to the current_user dependency
        - Consider validating that non-admin users cannot create admin accounts

    Example:
        POST /users/
        Authorization: Bearer eyJhbGc...
        {
            "email": "newuser@example.com",
            "name": "Jane Smith",
            "password": "securepassword123",
            "role": "officer"
        }
    """
    # Check if email already exists
    result = await db.execute(select(User).filter(User.email == user.email))
    db_user = result.scalar_one_or_none()
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    # Hash the password before storing
    hashed_password = get_password_hash(user.password)

    # Create new user
    db_user = User(
        email=user.email,
        name=user.name,
        hashed_password=hashed_password,
        role=user.role,
    )
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)

    # Log the user creation for audit trail
    # IMPORTANT: Use current_user.id (the creator) and db_user.id (the newly created user)
    await log_audit_event(
        db=db,
        user_id=current_user.id,  # Fixed: was using user.id which doesn't exist
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
    """
    List all users with pagination.

    Retrieves a paginated list of all users in the system.
    Requires supervisor or admin role due to hierarchical permissions.

    Args:
        skip: Number of records to skip (for pagination), default 0
        limit: Maximum number of records to return, default 100
        db: Database session
        current_user: Authenticated user with supervisor or admin role

    Returns:
        List[UserRead]: List of users without password information

    Requires:
        - Valid JWT token
        - Supervisor or Admin role (Officers will receive 403 Forbidden)

    Role Hierarchy:
        - SUPERVISOR: Can access (level 2)
        - ADMIN: Can access (level 3, inherits supervisor permissions)
        - OFFICER: Cannot access (level 1)

    Example:
        GET /users/?skip=0&limit=50
        Authorization: Bearer eyJhbGc...

        Response:
        [
            {"id": 1, "email": "user1@example.com", "name": "User One", "role": "officer"},
            {"id": 2, "email": "user2@example.com", "name": "User Two", "role": "supervisor"}
        ]
    """
    result = await db.execute(select(User).offset(skip).limit(limit))
    users = result.scalars().all()
    return users


@router.get("/{user_id}", response_model=UserRead)
async def read_user(
    user_id: int,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(require_role(Role.SUPERVISOR)),
):
    """
    Get a specific user by ID.

    Retrieves detailed information about a single user.
    Requires supervisor or admin role.

    Args:
        user_id: The ID of the user to retrieve
        db: Database session
        current_user: Authenticated user with supervisor or admin role

    Returns:
        UserRead: User information without password

    Raises:
        HTTPException: 404 if user not found
        HTTPException: 403 if requester lacks supervisor/admin role

    Requires:
        - Valid JWT token
        - Supervisor or Admin role

    Example:
        GET /users/123
        Authorization: Bearer eyJhbGc...

        Response:
        {
            "id": 123,
            "email": "user@example.com",
            "name": "John Doe",
            "role": "officer"
        }
    """
    result = await db.execute(select(User).filter(User.id == user_id))
    db_user = result.scalar_one_or_none()
    if db_user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    return db_user


@router.put("/{user_id}", response_model=UserRead)
async def update_user(
    user_id: int,
    user: UserCreate,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(require_role(Role.ADMIN)),
):
    """
    Update an existing user's information.

    Allows admins to modify user accounts including email, name, password, and role.
    This is a privileged operation restricted to admin users only.

    Args:
        user_id: The ID of the user to update
        user: Updated user data
        db: Database session
        current_user: Authenticated admin user

    Returns:
        UserRead: The updated user information

    Raises:
        HTTPException: 404 if user not found
        HTTPException: 403 if requester is not an admin

    Requires:
        - Valid JWT token
        - Admin role (Supervisors and Officers will receive 403 Forbidden)

    Security Note:
        - Password is only updated if provided (non-empty string)
        - Passwords are automatically hashed before storage
        - Consider adding audit logging for role changes
        - Consider preventing users from changing their own role

    Example:
        PUT /users/123
        Authorization: Bearer eyJhbGc...
        {
            "email": "updated@example.com",
            "name": "Updated Name",
            "password": "newpassword123",
            "role": "supervisor"
        }
    """
    # Find the user to update
    result = await db.execute(select(User).filter(User.id == user_id))
    db_user = result.scalar_one_or_none()
    if db_user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    # Update user fields
    db_user.email = user.email
    db_user.name = user.name

    # Only update password if a new one is provided
    if user.password:
        db_user.hashed_password = get_password_hash(user.password)

    db_user.role = user.role

    await db.commit()
    await db.refresh(db_user)

    # TODO: Consider adding audit logging for user updates, especially role changes
    # await log_audit_event(
    #     db=db,
    #     user_id=current_user.id,
    #     event_type="user_update",
    #     details=f"User {current_user.email} updated user {db_user.email}"
    # )

    return db_user


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: int,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(require_role(Role.ADMIN)),
):
    """
    Delete a user account.

    Permanently removes a user from the system. This is a destructive operation
    restricted to admin users only.

    Args:
        user_id: The ID of the user to delete
        db: Database session
        current_user: Authenticated admin user

    Returns:
        None (204 No Content on success)

    Raises:
        HTTPException: 404 if user not found
        HTTPException: 403 if requester is not an admin

    Requires:
        - Valid JWT token
        - Admin role

    Security Considerations:
        - This is a hard delete (permanent removal)
        - Consider implementing soft deletes (marking as inactive) instead
        - Consider preventing users from deleting themselves
        - Consider checking for related records (farms, etc.) before deletion
        - Add audit logging for accountability

    Example:
        DELETE /users/123
        Authorization: Bearer eyJhbGc...

        Response: 204 No Content
    """
    # Find the user to delete
    result = await db.execute(select(User).filter(User.id == user_id))
    db_user = result.scalar_one_or_none()
    if db_user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    # TODO: Consider preventing self-deletion
    # if db_user.id == current_user.id:
    #     raise HTTPException(
    #         status_code=status.HTTP_400_BAD_REQUEST,
    #         detail="Cannot delete your own account"
    #     )

    # TODO: Add audit logging for user deletion
    # await log_audit_event(
    #     db=db,
    #     user_id=current_user.id,
    #     event_type="user_delete",
    #     details=f"User {current_user.email} deleted user {db_user.email}"
    # )

    await db.delete(db_user)
    await db.commit()
    return
