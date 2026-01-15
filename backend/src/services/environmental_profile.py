from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from src.models.boundaries import FarmBoundary
from core.farm_profile import build_farm_profile
from geoalchemy2.shape import to_shape
from shapely.geometry import MultiPolygon, Polygon


class EnvironmentalProfileService:
    @staticmethod
    async def run_environmental_profile(db: AsyncSession, farm_id: int):
        # Fetch the boundary data
        result = await db.execute(
            select(FarmBoundary).where(FarmBoundary.id == farm_id)
        )
        boundary_record = result.scalar_one_or_none()

        if not boundary_record:
            return None

        # Geometry parsing
        shapely_geom = to_shape(boundary_record.boundary)

        target_poly = None

        if isinstance(shapely_geom, MultiPolygon):
            target_poly = list(shapely_geom.geoms)[0]
        elif isinstance(shapely_geom, Polygon):
            target_poly = shapely_geom
        else:
            return None

        # Format for GIS parser
        lat_lon_ring = [(lat, lon) for (lon, lat) in list(target_poly.exterior.coords)]
        formatted_geometry = [lat_lon_ring]

        # Call the external GEE logic
        # Passing the boundary and farm_id
        profile = build_farm_profile(geometry=formatted_geometry, farm_id=farm_id)

        return profile
