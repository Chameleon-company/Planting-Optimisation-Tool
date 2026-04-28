from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession


async def get_soil_texture_for_point(
    db: AsyncSession,
    latitude: float,
    longitude: float,
) -> str | None:
    query = text(
        """
        SELECT texture
        FROM soil_texture_spatial
        WHERE ST_Intersects(
            geometry,
            ST_SetSRID(ST_Point(:longitude, :latitude), 4326)
        )
        LIMIT 1;
        """
    )

    result = await db.execute(
        query,
        {
            "latitude": latitude,
            "longitude": longitude,
        },
    )

    row = result.fetchone()

    if row is None:
        return None

    return str(row.texture) if row.texture is not None else None
