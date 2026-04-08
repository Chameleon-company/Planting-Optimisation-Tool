from geoalchemy2.shape import from_shape, to_shape
from sapling_estimation.estimate import sapling_estimation
from sqlalchemy import delete, select, text
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.boundaries import FarmBoundary
from src.models.planting_estimates import PlantingEstimate


class SaplingEstimationService:
    @staticmethod
    async def run_estimation(
        db: AsyncSession,
        farm_id: int,
        spacing_m: float = 3.0,
    ):
        try:
            boundary_result = await db.execute(select(FarmBoundary).where(FarmBoundary.id == farm_id))
            boundary = boundary_result.scalar_one_or_none()

            if boundary is None:
                return {"status": "failed", "message": "Farm not found"}

            farm_polygon = to_shape(boundary.boundary)
            farm_wkt = farm_polygon.wkt

            # DEM Query
            dem_query = text(
                """
                WITH merged AS (
                    SELECT ST_Union(rast) AS rast
                    FROM dem_table
                    WHERE ST_Intersects(
                        rast,
                        ST_Transform(
                            ST_GeomFromText(:farm_wkt, 4326),
                            ST_SRID(rast)
                        )
                    )
                )
                SELECT
                    (ST_DumpValues(rast)).valarray AS valarray,
                    ST_UpperLeftX(rast) AS ulx,
                    ST_UpperLeftY(rast) AS uly,
                    ST_ScaleX(rast) AS scalex,
                    ST_ScaleY(rast) AS scaley,
                    ST_SRID(rast) AS srid
                FROM merged
                WHERE rast IS NOT NULL;
                """
            )

            dem_result = await db.execute(
                dem_query,
                {"farm_wkt": farm_wkt},
            )
            dem_row = dem_result.fetchone()

            if dem_row is None:
                return {"status": "failed", "message": "DEM not found"}

            estimation_result = sapling_estimation(
                farm_polygon=farm_polygon,
                spacing_m=spacing_m,
                farm_boundary_crs="EPSG:4326",
                dem_array=dem_row.valarray,
                dem_upper_left_x=float(dem_row.ulx),
                dem_upper_left_y=float(dem_row.uly),
                pixel_width=abs(float(dem_row.scalex)),
                pixel_height=abs(float(dem_row.scaley)),
                dem_crs=f"EPSG:{dem_row.srid}",
            )

            final_grid = estimation_result["final_grid"]
            slope_values = estimation_result["slope_values"]
            optimal_angle = estimation_result["optimal_angle"]

            # Clear old results
            await db.execute(delete(PlantingEstimate).where(PlantingEstimate.farm_id == farm_id))

            # Insert new
            planting_estimates = []
            for pt, slope_value in zip(final_grid["geometry"], slope_values):
                planting_estimates.append(
                    PlantingEstimate(
                        farm_id=farm_id,
                        slope=float(slope_value) if slope_value is not None else None,
                        geometry=from_shape(pt, srid=4326),
                    )
                )

            db.add_all(planting_estimates)
            await db.commit()

            return {
                "id": farm_id,
                "sapling_count": len(final_grid),
                "optimal_angle": optimal_angle,
            }

        except Exception as e:
            await db.rollback()
            return {"status": "failed", "message": str(e)}
