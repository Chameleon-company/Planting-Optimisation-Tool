import geopandas as gpd
import numpy as np
from shapely.geometry import Point

# The planting points function accepts the polygon and bounds of the input farm, along with separate spacing rules (spacing_x, spacing_y in meters).
# The function first reprojects the farm polygon into to DEM CRS.
# A rectangular grid is generated based on these spacings.
# Each point is tested to ensure it falls within the farm polygon.


def generate_planting_points(farm_polygon, target_crs, slope_bounds: tuple, spacing_x: float, spacing_y: float):
    farm_poly_dem = gpd.GeoSeries([farm_polygon], crs=target_crs).iloc[0]  # Reprojects polygon

    # Generate a regular grid inside polygon bounds
    xmin, ymin, xmax, ymax = slope_bounds

    # Create x and y coordinates for planting points based on 3x3 spacing_m
    xs = np.arange(xmin, xmax, spacing_x)
    ys = np.arange(ymin, ymax, spacing_y)

    # Generate planting points inside the farm polygon
    planting_points = []
    for x in xs:  # Loop through x coordinates
        for y in ys:  # Loop through y coordinates
            point = Point(x, y)  # Create a point at the current coordinate
            if farm_poly_dem.contains(point):  # Keep only the points within the polygon
                planting_points.append(point)

    # Converts planting points into a GeoDataFrame
    return gpd.GeoDataFrame(geometry=planting_points, crs=target_crs)
