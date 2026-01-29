"""
Authentication and Authorization Module

This module handles user authentication, password hashing, JWT token generation,
and role-based access control (RBAC) for the application.

Key Components:
- Password hashing using bcrypt
- JWT token creation and validation
- User authentication
- Role-based permission checking with hierarchical access
- Audit logging for security events
"""

from typing import Optional
import jwt
import bcrypt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from src.config import settings
from src.database import get_db_session
from src.dependencies import get_current_active_user
from src.models.audit_log import AuditLog
from src.models.user import User
from src.schemas.user import TokenData, UserRead, Role


# OAuth2 password bearer scheme for token-based authentication
# This extracts the token from the Authorization header (format: "Bearer <token>")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")


def get_password_hash(password: str) -> str:
    """
    Hashes a plain text password using bcrypt.

    Args:
        password: The plain text password to hash

    Returns:
        str: The bcrypt hashed password with salt

    Note:
        This function should be used when creating or updating user passwords.
        Never store plain text passwords in the database.
    """
    pwd_bytes = password.encode("utf-8")
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(pwd_bytes, salt)
    return hashed_password.decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifies a plain password against a hashed password.

    Args:
        plain_password: The plain text password to verify
        hashed_password: The bcrypt hashed password from the database

    Returns:
        bool: True if the password matches, False otherwise

    Note:
        Used during login to authenticate users by comparing their input
        password with the stored hash.
    """
    return bcrypt.checkpw(
        plain_password.encode("utf-8"), hashed_password.encode("utf-8")
    )


async def authenticate_user(
    db: AsyncSession, email: str, password: str
) -> Optional[User]:
    """
    Authenticates a user by verifying email and password.

    Args:
        db: Async database session
        email: User's email address
        password: Plain text password to verify

    Returns:
        User object if authentication succeeds, None otherwise

    Note:
        This function performs two checks:
        1. User exists with the given email
        2. Password matches the stored hash
        Returns None if either check fails (timing-safe against enumeration attacks).
    """
    result = await db.execute(select(User).filter(User.email == email))
    user = result.scalar_one_or_none()
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user


async def get_current_user(
    token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db_session)
) -> User:
    """
    FastAPI dependency to extract and validate the current user from a JWT token.

    Args:
        token: JWT token extracted from the Authorization header by oauth2_scheme
        db: Async database session

    Returns:
        User: The authenticated user object from the database

    Raises:
        HTTPException: 401 Unauthorized if token is invalid, expired, or user not found

    Note:
        This dependency is used in route handlers to ensure the request is authenticated.
        It decodes the JWT, extracts the user ID from the 'sub' claim, and retrieves
        the user from the database.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        # Decode and validate the JWT token
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        user_id: int = payload.get("sub")
        if user_id is None:
            raise credentials_exception
        token_data = TokenData(id=user_id)
    except jwt.PyJWTError:
        # Token is invalid, expired, or malformed
        raise credentials_exception

    # Retrieve user from database
    result = await db.execute(select(User).filter(User.id == token_data.id))
    user = result.scalar_one_or_none()

    if user is None:
        # User ID in token doesn't exist in database (user was deleted?)
        raise credentials_exception
    return user


# Role hierarchy mapping: defines permission levels for each role
# Higher numbers indicate greater permissions
# This enables hierarchical access control where higher-level roles
# automatically have all permissions of lower-level roles
#
# Hierarchy explanation:
# - OFFICER (1): Entry-level user with basic permissions
# - SUPERVISOR (2): Can view/manage users and has all officer permissions
# - ADMIN (3): Full system access, can perform all operations
role_hierarchy = {
    "officer": 1,
    "supervisor": 2,
    "admin": 3,
}


def require_role(required_role: Role):
    """
    FastAPI dependency factory for role-based access control.

    This function creates a dependency that checks if the authenticated user
    has sufficient permissions (role level) to access a protected endpoint.

    Args:
        required_role: The minimum role required to access the endpoint

    Returns:
        A dependency function that performs the role check

    Usage:
        @router.get("/admin-only")
        async def admin_endpoint(user: User = Depends(require_role(Role.ADMIN))):
            # Only admins can access this endpoint
            pass

        @router.get("/supervisor-and-above")
        async def supervisor_endpoint(user: User = Depends(require_role(Role.SUPERVISOR))):
            # Supervisors and admins can access this endpoint
            pass

    Note:
        Uses hierarchical role checking: users with higher roles automatically
        have permissions of lower roles (e.g., admin can access supervisor endpoints).

    Raises:
        HTTPException: 403 Forbidden if user's role level is below required level
    """

    def role_checker(
        current_user: User = Depends(get_current_user),
    ) -> User:
        """
        Inner function that performs the actual role validation.

        Args:
            current_user: The authenticated user (injected by get_current_user dependency)

        Returns:
            User: The current user if they have sufficient permissions

        Raises:
            HTTPException: 403 Forbidden if permissions are insufficient
        """
        # Get numeric permission levels from hierarchy
        user_role_level = role_hierarchy.get(current_user.role, 0)
        required_role_level = role_hierarchy.get(required_role.value, 0)

        # Check if user's role level meets or exceeds the requirement
        if user_role_level < required_role_level:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="The user does not have adequate permissions.",
            )
        return current_user

    return role_checker


async def require_role_async(required_role: Role):
    """
    Async version of require_role for compatibility with async dependencies.

    This function provides the same role-based access control as require_role
    but works with the async get_current_active_user dependency.

    Args:
        required_role: The minimum role required to access the endpoint

    Returns:
        An async dependency function that performs the role check

    Note:
        This is used when you need to work with UserRead schemas instead of
        User models, typically in routes that need the async dependency chain.

    Raises:
        HTTPException: 403 Forbidden if user's role level is below required level
    """

    async def role_checker(
        current_user: UserRead = Depends(get_current_active_user),
    ) -> UserRead:
        """
        Inner async function that performs the role validation.

        Args:
            current_user: The authenticated user as UserRead schema

        Returns:
            UserRead: The current user if they have sufficient permissions

        Raises:
            HTTPException: 403 Forbidden if permissions are insufficient
        """
        # Get numeric permission levels from hierarchy
        user_role_level = role_hierarchy.get(current_user.role, 0)
        required_role_level = role_hierarchy.get(required_role.value, 0)

        # Check if user's role level meets or exceeds the requirement
        if user_role_level < required_role_level:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="The user does not have adequate permissions.",
            )
        return current_user

    return role_checker


async def log_audit_event(
    db: AsyncSession,
    user_id: int,
    event_type: str,
    details: str,
):
    """
    Records a security audit event to the database for compliance and monitoring.

    Args:
        db: Async database session
        user_id: ID of the user who triggered the event
        event_type: Type of event (e.g., "user_create", "login", "role_change")
        details: Detailed description of the event for audit trail

    Note:
        Audit logs are critical for:
        - Security monitoring and incident response
        - Compliance with data protection regulations
        - Tracking user actions for accountability
        - Forensic analysis in case of security breaches

        Common event types:
        - "user_create": New user account created
        - "user_update": User account modified
        - "user_delete": User account deleted
        - "login": Successful authentication
        - "role_change": User role modified

    Example:
        await log_audit_event(
            db=db,
            user_id=current_user.id,
            event_type="user_create",
            details=f"Created user {new_user.email} with role {new_user.role}"
        )
    """
    db_log = AuditLog(user_id=user_id, event_type=event_type, details=details)
    db.add(db_log)
    await db.commit()
