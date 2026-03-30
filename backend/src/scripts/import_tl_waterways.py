"""
Ingest Timor-Leste waterways dataset into the database.

"""

import asyncio
import sys
from pathlib import Path

import geopandas as gpd
from sqlalchemy import text

from src.database import AsyncSessionLocal, engine

# Path to the waterways GeoPackage file
WATERWAYS_PATH = Path("src/scripts/data/hotosm_tls_waterways_lines_gpkg.gpkg")


async def ingest_waterways():
    """Read the waterways GeoPackage and insert all features into the DB."""

    # --- Load the GeoPackage ---
    if not WATERWAYS_PATH.exists():
        print(f"ERROR: Waterways file not found at '{WATERWAYS_PATH}'")
        print("Download from MS Teams → Planting Optimisation Tool → Datasets → GIS → Timor Leste Waterways")
        sys.exit(1)

    print(f"Loading waterways from '{WATERWAYS_PATH}'...")
    gdf = gpd.read_file(WATERWAYS_PATH, layer=0)
    gdf = gdf.to_crs(epsg=4326)  # ensure WGS84
    print(f"Loaded {len(gdf)} waterway features")

    # --- Insert into DB ---
    async with AsyncSessionLocal() as session:
        # Check if already ingested
        result = await session.execute(text("SELECT COUNT(*) FROM waterways"))
        existing = result.scalar()

        if existing > 0:
            print(f"Waterways table already has {existing} rows — skipping ingestion.")
            print("To re-ingest, truncate the table first: TRUNCATE TABLE waterways;")
            return

        print("Inserting waterways into database...")
        count = 0
        failed = 0

        for _, row in gdf.iterrows():
            if row.geometry is None:
                failed += 1
                continue

            # Convert geometry to EWKT format for PostGIS
            wkt = row.geometry.wkt
            ewkt = f"SRID=4326;{wkt}"

            await session.execute(
                text("""
                    INSERT INTO waterways (name, waterway, geometry)
                    VALUES (:name, :waterway, ST_GeomFromEWKT(:geometry))
                """),
                {
                    "name": row.get("name") or None,
                    "waterway": row.get("waterway") or None,
                    "geometry": ewkt,
                },
            )
            count += 1

            if count % 500 == 0:
                print(f"  Inserted {count}/{len(gdf)} features...")
                await session.commit()  # commit in batches to avoid large transactions

        await session.commit()

        print("\nIngestion complete!")
        print(f"  Inserted : {count}")
        print(f"  Skipped  : {failed} (null geometry)")

        # Verify
        result = await session.execute(text("SELECT COUNT(*) FROM waterways"))
        total = result.scalar()
        print(f"  Total in DB: {total}")


async def main():
    try:
        await ingest_waterways()
    finally:
        await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
