import asyncio
import csv

from sqlalchemy import select

from src.database import AsyncSessionLocal, engine
from src.models.boundaries import FarmBoundary
from src.models.farm import Farm


async def import_boundaries():
    async with AsyncSessionLocal() as session:
        csv_path = "src/scripts/data/farm_boundaries_master.csv"

        try:
            # Load all external_id -> farm_id mappings in one query
            result = await session.execute(select(Farm.id, Farm.external_id))
            id_map = {ext_id: farm_id for farm_id, ext_id in result.all()}

            with open(csv_path, mode="r", encoding="utf-8-sig") as f:
                rows = list(csv.DictReader(f))

            boundaries = []
            skipped = 0
            for row in rows:
                ext_id = int(row["external_id"])
                farm_id = id_map.get(ext_id)
                if farm_id:
                    boundaries.append(
                        FarmBoundary(
                            id=farm_id,
                            boundary=f"SRID=4326;{row['boundary'].strip()}",
                            external_id=ext_id,
                        )
                    )
                else:
                    print(f"Skip: No farm found for external_id {ext_id}")
                    skipped += 1

            session.add_all(boundaries)
            await session.commit()
            print(f"Successfully imported {len(boundaries)} boundaries, skipped {skipped}.")

        except FileNotFoundError:
            print(f"Error: Could not find {csv_path}")


async def main():
    try:
        await import_boundaries()
    finally:
        await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
