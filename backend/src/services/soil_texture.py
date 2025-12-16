from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from src.models import SoilTexture  # Import the ORM model


async def get_all_textures(db: AsyncSession):
    """
    Retrieves all SoilTexture records from the database.
    """
    statement = select(SoilTexture)

    # Execute the statement and get the results
    result = await db.execute(statement)

    return result.scalars().all()
