import pytest
from sqlalchemy import text
from src.config import Settings
from sqlalchemy.ext.asyncio import AsyncEngine  # Import the engine type


# Instantiate settings once for testing purposes
settings = Settings()


@pytest.mark.asyncio
async def test_database_url_is_set():
    """Verify that the DATABASE_URL environment variable is set"""
    assert settings.DATABASE_URL.startswith("postgresql+asyncpg://")
    assert "POT_db" in settings.DATABASE_URL


@pytest.mark.asyncio
async def test_database_connection_success(db_engine: AsyncEngine):
    """Test if a connection can be made to the running DB container."""
    # The engine is provided by the session-scoped fixture in conftest.py
    engine = db_engine

    try:
        # Connect and execute a simple, non-destructive query
        async with engine.connect() as conn:
            # Execute a basic query to prove the connection works
            result = await conn.execute(text("SELECT 1"))
            assert result.scalar_one() == 1

    except Exception as e:
        pytest.fail(f"Failed to connect to the database: {e}")

    # NOTE: engine.dispose() is called by the db_engine fixture (in conftest.py)
    # after the entire test session is complete.
