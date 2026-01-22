import numpy as np
import geopandas as gpd
from shapely.geometry import Point
from shapely.affinity import rotate

# The rotation function accepts the polygon and planting grid of the input farm, along with spacing rule (in meters).
# The function first generates a base grid, and planting points are created based on spacing rules (3x3 spacing).
# The base grid is then rotated by 1° from 0° to 90°, where the number of points that fall within the polygon is counted for each angle.
# The optimal angle and highest point count is tracked during the rotation, which is then applied on the final rotation that outputs the final rotated planting grid.


def rotate_grid(farm_polygon, planting_grid: gpd.GeoDataFrame, spacing_m: float):
    farm_poly_series = gpd.GeoSeries(
        [farm_polygon], crs=planting_grid.crs
    )  # Extract farm polygon as Geoseries

    # Generate a regular grid inside polygon bounds
    xmin, ymin, xmax, ymax = farm_poly_series.total_bounds
    farm_poly_shp = farm_poly_series.iloc[
        0
    ]  # Extract shapely geometry from farm polygon Geoseries

    # Create x and y coordinates for planting points based on 3x3 spacing_m
    xs = np.arange(xmin, xmax, spacing_m)
    ys = np.arange(ymin, ymax, spacing_m)

    # Generate planting points for the base grid
    base_points = []
    for x in xs:  # Loop through x coordinates
        for y in ys:  # Loop through y coordinates
            base_points.append(Point(x, y))  # Add point into array

    base_grid = gpd.GeoDataFrame(
        geometry=base_points, crs=planting_grid.crs
    )  # Convert to GeoDataFrame

    # Initialization for rotation mechanism
    center = (
        farm_poly_shp.centroid
    )  # Mark the center of the farm polygon as the rotation origin
    optimal_angle = 0  # Stores the optimal rotation angle
    highest_count = -1  # Stores the highest point count

    # Loops through every degree from 0 to 90
    for angle in range(0, 91, 1):
        # Copy base grid and rotate at origin
        rotated = base_grid.copy()
        rotated["geometry"] = rotated.geometry.apply(
            lambda g: rotate(g, angle, origin=center)
        )
        count = rotated.within(
            farm_poly_shp
        ).sum()  # Count number of points within the rotated farm polygon

        # Update new optimal angle and highest count if more points fall within the current rotated farm polygon
        if count > highest_count:
            optimal_angle = angle
            highest_count = count

    # Apply final rotation on the original base grid using optimal angle
    final_grid = base_grid.copy()
    final_grid["geometry"] = final_grid.geometry.apply(
        lambda g: rotate(g, optimal_angle, origin=center)
    )
    final_grid = final_grid[
        final_grid.within(farm_poly_shp)
    ]  # Keep only the points within the polygon

    return final_grid, optimal_angle


# Rotation Mechanism Tester Code
# Checks that the rotated grid does not have less planting points than the initial grid.


def rotation_tester(rotated_grid: gpd.GeoDataFrame, planting_grid: gpd.GeoDataFrame):
    valid = True

    # Point count check
    if len(rotated_grid) < len(planting_grid):
        raise ValueError(
            "ERROR: Rotated grid cannot have fewer planting points than the initial planting grid"
        )
        valid = False

    return valid
