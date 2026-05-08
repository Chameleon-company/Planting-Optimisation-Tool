import json

from sqlalchemy.ext.asyncio import AsyncSession

from src import cache
from src.services import farm as farm_service
from src.services.sapling_estimation import SaplingEstimationService


class SaplingBatchEstimationService:
    async def run_batch_estimation(
        self,
        db: AsyncSession,
        user_id: int,
        spacing_x: float,
        spacing_y: float,
        max_slope: float,
    ):
        farms = await farm_service.list_farms_by_user(db, user_id)  # Get all the user's farms

        if not farms:
            return {"status": "success", "farm_count": 0, "results": []}

        results = []

        # Loop through each farm and access cache for each farm, if cache is not found, run estimation for that farm
        for farm in farms:
            cache_key = f"sapling:{farm.id}:{spacing_x}:{spacing_y}:{max_slope}"
            cached = await cache.get(cache_key)

            if cached:
                data = json.loads(cached)
            else:
                data = await SaplingEstimationService().run_estimation(
                    db=db,
                    farm_id=farm.id,
                    spacing_x=spacing_x,
                    spacing_y=spacing_y,
                    max_slope=max_slope,
                )

            if data and data.get("status", "success") != "failed":
                await cache.set(cache_key, json.dumps(data))

            results.append(
                {
                    "status": data.get("status", "success"),
                    "farm_id": farm.id,
                    "pre_slope_count": data.get("pre_slope_count"),
                    "aligned_count": data.get("aligned_count"),
                    "optimal_angle": data.get("optimal_angle"),
                    "rotation_average": data.get("rotation_average"),
                    "rotation_std_dev": data.get("rotation_std_dev"),
                }
            )

        return {
            "status": "success",
            "farm_count": len(farms),
            "results": results,
        }
