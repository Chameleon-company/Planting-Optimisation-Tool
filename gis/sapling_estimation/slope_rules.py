import geopandas as gpd
import rasterio
import numpy as np

MAX_SLOPE = 15.0  # Slope threshold

# The slope rules function accepts the slope array and rotated grid of the input farm.
# The function first samples the slope values at every planting point
# The points are then filtered by removing points that are on terrian steeper than the maximum threshold.


def apply_slope_rules(
    slope_array: np.ndarray, rotated_grid: gpd.GeoDataFrame, slope_transform
):
    # Extract the coordinates of every point for sampling
    xs = [point.x for point in rotated_grid.geometry]
    ys = [point.y for point in rotated_grid.geometry]

    # Sample the slope array using the transform (World coords -> Array indices)
    rows, cols = rasterio.transform.rowcol(slope_transform, xs, ys)

    # Filter out points that might fall outside the raster bounds
    valid_indices = []
    slope_values = []
    height, width = slope_array.shape

    for i, (r, c) in enumerate(zip(rows, cols)):
        if 0 <= r < height and 0 <= c < width:
            slope_values.append(slope_array[r, c])
            valid_indices.append(i)
        else:
            # Point is technically outside the slope raster extent
            slope_values.append(float("inf"))

    # Keep only points below the slope threshold
    keep_mask = [s <= MAX_SLOPE for s in slope_values]
    adjusted_points = rotated_grid[keep_mask].copy()

    return adjusted_points
