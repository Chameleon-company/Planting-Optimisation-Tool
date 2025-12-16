from pydantic import BaseModel, Field, EmailStr
from typing import Optional


# Base model for validation
class UserBase(BaseModel):
    email: EmailStr = Field(..., description="The user's unique email address.")
    name: str = Field(..., description="The user's full name.")


# Used for registration (requires password input)
class UserCreate(UserBase):
    password: str = Field(
        ...,
        min_length=8,
        description="The user's password (must be hashed before storage).",
    )


# This is what is returned after registration or when fetching the current user.
# NEVER INCLUDE PASSWORD
class UserRead(UserBase):
    id: int = Field(..., description="The unique database ID of the user.")

    class Config:
        from_attributes = True


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
