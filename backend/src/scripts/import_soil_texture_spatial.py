import asyncio
import os

import geopandas as gpd
import pandas as pd
from geoalchemy2.shape import from_shape
from shapely.geometry import MultiPolygon, Polygon
from sqlalchemy import delete

from src.database import AsyncSessionLocal, engine
from src.models.soil_texture_spatial import SoilTextureSpatial

SOIL_TEXTURE_PATH = os.getenv(
    "SOIL_TEXTURE_PATH",
    "src/scripts/data/soil_texture/Soil Texture.shp",
)

TEXTURE_COLUMN = "texture"


def to_multipolygon(geom):
    if isinstance(geom, Polygon):
        return MultiPolygon([geom])
    return geom


async def import_soil_texture_spatial():
    if not os.path.exists(SOIL_TEXTURE_PATH):
        raise FileNotFoundError(f"Soil texture shapefile not found: {SOIL_TEXTURE_PATH}")

    gdf = gpd.read_file(SOIL_TEXTURE_PATH)

    if gdf.crs is None:
        raise ValueError("Soil texture shapefile has no CRS.")

    gdf = gdf.to_crs(epsg=4326)

    if TEXTURE_COLUMN not in gdf.columns:
        raise ValueError(f"Column '{TEXTURE_COLUMN}' not found. Available columns: {list(gdf.columns)}")

    async with AsyncSessionLocal() as session:
        await session.execute(delete(SoilTextureSpatial))

        count = 0

        for _, row in gdf.iterrows():
            if row.geometry is None or row.geometry.is_empty:
                continue

            texture_value = row[TEXTURE_COLUMN]

            if pd.isna(texture_value):
                continue

            session.add(
                SoilTextureSpatial(
                    texture=str(texture_value),
                    source="soil texture shapefile",
                    geometry=from_shape(to_multipolygon(row.geometry), srid=4326),
                )
            )

            count += 1

        await session.commit()

    print(f"Imported {count} soil texture spatial polygons.")


async def main():
    try:
        await import_soil_texture_spatial()
    finally:
        await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
