"""
User Model

SQLAlchemy model representing users in the system with authentication and authorization.
Users have hierarchical roles (officer, supervisor, admin) that determine their permissions.
"""

from typing import List
from sqlalchemy import ForeignKey
from sqlalchemy import String
from src.database import Base
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship

# For type hinting only, not runtime
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .farm import Farm


class User(Base):
    """
    User database model for authentication and authorization.

    Stores user credentials and role information for the planting optimization system.
    Users are assigned roles that determine their access level through a hierarchical
    permission system.

    Attributes:
        id: Primary key, unique identifier for the user
        name: User's full name (unique, indexed for fast lookups)
        email: User's email address (unique, indexed, used for login)
        hashed_password: Bcrypt-hashed password (never store plain text!)
        role: User's role - one of: "officer", "supervisor", "admin" (indexed)
        farms: Relationship to Farm model - farms supervised by this user

    Role Hierarchy:
        - officer (level 1): Basic user with limited permissions
        - supervisor (level 2): Can view/manage users and resources
        - admin (level 3): Full system access

    Relationships:
        - farms: One-to-many relationship with Farm model through farm_supervisor

    Security Notes:
        - Passwords are hashed using bcrypt before storage
        - Email is used as the username for OAuth2 authentication
        - Role determines access via require_role() dependency
        - All user modifications should be audit logged

    Database Schema:
        - Table name: users
        - Indexes on: name, email, role (for fast lookups)
        - Unique constraints on: name, email
    """

    __tablename__ = "users"

    # Primary key
    id: Mapped[int] = mapped_column(primary_key=True)

    # User information
    name: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255))

    # Authorization - role determines user's permission level
    role: Mapped[str] = mapped_column(String(50), index=True, default="officer")

    # Relationships - farms supervised by this user
    farms: Mapped[List["Farm"]] = relationship(back_populates="farm_supervisor")

    def __repr__(self) -> str:
        """String representation for debugging."""
        return f"<User (id={self.id!r}, email='{self.email!r}', role='{self.role!r}')>"
