"""Authentication Service

Service functions for user authentication, authorization, and audit logging.
"""

import hashlib
import secrets
from datetime import datetime, timedelta, timezone
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.audit_log import AuditLog
from src.models.auth_token import AuthToken
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

    if not user.is_verified:
        raise ValueError("Email address has not been verified")

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


# =========================
# TOKEN HELPERS
# =========================


def generate_raw_token() -> str:
    return secrets.token_urlsafe(32)


def hash_token(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()


async def create_auth_token(
    db,
    user_id: int,
    token_type: str,
    expires_minutes: int = 10,
):
    raw_token = generate_raw_token()
    token_hash = hash_token(raw_token)

    expires_at = datetime.now(timezone.utc) + timedelta(minutes=expires_minutes)

    db_token = AuthToken(
        user_id=user_id,
        token_hash=token_hash,
        token_type=token_type,
        expires_at=expires_at,
    )

    db.add(db_token)
    await db.commit()
    await db.refresh(db_token)

    return raw_token


async def get_valid_token(db, token: str, token_type: str):
    token_hash = hash_token(token)

    result = await db.execute(
        select(AuthToken).where(
            AuthToken.token_hash == token_hash,
            AuthToken.token_type == token_type,
            AuthToken.used_at.is_(None),
            AuthToken.expires_at > datetime.now(timezone.utc),
        )
    )
    return result.scalar_one_or_none()


async def mark_token_used(db, token_obj: AuthToken):
    token_obj.used_at = datetime.now(timezone.utc)


async def invalidate_user_tokens(db, user_id: int, token_type: str):
    result = await db.execute(
        select(AuthToken).where(
            AuthToken.user_id == user_id,
            AuthToken.token_type == token_type,
            AuthToken.used_at.is_(None),
        )
    )
    tokens = result.scalars().all()

    now = datetime.now(timezone.utc)
    for token in tokens:
        token.used_at = now
