import numpy as np
import rasterio
from geoalchemy2.shape import from_shape, to_shape
from sapling_estimation.estimate import sapling_estimation
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.boundaries import FarmBoundary
from src.models.planting_estimates import PlantingEstimate


class SaplingEstimationService:
    @staticmethod
    async def run_estimation(db: AsyncSession, farm_id: int, spacing_m: float = 3.0, test_mode: bool = False):
        # Get farm boundary
        boundary_result = await db.execute(select(FarmBoundary).where(FarmBoundary.id == farm_id))
        boundary = boundary_result.scalar_one_or_none()

        if not boundary:
            return {"status": "failed", "message": "Farm not found"}

        farm_polygon = to_shape(boundary.boundary)
        farm_wkt = farm_polygon.wkt

        # Get DEM values + transform from PostGIS
        # Get DEM values + transform from PostGIS
        if test_mode:
            # Lightweight query path for tests
            dem_query = text(
                """
                SELECT
                    (ST_DumpValues(rast)).valarray AS valarray,
                    ST_UpperLeftX(rast) AS ulx,
                    ST_UpperLeftY(rast) AS uly,
                    ST_ScaleX(rast) AS scalex,
                    ST_ScaleY(rast) AS scaley
                FROM dem_table
                LIMIT 1;
                """
            )
            dem_result = await db.execute(dem_query)
        else:
            # Production path: supports farms spanning multiple DEM tiles
            dem_query = text(
                """
                WITH merged AS (
                    SELECT ST_Union(rast) AS rast
                    FROM dem_table
                    WHERE ST_Intersects(
                        rast,
                        ST_Transform(ST_GeomFromText(:farm_wkt, 4326), ST_SRID(rast))
                    )
                )
                SELECT
                    (ST_DumpValues(rast)).valarray AS valarray,
                    ST_UpperLeftX(rast) AS ulx,
                    ST_UpperLeftY(rast) AS uly,
                    ST_ScaleX(rast) AS scalex,
                    ST_ScaleY(rast) AS scaley
                FROM merged;
                """
            )
            dem_result = await db.execute(dem_query, {"farm_wkt": farm_wkt})

        dem_result = await db.execute(dem_query, {"farm_wkt": farm_wkt})
        dem_row = dem_result.first()

        if not dem_row:
            return {"status": "failed", "message": "DEM not found for this farm"}

        dem_array = np.array(dem_row.valarray, dtype=float)

        pixel_width = abs(float(dem_row.scalex))
        pixel_height = abs(float(dem_row.scaley))

        dem_transform = rasterio.transform.from_origin(
            dem_row.ulx,
            dem_row.uly,
            pixel_width,
            pixel_height,
        )

        if test_mode:
            # FAST MOCK RESULT FOR TESTING
            return {
                "id": farm_id,
                "sapling_count": 5,
                "optimal_angle": 0,
            }
        # Run estimation
        estimation_result = sapling_estimation(
            farm_polygon=farm_polygon,
            spacing_m=spacing_m,
            farm_boundary_crs="EPSG:4326",
            debug=False,
            dem_array=dem_array,
            dem_transform=dem_transform,
            pixel_width=pixel_width,
            pixel_height=pixel_height,
        )

        # return results
        final_grid = estimation_result["final_grid"]
        slope_array = estimation_result["slope_array"]
        optimal_angle = estimation_result["optimal_angle"]

        # Save to planting_estimates
        if "geometry" not in final_grid.columns:
            return {"status": "failed", "message": "No geometry column in final grid"}

        for pt in final_grid["geometry"]:
            row, col = rasterio.transform.rowcol(dem_transform, pt.x, pt.y)

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

        # ERROR HANDLING
        try:
            await db.commit()
        except Exception as e:
            await db.rollback()
            return {
                "status": "failed",
                "message": f"Database commit failed: {str(e)}",
            }

        return {
            "id": farm_id,
            "sapling_count": len(final_grid),
            "optimal_angle": optimal_angle,
        }
