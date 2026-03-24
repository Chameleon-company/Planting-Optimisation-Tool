import numpy as np
import rasterio
from geoalchemy2.shape import from_shape, to_shape
from rasterio.transform import from_origin
from sapling_estimation.estimate import sapling_estimation
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.boundaries import FarmBoundary
from src.models.planting_estimates import PlantingEstimate


class SaplingEstimationService:
    @staticmethod
    async def run_estimation(db: AsyncSession, farm_id: int, spacing_m: float = 3.0):
        # Get farm boundary
        result = await db.execute(select(FarmBoundary).where(FarmBoundary.id == farm_id))
        boundary = result.scalar_one_or_none()

        if not boundary:
            return {"status": "failed", "message": "Farm not found"}

        farm_polygon = to_shape(boundary.boundary)

        # Get DEM values + transform from PostGIS
        dem_query = text("""
            SELECT
                (ST_DumpValues(rast)).valarray AS valarray,
                ST_UpperLeftX(rast) AS ulx,
                ST_UpperLeftY(rast) AS uly,
                ST_ScaleX(rast) AS scalex,
                ST_ScaleY(rast) AS scaley
            FROM dem_table
            LIMIT 1
        """)

        dem_result = await db.execute(dem_query)
        dem_row = dem_result.first()

        if not dem_row:
            return {"status": "failed", "message": "DEM not found"}

        dem_array = np.array(dem_row.valarray, dtype=float)

        # Real raster transform
        dem_transform = from_origin(
            dem_row.ulx,
            dem_row.uly,
            abs(dem_row.scalex),
            abs(dem_row.scaley),
        )

        # Run estimation
        result = sapling_estimation(
            farm_polygon=farm_polygon,
            spacing_m=spacing_m,
            farm_boundary_crs="EPSG:4326",
            debug=True,
            dem_array=dem_array,
            dem_transform=dem_transform,
        )

        final_grid = result["final_grid"]
        slope_array = result["slope_array"]

        # Save to planting_estimates
        if "geometry" not in final_grid.columns:
            return {"status": "failed", "message": "No geometry column in final grid"}

        for pt in final_grid["geometry"]:
            # Convert point → raster index
            row, col = rasterio.transform.rowcol(dem_transform, pt.x, pt.y)

            # Check bounds
            if 0 <= row < slope_array.shape[0] and 0 <= col < slope_array.shape[1]:
                slope_value = float(slope_array[row][col])
            else:
                slope_value = None

            db.add(
                PlantingEstimate(
                    farm_id=farm_id,
                    x_coord=pt.x,
                    y_coord=pt.y,
                    slope=slope_value,
                    geometry=from_shape(pt, srid=4326),
                )
            )

        await db.commit()

        return {
            "id": farm_id,
            "sapling_count": len(final_grid),
            "optimal_angle": result["optimal_angle"],
        }
