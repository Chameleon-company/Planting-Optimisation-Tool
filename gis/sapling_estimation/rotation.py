import numpy as np
import geopandas as gpd
from shapely.geometry import Point
from shapely.affinity import rotate

spacing = 3.0

# The rotation function accepts the planting grid of the given farm and boundary data of all farms, along with spacing rule (in meters), and the output file.
# The function first merges the planting points into a single geometry to match the the grid and farm polygon.
# A base grid is then generated, and planting points are created based on spacing rules (3x3 spacing).
# The base grid is then rotated by 1° from 0° to 360°, where the number of points that fall within the polygon is counted for each angle.
# The optimal angle and highest point count is tracked during the rotation, which is then applied on the final rotation that outputs the final rotated planting grid.


def rotate_grid(
    farm_grid_path: str, farm_boundary_path: str, spacing_m: float, output_path: str
):
    # Load farm boundaries data and checks if the file has a Coordinate Reference System (CRS)
    all_farm_boundaries = gpd.read_file(farm_boundary_path)
    if all_farm_boundaries.crs is None:  # Prints an error if file does not have a CRS
        raise ValueError(
            "ERROR: Farm boundary data has no CRS, please check farm boundary file."
        )

    # Load planting grid file
    planting_grid = gpd.read_file(farm_grid_path)
    grid_crs = planting_grid.crs  # Reads CRS of planting grid data
    if grid_crs is None:
        raise ValueError(
            "ERROR: Planting grid has no CRS, please check farm grid file."
        )

    # Reproject farm boundaries to match planting grid CRS
    all_farm_boundaries = all_farm_boundaries.to_crs(grid_crs)

    # Merge planting points into a single geometry to match the grid with a farm polygon
    planting_grid_geometry = planting_grid.unary_union
    matching_farm = all_farm_boundaries[
        all_farm_boundaries.intersects(planting_grid_geometry)
    ]
    if matching_farm.empty:  # Prints an error if there is no match
        raise ValueError("ERROR: No farm boundary intersects the planting grid.")

    # Merge only the matching farm polygon
    farm_polygon = matching_farm.geometry.union_all()
    farm_poly_shp = gpd.GeoSeries([farm_polygon], crs=grid_crs).iloc[
        0
    ]  # Extract farm polygon as shapely geometry

    # Generate a regular grid inside planting grid bounds
    xmin, ymin, xmax, ymax = planting_grid.total_bounds

    # Create x and y coordinates for planting points based on 3x3 spacing_m
    xs = np.arange(xmin, xmax, spacing_m)
    ys = np.arange(ymin, ymax, spacing_m)

    # Generate planting points for the base grid
    base_points = []
    for x in xs:  # Loop through x coordinates
        for y in ys:  # Loop through y coordinates
            base_points.append(Point(x, y))  # Add point into array

    base_grid = gpd.GeoDataFrame(
        geometry=base_points, crs=grid_crs
    )  # Convert to GeoDataFrame

    # Initialization for rotation mechanism
    center = (
        farm_poly_shp.centroid
    )  # Mark the center of the farm polygon as the rotation origin
    optimal_angle = 0  # Stores the optimal rotation angle
    highest_count = -1  # Stores the highest point count

    # Loops through every degree from 0 to 360
    for angle in range(0, 361, 1):
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

    # Save rotated planting points grid
    final_grid.to_file(output_path)
    print(f"Optimal rotation angle: {optimal_angle}°")
    print(f"Generated {len(final_grid)} rotated planting points")
    print(f"Rotated planting points grid saved to {output_path}")


# Rotation Mechanism Tester Code
# Checks that the rotated_grid.shp grid does not have less planting points than the initial farm_grid.shp grid.


def rotation_tester(rotated_grid_path: str, farm_grid_path: str):
    rotated_grid = gpd.read_file(rotated_grid_path)
    planting_grid = gpd.read_file(farm_grid_path)
    valid = True

    # Point count check
    if len(rotated_grid) < len(planting_grid):
        print(
            "ERROR: Rotated grid cannot have fewer planting points than the initial planting grid"
        )
        valid = False

    return valid
