import asyncio
import os

import rasterio
from sqlalchemy import text

from src.database import AsyncSessionLocal


async def ingest_dem():
    print("Starting DEM ingestion (chunked full DEM)...", flush=True)

    # Locate DEM file
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    dem_path = os.path.join(base_dir, "..", "gis", "sapling_estimation", "data", "DEM.tif")

    if not os.path.exists(dem_path):
        raise FileNotFoundError(f"DEM file not found: {dem_path}")

    async with AsyncSessionLocal() as session:
        with rasterio.open(dem_path) as src:
            transform = src.transform
            srid = src.crs.to_epsg()

            print(f"DEM size: {src.width} x {src.height}", flush=True)

            # Tile size
            tile_size = 500

            # Clear table
            await session.execute(text("TRUNCATE dem_table RESTART IDENTITY;"))

            tile_count = 0

            # Loop through DEM in chunks
            for i in range(0, src.height, tile_size):
                for j in range(0, src.width, tile_size):
                    window = src.read(
                        1,
                        window=(
                            (i, min(i + tile_size, src.height)),
                            (j, min(j + tile_size, src.width)),
                        ),
                    ).astype(float)

                    height, width = window.shape

                    # Calculate tile origin
                    ulx = transform.c + j * transform.a
                    uly = transform.f + i * transform.e

                    values = window.tolist()

                    await session.execute(
                        text(
                            """
                            INSERT INTO dem_table (rast)
                            VALUES (
                                ST_SetValues(
                                    ST_AddBand(
                                        ST_MakeEmptyRaster(
                                            :width, :height,
                                            :ulx, :uly,
                                            :scale_x, :scale_y,
                                            0, 0,
                                            :srid
                                        ),
                                        1,
                                        '32BF'
                                    ),
                                    1,
                                    1,
                                    1,
                                    :values
                                )
                            )
                            """
                        ),
                        {
                            "width": width,
                            "height": height,
                            "ulx": float(ulx),
                            "uly": float(uly),
                            "scale_x": float(transform.a),
                            "scale_y": float(transform.e),
                            "srid": int(srid),
                            "values": values,
                        },
                    )

                    tile_count += 1

                # Commit after each row of tiles
                await session.commit()
                print(f"Committed row block {i} | tiles inserted: {tile_count}", flush=True)

    print(f"DEM ingestion completed successfully. Total tiles: {tile_count}", flush=True)


if __name__ == "__main__":
    asyncio.run(ingest_dem())
