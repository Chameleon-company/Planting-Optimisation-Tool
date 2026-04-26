import asyncio
import csv

from sqlalchemy import select

from src.database import AsyncSessionLocal, engine
from src.models.exclusion_rules import SpeciesDependency
from src.models.species import Species


async def import_species_dependencies():
    """
    Imports species dependencies from a CSV file.
    Expects columns: focal_species_id, required_partner_id
    """
    async with AsyncSessionLocal() as session:
        # Path to csv
        csv_path = "src/scripts/data/species_dependencies_20260402.csv"

        # First, create a mapping of Species ID to verify existence
        species_res = await session.execute(select(Species.id))
        existing_ids = set(species_res.scalars().all())

        imported_count = 0
        skipped_count = 0

        try:
            with open(csv_path, mode="r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    try:
                        focal_id = int(row["focal_species_id"])
                        partner_id = int(row["required_partner_id"])

                        # Check if BOTH IDs exist in the database
                        if focal_id in existing_ids and partner_id in existing_ids:
                            new_dep = SpeciesDependency(focal_species_id=focal_id, required_partner_id=partner_id)
                            session.add(new_dep)
                            imported_count += 1
                        else:
                            # Identify which one is missing for easier debugging
                            missing = []
                            if focal_id not in existing_ids:
                                missing.append(f"focal:{focal_id}")
                            if partner_id not in existing_ids:
                                missing.append(f"partner:{partner_id}")
                            print(f"Skipping row: Species IDs {', '.join(missing)} not found in database.")
                            skipped_count += 1
                    except (ValueError, KeyError) as e:
                        print(f"Skipping malformed row: {row} - Error: {e}")
                        skipped_count += 1

            if imported_count > 0:
                await session.commit()
                print(f"Successfully imported {imported_count} dependencies.")
            print(f"Total skipped: {skipped_count}")

        except FileNotFoundError:
            print(f"Error: Could not find {csv_path}")


async def main():
    try:
        await import_species_dependencies()
    finally:
        await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
