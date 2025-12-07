import pytest
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text
from src.config import Settings

# Instantiate settings once for testing purposes
settings = Settings()


@pytest.mark.asyncio
async def test_database_url_is_set():
    """Verify that the DATABASE_URL environment variable is set"""
    assert settings.DATABASE_URL.startswith("postgresql+asyncpg://")
    assert "POT_db" in settings.DATABASE_URL


@pytest.mark.asyncio
async def test_database_connection_success():
    """Test if a connection can be made to the running DB container."""

    engine = create_async_engine(settings.DATABASE_URL)

    try:
        # Connect and execute a simple, non-destructive query
        async with engine.connect() as conn:
            # Execute a basic query to prove the connection works
            result = await conn.execute(text("SELECT 1"))
            assert result.scalar_one() == 1

    except Exception as e:
        pytest.fail(f"Failed to connect to the database: {e}")

    finally:
        await engine.dispose()
