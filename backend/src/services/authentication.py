"""Authentication Service

Pure service functions for user authentication and audit logging.
No FastAPI dependencies — these functions are called by routers or other services.
"""

from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from src.models.audit_log import AuditLog
from src.models.user import User
from src.utils.security import verify_password


async def authenticate_user(db: AsyncSession, email: str, password: str) -> Optional[User]:
    """Authenticates a user by verifying email and password.

    Args:
        db: Async database session
        email: User's email address
        password: Plain text password to verify

    Returns:
        User object if authentication succeeds, None otherwise
    """
    email = email.strip().lower()
    result = await db.execute(select(User).filter(User.email == email))
    user = result.scalar_one_or_none()

    if not user:
        return None

    if not verify_password(password, user.hashed_password):
        return None

    return user


async def log_audit_event(
    db: AsyncSession,
    user_id: int,
    event_type: str,
    details: str,
):
    """Records a security audit event to the database.

    Args:
        db: Async database session
        user_id: ID of the user who triggered the event
        event_type: Type of event (e.g., "user_create", "login", "role_change")
        details: Detailed description of the event
    """
    db_log = AuditLog(user_id=user_id, event_type=event_type, details=details)
    db.add(db_log)
    await db.commit()
