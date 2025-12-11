import pytest
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy import delete, select, text, insert  # noqa: F401
from src.config import Settings
from src.database import Base  # Import your Base  # noqa: F401

# Import the model classes needed for the test:
from src.models.farm import Farm
from src.models.soil_texture import SoilTexture

settings = Settings()
engine = create_async_engine(settings.DATABASE_URL)


@pytest.mark.asyncio
async def test_foreign_key_cascade_delete():
    """
    Verifies that deleting a SoilTexture record automatically cascades
    and deletes dependent Farm records.
    """

    async with AsyncSession(engine) as session:
        # --- 1. SETUP: Insert Parent and Child Records ---

        # 1a. Insert Parent (SoilTexture)
        soil_texture = SoilTexture(texture_name="Loam")
        session.add(soil_texture)
        await session.flush()
        soil_id = soil_texture.id

        # 1b. Insert Child (Farm) referencing the Parent
        farm = Farm(
            rainfall_mm=1000053400,
            temperature_celsius=222135.08686,
            elevation_m=51123120,
            ph=63.65,
            soil_texture_id=soil_id,
            area_ha=10.02,
            latitude=5234523.42342,
            longitude=3452.3,
            coastal=False,
            riparian=True,
            nitrogen_fixing=True,
            shade_tolerant=False,
            bank_stabilising=True,
            slope=32.556,
        )
        session.add(farm)
        await session.flush()

        # --- 2. ACTION: Delete the Parent Record ---

        # Delete the SoilTexture row
        await session.execute(delete(SoilTexture).where(SoilTexture.id == soil_id))

        # --- 3. VERIFICATION: Check Child Record ---

        # Query the Farm table to see if the dependent record still exists
        farm_check = await session.execute(
            select(Farm).where(Farm.soil_texture_id == soil_id)
        )

        # If CASCADE is working, the result list must be empty.
        assert farm_check.scalars().first() is None, (
            "CASCADE delete failed: Farm record still exists after parent SoilTexture was deleted."
        )

        # Manually roll back the session to clean the database state after the test
        await session.rollback()
