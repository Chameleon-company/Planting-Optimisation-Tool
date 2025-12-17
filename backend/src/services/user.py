from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from src.models.user import User


async def get_user_by_id(db: AsyncSession, user_id: int):
    """Retrieves a User ORM object by ID."""
    statement = select(User).where(User.id == user_id)
    result = await db.execute(statement)
    return result.scalar_one_or_none()
