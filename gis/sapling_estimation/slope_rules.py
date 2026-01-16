import geopandas as gpd
import rasterio

MAX_SLOPE = 15.0  # Slope threshold

# The slope rules function accepts the rotated grid and slope raster of the given farm, and the output file.
# The function first samples the slope values at every planting point
# The points are then filtered by removing points that are on terrian steeper than the maximum threshold.


def apply_slope_rules(rotated_grid_path: str, slope_raster_path: str, output_path: str):
    # Load rotated planting grid data and checks if the file has a Coordinate Reference System (CRS)
    planting_points = gpd.read_file(rotated_grid_path)
    points_crs = planting_points.crs  # Reads CRS of rotated planting grid data
    if points_crs is None:  # Prints an error if file does not have a CRS
        raise ValueError(
            "ERROR: Rotated planting grid has no CRS, please check rotated grid file."
        )

    # Load slope raster file
    with rasterio.open(slope_raster_path) as src:
        slope_crs = src.crs
        if slope_crs is None:
            raise ValueError(
                "ERROR: Slope raster has no CRS, please check slope raster file."
            )

        # Reproject planting points to slope CRS if both have different CRS
        if points_crs != slope_crs:
            planting_points = planting_points.to_crs(slope_crs)

        # Extract the coordinates of every point for sampling
        coordinates = [(point.x, point.y) for point in planting_points.geometry]

        # Samples the slope raster to extract slope values for every point into a list
        slope_values = list(src.sample(coordinates))
        slope_values = [
            float(v[0]) for v in slope_values
        ]  # Convert from nested array to list containing floats

    # Keep only points below the slope threshold
    adjusted_points = planting_points[[s <= MAX_SLOPE for s in slope_values]]

    # Save adjusted planting grid
    adjusted_points.to_file(output_path)
    # print(f"Original points: {len(planting_points)}")
    # print(f"Remaining points: {len(adjusted_points)}")
    print(f"Adjusted planting points saved to {output_path}")
