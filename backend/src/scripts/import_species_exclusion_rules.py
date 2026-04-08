import asyncio
import csv
import json

from sqlalchemy import select

from src.database import AsyncSessionLocal, engine
from src.models.exclusion_rules import SpeciesExclusionRule
from src.models.species import Species


def to_int_or_none(value):
    return int(value) if value and str(value).strip() != "" else None


async def import_species_exclusion_rules():
    """
    Imports species exclusion rules from a CSV file.
    Expects columns: species_id, feature, operator, value, reason
    """
    async with AsyncSessionLocal() as session:
        # Path to csv
        csv_path = "src/scripts/data/species_exclusion_rules_20260402.csv"

        # First, create a mapping of Species ID to verify existence
        species_res = await session.execute(select(Species.id))
        existing_ids = set(species_res.scalars().all())

        try:
            with open(csv_path, mode="r", encoding="utf-8") as f:
                reader = csv.DictReader(f)

                rules_to_add = []
                for row in reader:
                    sp_id = to_int_or_none(row["species_id"])

                    # Skip if the species doesn't exist in the database
                    if sp_id not in existing_ids:
                        print(f"Skipping rule for unknown species_id: {sp_id}")
                        continue

                    feature_string = row["feature"].strip()
                    operator_string = row["operator"].strip()
                    reason_string = row["reason"].strip()

                    # Parse the value: Convert strings that look like lists into actual lists
                    # This handles the "['clay']" format from the CSV
                    raw_value = row["value"]
                    try:
                        # Attempt to parse as JSON if it looks like a list or number
                        parsed_value = json.loads(raw_value.replace("'", '"'))
                    except (json.JSONDecodeError, ValueError):
                        # Fallback to raw string if it's not a JSON structure
                        parsed_value = raw_value

                    new_rule = SpeciesExclusionRule(species_id=sp_id, feature=feature_string, operator=operator_string, value=parsed_value, reason=reason_string)
                    rules_to_add.append(new_rule)

                if rules_to_add:
                    session.add_all(rules_to_add)
                    await session.commit()
                    print(f"Successfully imported {len(rules_to_add)} exclusion rules.")

        except FileNotFoundError:
            print(f"Error: Could not find {csv_path}")


async def main():
    try:
        await import_species_exclusion_rules()
    finally:
        await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
