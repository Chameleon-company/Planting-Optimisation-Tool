import asyncio
from sqlalchemy import select
from src.database import AsyncSessionLocal, engine
from src.models.user import User
from src.services.authentication import get_password_hash


async def create_user():
    async with AsyncSessionLocal() as session:
        email = "testuser123@test.com"
        # Check if user already exists
        result = await session.execute(select(User).where(User.email == email))
        existing_user = result.scalar_one_or_none()

        if existing_user:
            print(f"User '{email}' already exists.")
            return

        # Create test user with ADMIN role
        # Admin role grants full system access including:
        # - Create/read/update/delete all resources
        # - Manage users with any role (officer, supervisor, admin)
        # - Can view and create farms regardless of ownership
        user = User(
            name="Test User",
            email=email,
            hashed_password=get_password_hash("password123"),
            role="admin",  # ADMIN role for full access during testing
        )

        session.add(user)
        try:
            await session.commit()
            print(f"User {email} created successfully.")
        except Exception as e:
            await session.rollback()
            print(f"Error: {e}")


async def main():
    try:
        await create_user()
    finally:
        await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
