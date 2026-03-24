"""Dependency Injection Module

FastAPI dependencies for authentication and authorisation.
All functions in this module are intended to be injected into route handlers via Depends().
"""

from datetime import datetime, timedelta, timezone

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from src.config import settings
from src.database import get_db_session
from src.models.user import User
from src.schemas.user import Role, TokenData

# OAuth2 password bearer scheme for extracting JWT tokens from Authorization header
# Token URL points to the login endpoint that issues tokens
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    """Creates a JWT access token with timezone-aware expiration.

    Args:
        data: Dictionary of claims to encode in the token.
              Standard format: {"sub": str(user_id), "role": user_role}
        expires_delta: Optional custom expiration duration.
                      If not provided, uses ACCESS_TOKEN_EXPIRE_MINUTES from settings

    Returns:
        str: Encoded JWT token string ready for use in Authorization headers
    """
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db_session),
) -> User:
    """FastAPI dependency to extract and validate the current user from a JWT token.

    Args:
        token: JWT token extracted from the Authorization header by oauth2_scheme
        db: Async database session

    Returns:
        User: The authenticated user ORM object

    Raises:
        HTTPException: 401 Unauthorized if token is invalid, expired, or user not found
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id: int = payload.get("sub")
        if user_id is None:
            raise credentials_exception
        token_data = TokenData(id=user_id)
    except jwt.PyJWTError:
        raise credentials_exception

    result = await db.execute(select(User).filter(User.id == token_data.id))
    user = result.scalar_one_or_none()

    if user is None:
        raise credentials_exception
    return user


# Role hierarchy mapping: defines permission levels for each role.
# Higher numbers indicate greater permissions, enabling hierarchical access control
# where higher-level roles automatically have all permissions of lower-level roles.
role_hierarchy = {
    "officer": 1,
    "supervisor": 2,
    "admin": 3,
}


def require_ownership_or_admin(current_user: User, requested_user_id: int) -> None:
    """Raises 403 if an officer attempts to access another user's record.
    Supervisors and admins may access any record.
    """
    if current_user.role == Role.OFFICER.value and current_user.id != requested_user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this user",
        )


def require_role(required_role: Role):
    """FastAPI dependency factory for role-based access control.

    Creates a dependency that checks the authenticated user has sufficient
    permissions to access a protected endpoint.

    Args:
        required_role: The minimum role required to access the endpoint

    Returns:
        A dependency function that performs the role check and returns the current user

    Raises:
        HTTPException: 403 Forbidden if the user's role level is below the required level

    Usage:
        @router.get("/admin-only")
        async def admin_endpoint(user: User = Depends(require_role(Role.ADMIN))):
            pass
    """

    def role_checker(current_user: User = Depends(get_current_user)) -> User:
        user_role_level = role_hierarchy.get(current_user.role, 0)
        required_role_level = role_hierarchy.get(required_role.value, 0)

        if user_role_level < required_role_level:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="The user does not have adequate permissions.",
            )
        return current_user

    return role_checker
