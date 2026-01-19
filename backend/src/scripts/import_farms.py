import sys
import csv
import asyncio
import httpx
from sqlalchemy import select

# Project imports
from src.database import AsyncSessionLocal, engine
from src.models.user import User
from src.dependencies import create_access_token

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


async def ingest_farms():
    async with httpx.AsyncClient(timeout=60.0) as client:
        token = await get_test_user_token()
        headers = {"Authorization": f"Bearer {token}"}

        with open(
            "src/scripts/data/farms_20251219.csv", mode="r", encoding="utf-8-sig"
        ) as f:
            reader = csv.DictReader(f)
            count = 0

            for row in reader:
                # Mapping to what schemas/farm.py FarmCreate expects.
                payload = {
                    "rainfall_mm": int(float(row["rainfall_mm"])),
                    "temperature_celsius": int(float(row["temperature_celsius"])),
                    "elevation_m": int(float(row["elevation_m"])),
                    "ph": str(
                        round(float(row["ph"]), 1)
                    ),  # Decimal needs string or float
                    "soil_texture_id": int(row["soil_texture_id"]),
                    "area_ha": str(round(float(row["area_ha"]), 3)),
                    "latitude": str(round(float(row["latitude"]), 5)),
                    "longitude": str(round(float(row["longitude"]), 5)),
                    "coastal": row["coastal"].lower() == "true",
                    "riparian": row["riparian"].lower() == "true",
                    "nitrogen_fixing": row["nitrogen_fixing"].lower() == "true",
                    "shade_tolerant": row["shade_tolerant"].lower() == "true",
                    "bank_stabilising": row["bank_stabilising"].lower() == "true",
                    "slope": str(round(float(row["slope"]), 2)),
                    "external_id": int(row["external_id"]),
                }

                response = await client.post(
                    f"{BASE_URL}/farms", json=payload, headers=headers
                )

                if response.status_code == 201:
                    count += 1
                else:
                    # Check if the response is actually JSON before parsing
                    try:
                        error_msg = response.json().get("detail")
                    except Exception:
                        # Fallback to the raw status and text if JSON parsing fails
                        error_msg = (
                            f"Status {response.status_code}: {response.text[:100]}"
                        )

                    print(f"ID {row['external_id']} Failed: {error_msg}")

            print(f"Finished! Total farms created: {count}")

            if count == 0:
                print("Error: No farms were ingested.")
                sys.exit(1)


async def main():
    try:
        await ingest_farms()
    finally:
        await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
