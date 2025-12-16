# conftest.py

import pytest
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.ext.asyncio import AsyncConnection  # noqa: F401

# Import your application components
from src.config import Settings
from src.database import Base

settings = Settings()


# --- Fixture 1: Event Loop ---
@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


# --- Fixture 2: Database Engine (Session Scope) ---
@pytest.fixture(scope="function")
async def db_engine():
    """Provides a single, asynchronous database engine for the session."""
    engine = create_async_engine(settings.DATABASE_URL)
    yield engine
    # Dispose of the engine resources after all tests run
    await engine.dispose()


# --- 3. Database Setup/Teardown Fixture (Session Scope, Autoused) ---
@pytest.fixture(scope="function", autouse=True)
async def setup_database(db_engine):
    """
    Creates all tables before any test runs and drops them after all tests complete.
    """
    async with db_engine.begin() as conn:
        # Create all tables defined in Base.metadata
        await conn.run_sync(Base.metadata.create_all)

    yield

    async with db_engine.begin() as conn:
        # Drop all tables after all tests are complete
        await conn.run_sync(Base.metadata.drop_all)


# --- 4. Transactional Session Fixture (Function Scope - Guarantees Isolation) ---
@pytest.fixture(scope="function")
async def async_session(db_engine):
    """
    Provides a transactional async session that guarantees a clean database state
    for every single test function by rolling back the transaction afterward.
    """
    # Acquire a connection and start a transaction block
    async with db_engine.begin() as conn:
        # Bind a session to the connection/transaction
        session = AsyncSession(conn, expire_on_commit=False)

        try:
            # Yield the session to the test function
            yield session
        finally:
            # Close the session
            await session.close()
            # Rollback the transaction to discard all changes made during the test
            await conn.rollback()
