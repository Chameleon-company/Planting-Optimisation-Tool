import asyncio
from sqlalchemy import select
from src.database import AsyncSessionLocal, engine
from src.models.soil_texture import SoilTexture
from src.models.agroforestry_type import AgroforestryType
from src.schemas.constants import SoilTextureID, AgroforestryTypeID


async def seed_references():
    async with AsyncSessionLocal() as session:
        print("--- Seeding Reference Tables from Constants ---")

        # Seed Soil Textures
        for entry in SoilTextureID:
            # Transform to lower case
            readable_name = entry.name.replace("_", " ").lower()

            stmt = select(SoilTexture).where(SoilTexture.id == entry.value)
            result = await session.execute(stmt)
            existing = result.scalar_one_or_none()

            if not existing:
                session.add(SoilTexture(id=entry.value, name=readable_name))
                print(f"Added Soil [{entry.value}]: {readable_name}")
            else:
                # update name if it changed in enum
                existing.name = readable_name

        # Seed Agroforestry Types
        for entry in AgroforestryTypeID:
            # Transform to lower case
            readable_type = entry.name.lower()

            stmt = select(AgroforestryType).where(AgroforestryType.id == entry.value)
            result = await session.execute(stmt)
            existing = result.scalar_one_or_none()

            if not existing:
                session.add(AgroforestryType(id=entry.value, type_name=readable_type))
                print(f"Added Agroforestry [{entry.value}]: {readable_type}")
            else:
                existing.type_name = readable_type

        await session.commit()
        print("Seeding complete and synced with constants.py.")


async def main():
    try:
        await seed_references()
    finally:
        # Dispose the engine while the main loop is still running
        await engine.dispose()


if __name__ == "__main__":
    # asyncio.run handles the loop creation and closing cleanly
    asyncio.run(main())
