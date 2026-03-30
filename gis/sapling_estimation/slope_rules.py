import geopandas as gpd
import numpy as np
import rasterio

MAX_SLOPE = 15.0


def apply_slope_rules(
    slope_array: np.ndarray,
    rotated_grid: gpd.GeoDataFrame,
    slope_transform,
):
    xs = [point.x for point in rotated_grid.geometry]
    ys = [point.y for point in rotated_grid.geometry]

    rows, cols = rasterio.transform.rowcol(slope_transform, xs, ys)

    height, width = slope_array.shape
    kept_indices = []
    kept_slopes = []

    for idx, (r, c) in enumerate(zip(rows, cols)):
        if 0 <= r < height and 0 <= c < width:
            slope_value = float(slope_array[r, c])
            if slope_value <= MAX_SLOPE:
                kept_indices.append(idx)
                kept_slopes.append(slope_value)

    adjusted_points = rotated_grid.iloc[kept_indices].copy()

    adjusted_points = gpd.GeoDataFrame(
        adjusted_points,
        geometry=rotated_grid.geometry.name,
        crs=rotated_grid.crs,
    )

    return adjusted_points, kept_slopes
