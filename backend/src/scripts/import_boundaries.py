import csv
import asyncio
from sqlalchemy import select
from src.database import AsyncSessionLocal, engine
from src.models.farm import Farm
from src.models.boundaries import FarmBoundary


async def import_boundaries():
    async with AsyncSessionLocal() as session:
        # Path to csv
        csv_path = "src/scripts/data/boundaries_20251219.csv"

        try:
            with open(csv_path, mode="r", encoding="utf-8-sig") as f:
                reader = csv.DictReader(f)
                count = 0

                for row in reader:
                    ext_id = int(row["external_id"])
                    wkt_string = row["boundary"].strip()

                    # Find the Farm ID using the external_id
                    stmt = select(Farm.id).where(Farm.external_id == ext_id)
                    result = await session.execute(stmt)
                    farm_id = result.scalar_one_or_none()

                    if farm_id:
                        # Format for GeoAlchemy2 / PostGIS
                        # Using EWKT format: SRID=4326;POLYGON(...)
                        new_boundary = FarmBoundary(
                            id=farm_id,  # Shared PK with Farm
                            boundary=f"SRID=4326;{wkt_string}",
                            external_id=ext_id,
                        )
                        session.add(new_boundary)
                        count += 1
                    else:
                        print(f"Skip: No farm found for external_id {ext_id}")

                await session.commit()
                print(f"Successfully imported {count} boundaries.")

        except FileNotFoundError:
            print(f"Error: Could not find {csv_path}")


async def main():
    try:
        await import_boundaries()
    finally:
        await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
