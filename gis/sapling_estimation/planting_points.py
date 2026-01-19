import numpy as np
import rasterio
import geopandas as gpd
from shapely.geometry import Point

spacing = 3.0

# The planting points function accepts the slope raster of the given farm and boundary data of all farms, along with spacing rule (in meters), and the output file.
# The function first reprojects the farm polygon into to slope raster CRS to align both data.
# A regular grid is then generated, and planting points are created based on spacing rules (3x3 spacing), where each point is tested to ensure it falls within the farm polygon.


def generate_planting_points(
    slope_raster_path: str, farm_boundary_path: str, spacing_m: float, output_path: str
):
    # Load farm boundaries data and checks if the file has a Coordinate Reference System (CRS)
    all_farm_boundaries = gpd.read_file(farm_boundary_path)
    if all_farm_boundaries.crs is None:  # Prints an error if file does not have a CRS
        raise ValueError(
            "ERROR: Farm boundary data has no CRS, please check farm boundary file."
        )

    # Merge all polygons into a single farm polygon
    farm_polygon = all_farm_boundaries.geometry.unary_union

    # Load slope raster file and reproject the farm polygon into to slope raster CRS
    with rasterio.open(slope_raster_path) as src:
        slope_crs = src.crs  # Reads CRS of slope data
        if slope_crs is None:
            raise ValueError(
                "ERROR: Slope raster has no CRS, please check slope raster file."
            )
        slope_bounds = src.bounds  # Gets the bounds of the farm polygon

    farm_poly_dem = (
        gpd.GeoSeries([farm_polygon], crs=all_farm_boundaries.crs)
        .to_crs(slope_crs)
        .iloc[0]
    )  # Reprojects polygon

    # Generate a regular grid inside polygon bounds
    xmin, ymin, xmax, ymax = slope_bounds

    # Create x and y coordinates for planting points based on 3x3 spacing_m
    xs = np.arange(xmin, xmax, spacing_m)
    ys = np.arange(ymin, ymax, spacing_m)

    # Generate planting points inside the farm polygon
    planting_points = []
    for x in xs:  # Loop through x coordinates
        for y in ys:  # Loop through y coordinates
            point = Point(x, y)  # Create a point at the current coordinate
            if farm_poly_dem.contains(point):  # Keep only the points within the polygon
                planting_points.append(point)

    # Converts planting points into a GeoDataFrame
    planting_points_gdf = gpd.GeoDataFrame(geometry=planting_points, crs=slope_crs)

    # Save planting points grid
    planting_points_gdf.to_file(output_path)
    # print(f"Generated {len(planting_points_gdf)} planting points.")
    print(f"Planting points grid saved to {output_path}")
