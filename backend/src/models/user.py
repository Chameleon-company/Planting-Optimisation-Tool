"""User Model

SQLAlchemy model representing users in the system with authentication and authorization.
Users have hierarchical roles (officer, supervisor, admin) that determine their permissions.
"""

# For type hinting only, not runtime
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database import Base
from src.models.association import farm_owners_association

if TYPE_CHECKING:
    from .auth_token import AuthToken
    from .farm import Farm


class User(Base):
    """User database model for authentication and authorization.

    Stores user credentials and role information for the planting optimization system.
    Users are assigned roles that determine their access level through a hierarchical
    permission system.

    Attributes:
        id: Primary key, unique identifier for the user
        name: User's full name (indexed for fast lookups)
        email: User's email address (unique, indexed, used for login)
        hashed_password: Bcrypt-hashed password (never store plain text!)
        role: User's role - one of: "officer", "supervisor", "admin" (indexed)
        is_approved: Whether an admin has approved this account for login
        requested_role: The role the user asked for at registration (admin context only)
        farms: Relationship to Farm model - farms supervised by this user

    Role Hierarchy:
        - officer (level 1): Basic user with limited permissions
        - supervisor (level 2): Can view/manage users and resources
        - admin (level 3): Full system access

    Relationships:
        - farms: Many-to-many relationship with Farm model through farm_supervisor

    Security Notes:
        - Passwords are hashed using bcrypt before storage
        - Email is used as the username for OAuth2 authentication
        - Role determines access via require_role() dependency
        - All user modifications should be audit logged
        - New registrations are created with is_approved=False and cannot log in
          until an admin approves them and assigns their effective role

    Database Schema:
        - Table name: users
        - Indexes on: name, email, role (for fast lookups)
        - Unique constraints on: email
    """

    __tablename__ = "users"

    # Primary key
    id: Mapped[int] = mapped_column(primary_key=True)

    # User information
    name: Mapped[str] = mapped_column(String(255), index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255))
    is_verified: Mapped[bool] = mapped_column(default=False, nullable=False)

    # Admin approval gate, users cannot log in until an admin approves them
    is_approved: Mapped[bool] = mapped_column(default=False, nullable=False)

    # The role the applicant requested at registration. The effective role lives
    # in "role" and is only ever assigned by an admin at approval time. Nullable so
    # pre-existing rows (and admin-created users) are unaffected.
    requested_role: Mapped[Optional[str]] = mapped_column(String(50), nullable=True, default=None)

    # Authorization - role determines user's permission level
    role: Mapped[str] = mapped_column(String(50), index=True, default="officer")

    # Relationships - farms supervised by this user
    farms: Mapped[List["Farm"]] = relationship(secondary=farm_owners_association, back_populates="owners")

    # Auth tokens (email verification / password reset) belonging to this user.
    # delete-orphan so removing a user cleans up their tokens and doesn't trip
    # the auth_tokens_user_id_fkey constraint.
    tokens: Mapped[List["AuthToken"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        """String representation for debugging."""
        return f"<User (id={self.id!r}, email='{self.email!r}', role='{self.role!r}')>"
