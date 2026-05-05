import asyncio
import os

import geopandas as gpd
import pandas as pd
from geoalchemy2.shape import from_shape
from shapely.geometry import MultiPolygon, Polygon
from sqlalchemy import delete

from src.database import AsyncSessionLocal, engine
from src.models.soil_ph import SoilPH

SOIL_PH_PATH = os.getenv(
    "SOIL_PH_PATH",
    "src/scripts/data/soil_ph/soil pH.shp",
)

PH_COLUMN = "ph"


def to_multipolygon(geom):
    if isinstance(geom, Polygon):
        return MultiPolygon([geom])
    return geom


async def import_soil_ph():
    if not os.path.exists(SOIL_PH_PATH):
        raise FileNotFoundError(f"Soil pH shapefile not found: {SOIL_PH_PATH}")

    gdf = gpd.read_file(SOIL_PH_PATH)

    if gdf.crs is None:
        raise ValueError("Soil pH shapefile has no CRS.")

    gdf = gdf.to_crs(epsg=4326)

    if PH_COLUMN not in gdf.columns:
        raise ValueError(f"Column '{PH_COLUMN}' not found. Available columns: {list(gdf.columns)}")

    async with AsyncSessionLocal() as session:
        await session.execute(delete(SoilPH))

        count = 0

        for _, row in gdf.iterrows():
            if row.geometry is None or row.geometry.is_empty:
                continue

            ph_value = row[PH_COLUMN]

            if pd.isna(ph_value):
                continue

            session.add(
                SoilPH(
                    ph=float(ph_value),
                    source="soil pH shapefile",
                    geometry=from_shape(to_multipolygon(row.geometry), srid=4326),
                )
            )

            count += 1

        await session.commit()

    print(f"Imported {count} soil pH polygons.")


async def main():
    try:
        await import_soil_ph()
    finally:
        await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
