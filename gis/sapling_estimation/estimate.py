import geopandas as gpd
import numpy as np
from rasterio.transform import from_origin

from sapling_estimation.planting_points import generate_planting_points
from sapling_estimation.rotation import rotate_grid, rotation_tester
from sapling_estimation.slope_raster import compute_slope_from_array, slope_tester
from sapling_estimation.slope_rules import apply_slope_rules


def sapling_estimation(
    farm_polygon,
    spacing_m: float,
    farm_boundary_crs="EPSG:4326",
    debug=False,
    dem_array=None,
    dem_upper_left_x=None,
    dem_upper_left_y=None,
    pixel_width=1.0,
    pixel_height=1.0,
    dem_crs="EPSG:4326",
):
    """
    Main orchestrator for sapling estimation.
    Uses DEM data from database to compute slope and generate planting plan.
    """

    if dem_array is None:
        raise ValueError("DEM array must be provided")

    if dem_upper_left_x is None or dem_upper_left_y is None:
        raise ValueError("DEM origin must be provided")

    dem_array = np.array(dem_array, dtype=float)

    dem_transform = from_origin(
        dem_upper_left_x,
        dem_upper_left_y,
        pixel_width,
        pixel_height,
    )

    farm_poly_projected = gpd.GeoSeries([farm_polygon], crs=farm_boundary_crs).to_crs("EPSG:3857").iloc[0]

    bounds = farm_poly_projected.bounds

    initial_grid = generate_planting_points(farm_poly_projected, "EPSG:3857", bounds, spacing_m)

    rotated_grid, optimal_angle = rotate_grid(farm_poly_projected, initial_grid, spacing_m)

    if not rotation_tester(rotated_grid, initial_grid):
        raise ValueError("Rotated grid failed validation")

    slope_array = compute_slope_from_array(
        dem_array,
        pixel_width=pixel_width,
        pixel_height=pixel_height,
    )

    if not slope_tester(slope_array):
        raise ValueError("Slope validation failed")

    rotated_grid_in_dem_crs = rotated_grid.to_crs(dem_crs)

    filtered_grid, slope_values = apply_slope_rules(
        slope_array,
        rotated_grid_in_dem_crs,
        dem_transform,
    )

    if filtered_grid.empty:
        final_grid = gpd.GeoDataFrame(geometry=[], crs=dem_crs)
    else:
        final_grid = gpd.GeoDataFrame(
            filtered_grid,
            geometry=filtered_grid.geometry.name,
            crs=dem_crs,
        )

    final_grid = final_grid.to_crs("EPSG:4326")

    if debug:
        print(f"Optimal Rotation Angle: {optimal_angle}°")
        print(f"Final Sapling Count: {len(final_grid)}")

    return {
        "final_grid": final_grid,
        "slope_array": slope_array,
        "slope_values": slope_values,
        "optimal_angle": optimal_angle,
    }
