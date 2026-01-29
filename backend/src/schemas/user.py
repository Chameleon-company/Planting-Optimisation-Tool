from pydantic import BaseModel, Field, EmailStr, ConfigDict, field_validator
from typing import Optional

from src.schemas.constants import Role

# Re-export Role for backward compatibility
__all__ = [
    "Role",
    "UserBase",
    "UserCreate",
    "UserRead",
    "UserLogin",
    "Token",
    "TokenData",
]


# Base model for validation
class UserBase(BaseModel):
    email: EmailStr = Field(..., description="The user's unique email address.")
    name: str = Field(..., description="The user's full name.")


# Used for registration (requires password input)
class UserCreate(UserBase):
    password: str = Field(
        ...,
        description="The user's password (must be hashed before storage).",
    )
    role: str = "officer"

    @field_validator("password")
    @classmethod
    def password_min_length(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters long")
        return v


# This is what is returned after registration or when fetching the current user.
# NEVER INCLUDE PASSWORD
class UserRead(UserBase):
    id: int = Field(..., description="The unique database ID of the user.")
    role: str = Field(..., description="The user's role.")

    model_config = ConfigDict(from_attributes=True)


# Used for authentication requests
class UserLogin(BaseModel):
    email: EmailStr
    password: str


# Token (The contract for what the login endpoint returns)
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """Schema for the JWT payload validation."""

    id: Optional[int] = None  # The user ID stored in the token's subject (sub) field
    role: Optional[str] = None
