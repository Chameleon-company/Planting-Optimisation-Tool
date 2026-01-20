import csv
import asyncio

from src.database import AsyncSessionLocal, engine

from src.models.species import Species
from src.models.parameters import Parameter


def to_float_or_none(value):
    return float(value) if value and str(value).strip() != "" else None


def to_int_or_none(value):
    return int(value) if value and str(value).strip() != "" else None


async def import_species_parameters():
    async with AsyncSessionLocal() as session:
        # Path to csv
        csv_path = "src/scripts/data/species_params20260112.csv"

        try:
            with open(csv_path, mode="r", encoding="utf-8-sig") as f:
                reader = csv.DictReader(f)
                count = 0

                for row in reader:
                    sp_id = to_int_or_none(row["species_id"])
                    feature_string = row["feature"].strip()
                    sm_string = row["score_method"].strip()
                    wt = to_float_or_none(row["weight"])
                    trp_lt = to_float_or_none(row["trap_left_tol"])
                    trp_rt = to_float_or_none(row["trap_right_tol"])

                    # Check if the species exists
                    # If sp_id is none set to large value so the get doesn't error, but will
                    # return False since the specie won't exist
                    species = await session.get(Species, sp_id if sp_id else 9999999)

                    if species:
                        new_species_parameter = Parameter(
                            species_id=sp_id,
                            feature=feature_string,
                            score_method=sm_string,
                            weight=wt,
                            trap_left_tol=trp_lt,
                            trap_right_tol=trp_rt,
                        )
                        session.add(new_species_parameter)
                        count += 1
                    else:
                        print(f"Skip: No species found for species_id {sp_id}")

                await session.commit()
                print(f"Successfully imported {count} species parameters.")

        except FileNotFoundError:
            print(f"Error: Could not find {csv_path}")


async def main():
    try:
        await import_species_parameters()
    finally:
        await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
