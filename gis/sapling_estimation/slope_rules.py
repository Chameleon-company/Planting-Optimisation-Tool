import geopandas as gpd
import numpy as np
import rasterio

MAX_SLOPE = 15.0  # Slope threshold


def apply_slope_rules(slope_array: np.ndarray, rotated_grid: gpd.GeoDataFrame, slope_transform):
    # Extract coordinates
    xs = [point.x for point in rotated_grid.geometry]
    ys = [point.y for point in rotated_grid.geometry]

    # Convert world coordinates to raster row/col
    rows, cols = rasterio.transform.rowcol(slope_transform, xs, ys)

    height, width = slope_array.shape
    slope_values = []

    for r, c in zip(rows, cols):
        if 0 <= r < height and 0 <= c < width:
            slope_values.append(slope_array[r, c])
        else:
            slope_values.append(float("inf"))

    # Keep only points below threshold
    keep_mask = [s <= MAX_SLOPE for s in slope_values]
    adjusted_points = rotated_grid.loc[keep_mask].copy()

    adjusted_points = gpd.GeoDataFrame(
        adjusted_points,
        geometry=rotated_grid.geometry.name,
        crs=rotated_grid.crs,
    )

    return adjusted_points
