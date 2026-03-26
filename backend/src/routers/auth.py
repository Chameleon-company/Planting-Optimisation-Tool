"""Authentication Router

This module provides API endpoints for user authentication and authorization:
- Token-based login (OAuth2 password flow)
- User registration
- Current user information retrieval

All endpoints use JWT tokens for stateless authentication.
"""

from typing import List

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_db_session
from src.dependencies import create_access_token, get_current_user, limiter, require_role
from src.models import User
from src.schemas.farm import FarmRead
from src.schemas.user import Role, Token, UserCreate, UserRead
from src.services import authentication as authentication_service
from src.services import farm as farm_service
from src.services import user as user_service

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/token", response_model=Token)
@limiter.limit("10/minute")
async def login_for_access_token(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db_session),
):
    """OAuth2 compatible token login endpoint.

    Authenticates a user using email (as username) and password, then returns
    a JWT access token for subsequent API requests.

    Args:
        form_data: OAuth2 form containing username (email) and password
        db: Database session

    Returns:
        Token response containing access_token and token_type

    Raises:
        HTTPException: 401 if credentials are invalid

    Example:
        POST /auth/token
        Content-Type: application/x-www-form-urlencoded

        username=user@example.com&password=secretpassword

        Response:
        {
            "access_token": "eyJhbGc...",
            "token_type": "bearer"
        }
    """
    user = await authentication_service.authenticate_user(db, email=form_data.username, password=form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    # Create JWT token with user ID and role in the payload
    access_token = create_access_token(data={"sub": str(user.id), "role": user.role})
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/register", response_model=UserRead)
@limiter.limit("10/minute")
async def register_user(request: Request, user: UserCreate, db: AsyncSession = Depends(get_db_session)):
    """Register a new user account.

    Creates a new user with the provided email, name, password, and role.
    This is a public endpoint that allows self-registration.

    Args:
        user: User creation data (email, name, password, role)
        db: Database session

    Returns:
        UserRead: The created user (without password)

    Raises:
        HTTPException: 400 if email is already registered

    Note:
        - Passwords are hashed before storage using bcrypt
        - Default role is "officer" if not specified
        - The password field is never returned in the response
        - For production, you may want to restrict which roles can self-register
          or require email verification

    Example:
        POST /auth/register
        {
            "email": "newuser@example.com",
            "name": "John Doe",
            "password": "securepassword123",
            "role": "officer"
        }
    """
    try:
        return await user_service.create_user(db, user)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.get("/users/me", response_model=UserRead)
async def read_users_me(current_user: User = Depends(get_current_user)):
    """Get the currently authenticated user's information.

    Returns the profile of the user making the request based on their JWT token.

    Args:
        current_user: Authenticated user (injected from JWT token)

    Returns:
        UserRead: Current user's profile information

    Requires:
        Valid JWT token in Authorization header

    Example:
        GET /auth/users/me
        Authorization: Bearer eyJhbGc...

        Response:
        {
            "id": 1,
            "email": "user@example.com",
            "name": "John Doe",
            "role": "officer"
        }
    """
    return current_user


@router.get("/users/me/items", response_model=List[FarmRead])
async def read_own_items(
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(require_role(Role.OFFICER)),
):
    """Returns all farms associated with the currently authenticated user."""
    return await farm_service.list_farms_by_user(db, current_user.id)
