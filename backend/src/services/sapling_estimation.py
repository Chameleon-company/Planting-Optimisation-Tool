from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from src.models.boundaries import FarmBoundary
from geoalchemy2.shape import to_shape
from sapling_estimation.estimate import sapling_estimation


class SaplingEstimationService:
    @staticmethod
    async def run_estimation(db: AsyncSession, farm_id: int):
        # Fetch boundary from DB
        result = await db.execute(
            select(FarmBoundary).where(FarmBoundary.id == farm_id)
        )
        boundary_record = result.scalar_one_or_none()
        if not boundary_record:
            return None

        # Convert database geometry to a Shapely object
        shapely_geom = to_shape(boundary_record.boundary)

        # Pass to GIS logic
        # Function not implemented yet
        estimation_results = sapling_estimation(
            farm_polygon=shapely_geom,
            spacing_m=3.0,
            farm_boundary_crs="EPSG:4326",
            debug=False,
        )

        # Return results
        return {
            "id": farm_id,
            "sapling_count": estimation_results["sapling_count"],
            "optimal_angle": estimation_results["optimal_angle"],
        }
