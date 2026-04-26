import asyncio
import csv
import os
import sys

import httpx
from sqlalchemy import select

# Project imports
from src.database import AsyncSessionLocal, engine
from src.dependencies import create_access_token
from src.models.user import User

# Configuration
BASE_URL = f"http://127.0.0.1:{os.getenv('API_PORT', '8080')}"
USER_EMAIL = "testuser123@test.com"


async def get_test_user_token():
    """Generates a valid JWT token for our test user by fetching their ID from DB."""
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(User).where(User.email == USER_EMAIL))
        user = result.scalar_one_or_none()

        if not user:
            raise Exception(f"User {USER_EMAIL} not found. Run create_test_user.py first.")

        token = create_access_token(data={"sub": str(user.id)})
        return token


async def ingest_farms():
    async with httpx.AsyncClient(timeout=60.0) as client:
        token = await get_test_user_token()
        headers = {"Authorization": f"Bearer {token}"}
        semaphore = asyncio.Semaphore(50)

        with open("src/scripts/data/farm_master.csv", mode="r", encoding="utf-8-sig") as f:
            rows = list(csv.DictReader(f))

        count = 0
        failures = 0

        async def post_farm(row):
            nonlocal count, failures
            payload = {
                "rainfall_mm": int(float(row["rainfall_mm"])),
                "temperature_celsius": int(float(row["temperature_celsius"])),
                "elevation_m": int(float(row["elevation_m"])),
                "ph": str(round(float(row["ph"]), 1)),
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
            async with semaphore:
                response = await client.post(f"{BASE_URL}/farms", json=payload, headers=headers)

            if response.status_code == 201:
                count += 1
            else:
                failures += 1
                try:
                    body = response.json()
                    errors = body.get("errors")
                    if errors:
                        error_msg = "; ".join(f"{e['field']}: {e['message']}" for e in errors)
                    else:
                        error_msg = body.get("detail", f"Status {response.status_code}")
                except Exception:
                    error_msg = f"Status {response.status_code}: {response.text[:100]}"
                print(f"ID {row['external_id']} Failed: {error_msg}")

        await asyncio.gather(*[post_farm(row) for row in rows])
        print(f"Finished! Total farms created: {count}, failures: {failures}")

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
