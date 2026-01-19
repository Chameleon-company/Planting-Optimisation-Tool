import csv
import asyncio
import httpx
from sqlalchemy import select

# Project imports
from src.database import AsyncSessionLocal, engine
from src.models.user import User
from src.dependencies import create_access_token
from src.schemas.constants import SoilTextureID, AgroforestryTypeID

# Configuration
BASE_URL = "http://127.0.0.1:8080"
USER_EMAIL = "testuser123@test.com"


async def get_test_user_token():
    """Generates a valid JWT token for our test user by fetching their ID from DB."""
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(User).where(User.email == USER_EMAIL))
        user = result.scalar_one_or_none()

        if not user:
            raise Exception(
                f"User {USER_EMAIL} not found. Run create_test_user.py first."
            )

        token = create_access_token(data={"sub": str(user.id)})
        return token


async def ingest_species():
    soil_map = {e.name.replace("_", " ").lower(): e.value for e in SoilTextureID}
    agro_map = {e.name.lower(): e.value for e in AgroforestryTypeID}

    async with httpx.AsyncClient(timeout=60.0) as client:
        token = await get_test_user_token()
        headers = {"Authorization": f"Bearer {token}"}
        url = f"{BASE_URL}/species"

        with open(
            "src/scripts/data/species_20251222.csv", mode="r", encoding="utf-8-sig"
        ) as f:
            reader = csv.DictReader(f)
            count = 0

            for row in reader:

                def map_names_to_ids(csv_value, lookup_table):
                    if not csv_value or str(csv_value).lower() == "nan":
                        return []
                    names = [
                        n.strip().lower()
                        for n in str(csv_value).split("|")
                        if n.strip()
                    ]
                    return [lookup_table[n] for n in names if n in lookup_table]

                payload = {
                    "name": row["name"],
                    "common_name": row["common_name"],
                    "rainfall_mm_min": int(row["rainfall_mm_min"]),
                    "rainfall_mm_max": int(row["rainfall_mm_max"]),
                    "temperature_celsius_min": int(row["temperature_celsius_min"]),
                    "temperature_celsius_max": int(row["temperature_celsius_max"]),
                    "elevation_m_min": int(row["elevation_m_min"]),
                    "elevation_m_max": int(row["elevation_m_max"]),
                    "ph_min": float(row["ph_min"]),
                    "ph_max": float(row["ph_max"]),
                    "coastal": row["coastal"].lower() == "true",
                    "riparian": row["riparian"].lower() == "true",
                    "nitrogen_fixing": row["nitrogen_fixing"].lower() == "true",
                    "shade_tolerant": row["shade_tolerant"].lower() == "true",
                    "bank_stabilising": row["bank_stabilising"].lower() == "true",
                    "soil_textures": map_names_to_ids(
                        row.get("preferred_soil_texture"), soil_map
                    ),
                    "agroforestry_types": map_names_to_ids(
                        row.get("agroforestry_type"), agro_map
                    ),
                }

                # Retry logic for intermittent Windows/FastAPI connection drops
                max_retries = 3
                for attempt in range(max_retries):
                    try:
                        response = await client.post(url, json=payload, headers=headers)

                        if response.status_code == 201:
                            count += 1
                            break
                        else:
                            if attempt < max_retries - 1:
                                print(".", end="", flush=True)
                                await asyncio.sleep(1)
                            else:
                                # Only print the full error if it fails 3 times in a row
                                print(
                                    f"\nFailed {row['name']} after {max_retries} attempts: {response.status_code}"
                                )
                            if attempt < max_retries - 1:
                                await asyncio.sleep(1)  # Wait before retry

                    except (httpx.RemoteProtocolError, httpx.ConnectError) as e:
                        print(
                            f"Connection error for {row['name']} (Attempt {attempt + 1}): {e}"
                        )
                        if attempt < max_retries - 1:
                            await asyncio.sleep(1)
                        else:
                            raise

            print(f"Finished! Total species created: {count}")


async def main():
    try:
        await ingest_species()
    finally:
        await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
