from geoalchemy2.shape import from_shape, to_shape
from sapling_estimation.estimate import sapling_estimation
from shapely.geometry import mapping
from sqlalchemy import delete, select, text
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.boundaries import FarmBoundary
from src.models.farm import Farm
from src.models.planting_estimates import PlantingEstimate


class SaplingEstimationService:
    async def run_estimation(
        self,
        db: AsyncSession,
        farm_ids: list[int],
        spacing_x: float,
        spacing_y: float,
        max_slope: float,
        persist: bool = True,
    ) -> dict:
        """Runs the sapling estimation for one or many farms.

        persist controls whether the computed planting grid replaces the farm's
        saved PlantingEstimate records. Defaults to True for the Sapling
        Calculator's normal use. Callers that only need the numbers (e.g. a
        read-only report) should pass persist=False so viewing a report can
        never overwrite a farm's existing planting grid.
        """

        if not farm_ids:
            return {"status": "success", "farm_count": 0, "results": []}

        results = []

        for farm_id in farm_ids:
            data = await self._estimate_single_farm(
                db=db,
                farm_id=farm_id,
                spacing_x=spacing_x,
                spacing_y=spacing_y,
                max_slope=max_slope,
                persist=persist,
            )

            results.append(
                {
                    "status": data.get("status", "success"),
                    "farm_id": farm_id,
                    "message": data.get("message"),
                    "pre_slope_count": data.get("pre_slope_count"),
                    "aligned_count": data.get("aligned_count"),
                    "baseline_tree_count": data.get("baseline_tree_count"),  # add
                    "additional_sapling_count": data.get("additional_sapling_count"),  # add
                    "optimal_angle": data.get("optimal_angle"),
                    "rotation_average": data.get("rotation_average"),
                    "rotation_std_dev": data.get("rotation_std_dev"),
                }
            )

        return {
            "status": "success",
            "farm_count": len(farm_ids),
            "results": results,
        }

    @staticmethod
    async def _estimate_single_farm(
        db: AsyncSession,
        farm_id: int,
        spacing_x: float,
        spacing_y: float,
        max_slope: float,
        persist: bool = True,
    ) -> dict:
        try:
            farm_result = await db.execute(select(Farm).where(Farm.id == farm_id))
            farm = farm_result.scalar_one_or_none()

            if farm is None:
                return {"status": "failed", "message": "Farm not found"}
            boundary_result = await db.execute(select(FarmBoundary).where(FarmBoundary.id == farm_id))
            boundary = boundary_result.scalar_one_or_none()

            if boundary is None:
                return {"status": "failed", "message": "Farm boundary not found"}

            baseline_tree_count = farm.baseline_tree_count
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
                spacing_x=spacing_x,
                spacing_y=spacing_y,
                max_slope=max_slope,
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
            aligned_count = len(final_grid)
            additional_sapling_count = max(aligned_count - baseline_tree_count, 0)

            if persist:
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
                "pre_slope_count": estimation_result.get("pre_slope_count"),
                "aligned_count": aligned_count,
                "baseline_tree_count": baseline_tree_count,
                "additional_sapling_count": additional_sapling_count,
                "optimal_angle": optimal_angle,
                "rotation_average": estimation_result.get("rotation_average"),
                "rotation_std_dev": estimation_result.get("rotation_std_dev"),
            }

        except Exception as e:
            await db.rollback()
            return {"status": "failed", "message": str(e)}


async def get_planting_grid(db: AsyncSession, farm_id: int) -> dict:
    result = await db.execute(select(PlantingEstimate).where(PlantingEstimate.farm_id == farm_id))
    estimates = list(result.scalars().all())
    features = [
        {
            "type": "Feature",
            "geometry": mapping(to_shape(est.geometry)),
            "properties": {"slope": est.slope},
        }
        for est in estimates
    ]
    return {"type": "FeatureCollection", "features": features}
