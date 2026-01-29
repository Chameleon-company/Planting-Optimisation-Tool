"""
Dependency Injection Module

This module provides reusable FastAPI dependencies for authentication and authorization.
It includes JWT token creation, validation, and user retrieval functions.

This is the primary module for token-based authentication operations.
The authentication.py module in domains/ provides complementary functions.
"""

from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends, HTTPException, status, Security
from sqlalchemy.ext.asyncio import AsyncSession
import jwt
from jwt.exceptions import InvalidTokenError
from datetime import datetime, timedelta, timezone

from src.database import get_db_session
from src.schemas.user import UserRead
from src.services.user import get_user_by_id
from src.config import settings

# OAuth2 password bearer scheme for extracting JWT tokens from Authorization header
# Token URL points to the login endpoint that issues tokens
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    """
    Creates a JWT access token with timezone-aware expiration.

    This is the primary token creation function used throughout the application.
    It generates a signed JWT token containing user identification and claims.

    Args:
        data: Dictionary of claims to encode in the token.
              Standard format: {"sub": str(user_id), "role": user_role}
              - "sub" (subject): User ID as string (JWT standard)
              - "role": User's role for authorization checks
        expires_delta: Optional custom expiration duration.
                      If not provided, uses ACCESS_TOKEN_EXPIRE_MINUTES from settings

    Returns:
        str: Encoded JWT token string ready for use in Authorization headers

    Note:
        - Uses timezone-aware UTC datetime for proper expiration handling
        - Token expiration ("exp" claim) is automatically validated by PyJWT during decode
        - Tokens are signed with HMAC using the SECRET_KEY from application settings
        - The "sub" claim should be a string representation of the user ID (JWT standard)

    Example:
        token = create_access_token(
            data={"sub": "123", "role": "admin"}
        )
        # Returns: "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."

    Security:
        - Keep SECRET_KEY secure and rotate periodically
        - Use appropriate expiration times (shorter is more secure)
        - Consider using refresh tokens for long-lived sessions
    """
    to_encode = data.copy()

    # Use timezone-aware UTC for consistency and proper expiration handling
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )

    # Add expiration claim to token payload
    to_encode.update({"exp": expire})

    # Encode and sign the token
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


async def get_current_active_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db_session),
) -> UserRead:
    """
    FastAPI dependency to get the currently authenticated user from a JWT token.

    This is the primary authentication dependency used across the application.
    It extracts the JWT token from the Authorization header, validates it,
    and returns the authenticated user as a Pydantic schema.

    Args:
        token: JWT token extracted from "Authorization: Bearer <token>" header
               by the oauth2_scheme dependency
        db: Async database session for user lookup

    Returns:
        UserRead: Pydantic schema of the authenticated user (excludes password)

    Raises:
        HTTPException: 401 Unauthorized in these cases:
            - Token is missing or malformed
            - Token signature is invalid
            - Token has expired
            - User ID in token doesn't exist in database
            - Token lacks required "sub" (subject) claim

    Process Flow:
        1. Extract token from Authorization header (handled by oauth2_scheme)
        2. Decode and verify token signature
        3. Check token expiration (automatic in PyJWT)
        4. Extract user ID from "sub" claim
        5. Retrieve user from database
        6. Return user as UserRead schema

    Usage:
        @router.get("/protected")
        async def protected_endpoint(
            current_user: UserRead = Depends(get_current_active_user)
        ):
            return {"user": current_user.email}

    Note:
        - Returns UserRead (Pydantic schema) instead of User (SQLAlchemy model)
        - User ID is stored as string in token ("sub" claim) per JWT standard
        - PyJWT automatically validates expiration during decode
        - InvalidTokenError covers expired, malformed, and invalid signature cases

    Security:
        - Always use HTTPS in production to protect tokens in transit
        - Tokens are stateless (not stored server-side)
        - Compromised tokens remain valid until expiration
        - Consider implementing token blacklisting for logout functionality
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        # Decode and validate the JWT token
        # PyJWT automatically handles the 'exp' (expiration) check during decode
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )

        # Extract user ID from the "sub" (subject) claim
        user_id_str = payload.get("sub")
        if user_id_str is None:
            raise credentials_exception

        # Convert the string ID from the token to integer for database lookup
        user_id_int = int(user_id_str)

    except (InvalidTokenError, ValueError):
        # InvalidTokenError covers expired, malformed, or wrong-signature tokens
        # ValueError occurs if user ID can't be converted to integer
        raise credentials_exception
    except Exception:
        # Catch-all for other unexpected issues during token processing
        raise credentials_exception

    # Look up the user in the database by ID
    user = await get_user_by_id(db, user_id=user_id_int)
    if user is None:
        # User ID from token doesn't exist (user may have been deleted)
        raise credentials_exception

    # Convert SQLAlchemy model to Pydantic schema and return
    return UserRead.model_validate(user)


# Security dependency for use with FastAPI's Security() instead of Depends()
# Provides the same functionality as get_current_active_user but can be used
# in OpenAPI documentation to show security requirements
CurrentActiveUser = Security(get_current_active_user)
