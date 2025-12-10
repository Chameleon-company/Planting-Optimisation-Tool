"""
One-time script to load farm_boundaries.gpkg, clean geometries,
compute centroids and area, and export a farm_table.csv for later use.

"""

import geopandas as gpd
import pandas as pd
from shapely.geometry import shape, mapping
import os


def build_farm_table():
    """
    Load the farm GPKG file, clean geometry, compute centroid & area,
    and output a final CSV inside gis/docs/.
    """

    # Paths relative to this file
    base_dir = os.path.dirname(__file__)
    gpkg_path = os.path.join(base_dir, "../assets/farm_boundaries.gpkg")
    docs_dir = os.path.join(base_dir, "../docs")

    print("Loading:", gpkg_path)

    # Load dataset
    gdf = gpd.read_file(gpkg_path)

    # Convert 3D geometry → 2D (drop Z)
    gdf["polygon"] = gdf.geometry.apply(lambda geom: shape(mapping(geom)))

    # Centroid (EPSG:4326)
    gdf["centroid"] = gdf["polygon"].centroid
    gdf["centroid_lat"] = gdf["centroid"].y
    gdf["centroid_lon"] = gdf["centroid"].x

    # Area in hectares — project to metric CRS first
    gdf_metric = gdf.to_crs(epsg=3857)
    gdf["area_ha"] = gdf_metric["polygon"].area / 10_000

    # Polygon WKT for database storage
    gdf["polygon_wkt"] = gdf["polygon"].apply(lambda g: g.wkt)

    # Build final DataFrame
    df = pd.DataFrame(
        {
            "name": gdf["Name"],
            "suco": gdf["Suco"],
            "aldeia": gdf["Aldeia"],
            "treeo_id": gdf.get("treeo_id", None),
            "plant_year": gdf.get("plant_year", None),
            "subdistrict": gdf.get("Subdistrict", None),
            "layer": gdf.get("layer", None),
            "centroid_lat": gdf["centroid_lat"],
            "centroid_lon": gdf["centroid_lon"],
            "area_ha": gdf["area_ha"],
            "polygon": gdf["polygon"],
            "polygon_wkt": gdf["polygon_wkt"],
        }
    )

    # Ensure docs folder exists
    os.makedirs(docs_dir, exist_ok=True)

    # Save output
    output_csv = os.path.join(docs_dir, "farm_table.csv")
    df.to_csv(output_csv, index=False)

    print("\nFarm Table Preview:")
    print(df.head())

    print("\nSaved:")
    print(f"- {output_csv}")


if __name__ == "__main__":
    build_farm_table()
