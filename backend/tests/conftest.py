import pytest
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.pool import NullPool
from src.database import get_db_session
from sqlalchemy.ext.asyncio import AsyncConnection  # noqa: F401
from httpx import AsyncClient, ASGITransport

# --- Application Imports ---
from src.config import Settings
from src.dependencies import create_access_token
from src.models.user import User
from src.models.soil_texture import SoilTexture
from src.main import app

settings = Settings()


# Event Loop
@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the session."""
    policy = asyncio.get_event_loop_policy()
    loop = policy.new_event_loop()
    yield loop
    loop.close()


# Database Engine
@pytest.fixture(scope="session")
async def db_engine():
    """Provides a single, asynchronous database engine for the session."""
    test_url = "postgresql+asyncpg://postgres:devpassword@localhost:5432/pot_test_db"
    engine = create_async_engine(test_url, poolclass=NullPool, query_cache_size=0)
    yield engine
    # Dispose of the engine resources after all tests run
    await engine.dispose()


# Database Setup Fixture
@pytest.fixture(scope="session", autouse=True)
async def setup_database(db_engine):
    yield


# Transactional Session Fixture
@pytest.fixture(scope="function")
async def async_session(db_engine):
    """
    Transactional session that rolls back after every test.
    Runs on replicated DB.
    """
    async with db_engine.connect() as connection:
        # Start the transaction
        transaction = await connection.begin()

        # Bind the session to the existing connection
        session = AsyncSession(bind=connection, expire_on_commit=False)

        yield session

        # Undo the transaction
        await session.close()
        await transaction.rollback()


@pytest.fixture(scope="function")
async def async_client(async_session):
    """HTTP client forced to use the test's transactional session."""

    # We define a nested function that FastAPI will call.
    # It returns the session object provided by the pytest fixture.
    async def _get_test_db():
        yield async_session

    # Link the override to your project's dependency name
    app.dependency_overrides[get_db_session] = _get_test_db

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        yield client

    # Clean up after the test so production code isn't affected
    app.dependency_overrides.clear()


# User Fixtures
@pytest.fixture(scope="function")
async def test_user_a(async_session: AsyncSession) -> User:
    """Fixture for creating User A (Owner) and persisting them."""
    user = User(
        name="Alice Owner", email="alice.test@farm.com", hashed_password="secure_hash_a"
    )
    user = await async_session.merge(user)
    await async_session.flush()
    await async_session.refresh(user)
    return user


@pytest.fixture(scope="function")
async def test_user_b(async_session: AsyncSession) -> User:
    """Fixture for creating User B (Intruder)."""
    user = User(
        name="Bob Intruder", email="bob.test@farm.com", hashed_password="secure_hash_b"
    )
    user = await async_session.merge(user)
    await async_session.flush()
    await async_session.refresh(user)
    return user


@pytest.fixture(scope="function")
async def setup_soil_texture(async_session: AsyncSession):
    """Ensures a SoilTexture record exists with a known ID for Farm FK constraints."""
    texture = SoilTexture(id=1, name="Test Loam")
    texture = await async_session.merge(texture)
    await async_session.flush()
    return texture


# Authorization Header Fixtures
@pytest.fixture(scope="function")
def auth_user_headers(test_user_a: User) -> dict:
    access_token = create_access_token(data={"sub": str(test_user_a.id)})
    return {"Authorization": f"Bearer {access_token}"}


@pytest.fixture(scope="function")
def auth_user_b_headers(test_user_b: User) -> dict:
    access_token = create_access_token(data={"sub": str(test_user_b.id)})
    return {"Authorization": f"Bearer {access_token}"}
