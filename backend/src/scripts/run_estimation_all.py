import asyncio

from sqlalchemy import select

from src.database import AsyncSessionLocal
from src.models.farm import Farm
from src.services.sapling_estimation import SaplingEstimationService


async def run_all_estimations():
    print("Starting sapling estimation for all farms...")

    total_saplings = 0
    success_count = 0
    failed_count = 0

    async with AsyncSessionLocal() as session:
        result = await session.execute(select(Farm.id))
        farm_ids = [row[0] for row in result.fetchall()]

        print(f"Total farms found: {len(farm_ids)}")

        for farm_id in farm_ids:
            try:
                result = await SaplingEstimationService.run_estimation(
                    session,
                    farm_id=farm_id,
                )

                # accumulate total saplings
                saplings = result.get("sapling_count", 0)
                total_saplings += saplings
                success_count += 1

            except Exception as e:
                print(f"Farm {farm_id} failed → {e}")
                failed_count += 1

    print("\n Estimation Summary")
    print(f"✔ Total farms processed : {len(farm_ids)}")
    print(f"✔ Successful runs       : {success_count}")
    print(f"✔ Failed runs           : {failed_count}")
    print(f"✔ Total saplings        : {total_saplings}")

    print("\nAll estimations completed.")


if __name__ == "__main__":
    asyncio.run(run_all_estimations())
