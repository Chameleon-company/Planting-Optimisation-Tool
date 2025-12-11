# SQLAlchemy engine
from sqlalchemy.ext.asyncio import (
    create_async_engine,
    async_sessionmaker,
    AsyncSession,
)  # Required for asynchronous sessions and engine creation
from sqlalchemy.orm import DeclarativeBase
from typing import AsyncGenerator
from .config import settings  # import the settings object from config.py


class Base(DeclarativeBase):
    """
    All SQLAlchemy models inherit from this base class.
    """

    pass


engine = create_async_engine(settings.DATABASE_URL, echo=False, plugins=["geoalchemy2"])

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    autoflush=False,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """Provides a fresh, isolated database session for each API request."""
    db = AsyncSessionLocal()
    try:
        yield db
    finally:
        await db.close()
