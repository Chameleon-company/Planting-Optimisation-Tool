"""
Creates 10 admin users for load testing.

Usage:
    cd backend
    uv run python locust/seed_users.py
"""

import asyncio

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.pool import NullPool

from src.config import settings
from src.models.user import User
from src.schemas.user import Role
from src.utils.security import get_password_hash

USER_COUNT = 10
PASSWORD = "Loadtest123!"


async def seed():
    engine = create_async_engine(settings.DATABASE_URL, poolclass=NullPool)

    async with AsyncSession(engine) as session:
        for i in range(1, USER_COUNT + 1):
            email = f"loadtest_{i:02d}@test.com"
            result = await session.execute(select(User).where(User.email == email))
            existing = result.scalar_one_or_none()
            if existing:
                existing.hashed_password = get_password_hash(PASSWORD)
                print(f"  updated: {email}")
                continue
            session.add(
                User(
                    name=f"Load Test User {i:02d}",
                    email=email,
                    hashed_password=get_password_hash(PASSWORD),
                    role=Role.ADMIN.value,
                    is_verified=True,
                )
            )
            print(f"  created: {email}")

        await session.commit()

    await engine.dispose()
    print("Seeding complete.")


if __name__ == "__main__":
    asyncio.run(seed())
