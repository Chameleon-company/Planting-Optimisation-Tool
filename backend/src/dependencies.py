from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends, HTTPException, status, Security
from sqlalchemy.ext.asyncio import AsyncSession
from jose import jwt, JWTError
from pydantic import ValidationError


from src.database import get_db_session
from src.schemas.user import UserRead, TokenData
from src.services.user import get_user_by_id
from src.config import settings


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")


# This dependency is used to fetch the currently authenticated user from the token.
async def get_current_active_user(
    # Reads the token from the Authorization header (Bearer <token>)
    token: str = Depends(oauth2_scheme),
    # Gets the database session
    db: AsyncSession = Depends(get_db_session),
) -> UserRead:
    """
    Validates the JWT token, extracts the user ID, and fetches the User ORM object
    from the database, returning it as a UserRead Pydantic model.
    """

    # Define a generic exception for failed authentication
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        # Decode and Validate the JWT
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )

        # Extract and validate the user ID
        user_id = payload.get("sub")

        # Ensure the payload structure is correct
        if user_id is None:
            raise credentials_exception

        # Pydantic validation of the token payload
        token_data = TokenData(id=payload.get("sub"))
        if token_data.id is None:
            raise credentials_exception

    except (JWTError, ValidationError, ValueError):
        # Catches bad signatures, expired tokens, or invalid data types
        raise credentials_exception

    # Look up the user in the database
    # This returns the User ORM object, which FastAPI will serialize to UserRead
    user = await get_user_by_id(db, user_id=token_data.id)

    if user is None:
        raise credentials_exception

    return UserRead.model_validate(user)


# An alias for cleaner router code when authentication is mandatory
CurrentActiveUser = Security(get_current_active_user)
