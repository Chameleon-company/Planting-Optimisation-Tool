from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession


async def get_soil_ph_for_point(
    db: AsyncSession,
    latitude: float,
    longitude: float,
) -> float | None:
    query = text(
        """
        SELECT ph
        FROM soil_ph
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

    return float(row.ph) if row.ph is not None else None
