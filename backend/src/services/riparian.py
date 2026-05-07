from geoalchemy2.shape import from_shape
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.waterways import Waterway
from src.schemas.constants import CRS_ANALYSIS, RIPARIAN_BUFFER_M


async def get_riparian_flags(
    db: AsyncSession,
    shapely_farm_geom: object,
) -> dict:
    """
    Check if a farm boundary intersects a riparian zone.

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
        func.bool_or(
            func.ST_Intersects(
                farm_geom_utm,
                func.ST_Buffer(
                    waterway_geom_utm,
                    RIPARIAN_BUFFER_M,
                ),
            )
        ).label("riparian"),
        func.min(
            func.ST_Distance(
                func.ST_Boundary(farm_geom_utm),
                waterway_geom_utm,
            )
        ).label("distance_to_waterway_m"),
    ).select_from(Waterway)

    row = (await db.execute(stmt)).first()

    return {
        "riparian": bool(row.riparian),
        "distance_to_nearest_waterway_m": None if row.distance_to_waterway_m is None else round(float(row.distance_to_waterway_m), 1),
    }
