from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from src.models.boundaries import FarmBoundary


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
        # shapely_geom = to_shape(boundary_record.boundary)

        # Pass to GIS logic
        # Function not implemented yet
        # estimation_results = sapling_estimation(geometry=shapely_geom, spacing_m=3.0)

        # Return results
        # return {"farm_id": farm_id, "results": estimation_results}
