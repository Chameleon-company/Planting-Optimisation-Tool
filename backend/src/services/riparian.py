from unittest import result

from geoalchemy2.shape import from_shape
from sqlalchemy import func, select, text
from sqlalchemy.ext.asyncio import AsyncSession

from geoalchemy2 import Geography
from geoalchemy2.shape import from_shape
from sqlalchemy import func, select, cast
from src.models.waterways import Waterway


CRS_ANALYSIS = 32751  # UTM 51S
RIPARIAN_BUFFER_M: float = 15.0


async def get_riparian_flags(
    db: AsyncSession,
    shapely_farm_geom: object,
) -> dict:
    """
    Check if a farm location falls within a riparian zone.

    This function uses PostGIS spatial queries to determine if the farm geometry
    intersects with a buffered area around waterways.

    Both geometries are transformed to UTM Zone 51S (EPSG:32751) for
    metre-accurate distance calculations.

    Args:
        db:        Async database session.
        shapely_farm_geom: Farm geometry as a Shapely object.

    Returns:
        {
            "riparian": bool,
        }
    """

    farm_geom_utm = func.ST_Transform(
        from_shape(shapely_farm_geom, srid=4326),
        CRS_ANALYSIS,
    )

    waterway_geom_utm = func.ST_Transform(
        Waterway.geometry,
        CRS_ANALYSIS,
    )

    stmt = select(
        func.exists(
            select(1)
            .select_from(Waterway)
            .where(
                func.ST_Intersects(
                    farm_geom_utm,
                    func.ST_Buffer(
                        waterway_geom_utm,
                        RIPARIAN_BUFFER_M,
                    ),
                )
            )
            .scalar_subquery()
        )
    )

    riparian = bool(await db.scalar(stmt))

    stmt = select(
        func.min(
            func.ST_Distance(
                func.ST_Boundary(farm_geom_utm),
                waterway_geom_utm,
            )
        )
    ).select_from(Waterway)

    distance_m = await db.scalar(stmt)

    print(f"Riparian: {riparian}")
    print(f"Distance to waterway (m): {distance_m}")
    return {
        "riparian": bool(riparian),
        "distance_to_waterway_m": None if distance_m is None else round(float(distance_m), 1),
    }
