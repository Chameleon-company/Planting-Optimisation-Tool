import asyncio
from sqlalchemy import select
from src.database import AsyncSessionLocal, engine
from src.models.user import User

# We don't have password functionality yet, using plaintext
# from src.auth.utils import get_password_hash


async def create_user():
    async with AsyncSessionLocal() as session:
        email = "testuser123@test.com"
        # Check if user already exists
        result = await session.execute(select(User).where(User.email == email))
        existing_user = result.scalar_one_or_none()

        if existing_user:
            print(f"User '{email}' already exists.")
            return

        user = User(
            name="Test User",
            email=email,
            hashed_password="password123",
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
