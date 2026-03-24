from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.user import User
from src.schemas.user import UserCreate, UserUpdate
from src.utils.security import get_password_hash


async def get_user_by_id(db: AsyncSession, user_id: int):
    """Retrieves a User ORM object by ID."""
    result = await db.execute(select(User).where(User.id == user_id))
    return result.scalar_one_or_none()


async def create_user(db: AsyncSession, user: UserCreate) -> User:
    """Creates a new user. Raises ValueError if the email is already registered."""
    normalized_email = user.email.strip().lower()
    result = await db.execute(select(User).filter(User.email == normalized_email))
    if result.scalar_one_or_none():
        raise ValueError("Email already registered")

    db_user = User(
        email=normalized_email,
        name=user.name,
        hashed_password=get_password_hash(user.password),
        role=user.role,
    )
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user


async def list_users(db: AsyncSession, skip: int = 0, limit: int = 100) -> list[User]:
    """Returns a paginated list of all users."""
    result = await db.execute(select(User).offset(skip).limit(limit))
    return list(result.scalars().all())


async def update_user(db: AsyncSession, user_id: int, user: UserUpdate) -> User | None:
    """Updates an existing user. Returns None if the user does not exist."""
    result = await db.execute(select(User).filter(User.id == user_id))
    db_user = result.scalar_one_or_none()
    if db_user is None:
        return None

    if user.email is not None:
        if user.email != db_user.email:
            dup = await db.execute(select(User).filter(User.email == user.email, User.id != user_id))
            if dup.scalar_one_or_none():
                raise ValueError("Email already registered")
        db_user.email = user.email
    if user.name is not None:
        db_user.name = user.name
    if user.password is not None:
        db_user.hashed_password = get_password_hash(user.password)
    if user.role is not None:
        db_user.role = user.role

    await db.commit()
    await db.refresh(db_user)
    return db_user


async def delete_user(db: AsyncSession, user_id: int) -> bool:
    """Deletes a user by ID. Returns False if the user does not exist."""
    result = await db.execute(select(User).filter(User.id == user_id))
    db_user = result.scalar_one_or_none()
    if db_user is None:
        return False

    await db.delete(db_user)
    await db.commit()
    return True
