from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.waterways import Waterway

RIPARIAN_BUFFER_M: float = 15.0


async def get_riparian_flags(
    db: AsyncSession,
    latitude: float,
    longitude: float,
) -> dict:
    """
    Check if a farm location falls within a riparian zone.

    Queries the waterways table using PostGIS ST_Distance to find the
    distance from the farm point to the nearest waterway line.
    Both geometries are transformed to UTM Zone 52S (EPSG:32752) for
    metre-accurate distance calculations.

    Args:
        db:        Async database session.
        latitude:  Farm latitude (WGS84).
        longitude: Farm longitude (WGS84).

    Returns:
        {
            "riparian": bool,
            "distance_to_nearest_waterway_m": float | None,
        }
    """

    farm_point = func.ST_Transform(
        func.ST_SetSRID(
            func.ST_Makepoint(longitude, latitude),
            4326,
        ),
        32752,
    )

    stmt = (
        select(
            func.ST_Distance(
                farm_point,
                func.ST_Transform(Waterway.geometry, 32752),
            ).label("distance_m")
        )
        .where(
            func.ST_DWithin(
                func.ST_Transform(Waterway.geometry, 32752),
                farm_point,
                RIPARIAN_BUFFER_M,
            )
        )
        .order_by("distance_m")
        .limit(1)
    )

    result = await db.execute(stmt)
    row = result.first()

    if row is None or row.distance_m is None:
        return {
            "riparian": False,
            "distance_to_nearest_waterway_m": None,
        }

    distance_m = float(row.distance_m)

    return {
        "riparian": distance_m < RIPARIAN_BUFFER_M,
        "distance_to_nearest_waterway_m": round(distance_m, 1),
    }
