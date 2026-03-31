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
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.config import settings
from src.database import get_db_session
from src.dependencies import create_access_token, get_current_user, limiter, require_role
from src.models import User
from src.schemas.auth import ForgotPasswordRequest, ResetPasswordRequest, VerifyEmailRequest
from src.schemas.farm import FarmRead
from src.schemas.user import Role, Token, UserCreate, UserRead
from src.services import authentication as authentication_service
from src.services import farm as farm_service
from src.services.authentication import (
    create_auth_token,
    get_valid_token,
    invalidate_user_tokens,
    mark_token_used,
)
from src.services.email_service import send_email
from src.utils.security import get_password_hash, validate_password

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
    try:
        user = await authentication_service.authenticate_user(db, email=form_data.username, password=form_data.password)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    # Create JWT token with user ID and role in the payload
    access_token = create_access_token(data={"sub": str(user.id), "role": user.role})
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/register")
@limiter.limit("10/minute")
async def register_user(request: Request, user: UserCreate, db: AsyncSession = Depends(get_db_session)):
    """Register a new user account."""

    normalized_email = user.email.strip().lower()

    result = await db.execute(select(User).filter(User.email == normalized_email))
    existing_user = result.scalar_one_or_none()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    hashed_password = get_password_hash(user.password)

    db_user = User(
        email=normalized_email,
        name=user.name,
        hashed_password=hashed_password,
        role=user.role,
        is_verified=False,
    )
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)

    token = await create_auth_token(
        db,
        user_id=db_user.id,
        token_type="email_verification",
        expires_minutes=settings.email_verification_expiry_minutes,
    )

    verification_link = f"{settings.frontend_base_url}/verify-email?token={token}"

    await send_email(
        subject="Verify your account",
        recipient=db_user.email,
        body=f"Click this link to verify your account:\n{verification_link}",
    )

    return {"message": "User registered. Verification email sent."}


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
    """Returns all farms associated with the currently authenticated user.

    Example endpoint demonstrating officer-or-above access.

    This is a placeholder endpoint showing how to restrict access to users
    with the OFFICER role (or higher). In production, replace with actual
    business logic.

    Args:
        current_user: Authenticated user with role OFFICER or higher

    Returns:
        List of items owned by the current user

    Requires:
        Valid JWT token with role OFFICER or higher

    Note:
        This endpoint is restricted to users with role OFFICER or higher.
        Users with lower privileges will receive a 403 Forbidden response.
    """
    return await farm_service.list_farms_by_user(db, current_user.id)


@router.post("/verify-email")
async def verify_email(
    request: VerifyEmailRequest,
    db: AsyncSession = Depends(get_db_session),
):
    token_obj = await get_valid_token(
        db,
        token=request.token,
        token_type="email_verification",
    )

    if not token_obj:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired token",
        )

    # Get user
    result = await db.execute(select(User).filter(User.id == token_obj.user_id))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    # Mark user verified
    user.is_verified = True

    # Mark token used
    await mark_token_used(db, token_obj)

    await db.commit()

    return {"message": "Email verified successfully"}


@router.post("/forgot-password")
async def forgot_password(
    request: ForgotPasswordRequest,
    db: AsyncSession = Depends(get_db_session),
):
    normalized_email = request.email.strip().lower()
    result = await db.execute(select(User).filter(User.email == normalized_email))
    user = result.scalar_one_or_none()

    if user:
        await invalidate_user_tokens(db, user.id, "password_reset")

        token = await create_auth_token(
            db,
            user_id=user.id,
            token_type="password_reset",
            expires_minutes=settings.password_reset_expiry_minutes,
        )

        reset_link = f"{settings.frontend_base_url}/reset-password?token={token}"

        await send_email(
            subject="Reset your password",
            recipient=user.email,
            body=f"Click this link to reset your password:\n{reset_link}",
        )

    return {"message": "If an account with that email exists, a password reset email has been sent."}


@router.post("/reset-password")
async def reset_password(
    request: ResetPasswordRequest,
    db: AsyncSession = Depends(get_db_session),
):
    token_obj = await get_valid_token(
        db,
        token=request.token,
        token_type="password_reset",
    )

    if not token_obj:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired token",
        )

    result = await db.execute(select(User).filter(User.id == token_obj.user_id))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    validate_password(request.new_password)
    user.hashed_password = get_password_hash(request.new_password)

    await mark_token_used(db, token_obj)
    await db.commit()

    return {"message": "Password reset successfully"}
