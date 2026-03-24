import geopandas as gpd

from sapling_estimation.planting_points import generate_planting_points
from sapling_estimation.rotation import rotate_grid, rotation_tester
from sapling_estimation.slope_raster import compute_slope_from_array, slope_tester
from sapling_estimation.slope_rules import apply_slope_rules


# The sapling estimation function accepts the farm polygon and spacing (in meters).
# This function acts as the main orchestrator of the sapling estimation workflow,
# integrating DEM data from the database and producing the final planting plan.
def sapling_estimation(
    farm_polygon,
    spacing_m: float,
    farm_boundary_crs="EPSG:4326",
    debug=False,
    dem_array=None,
    dem_transform=None,
):
    # Ensure DEM data is provided from database
    if dem_array is None or dem_transform is None:
        raise ValueError("DEM array and transform must be provided from database")

    # Convert farm polygon to projected CRS (meters)
    farm_poly_crs = gpd.GeoSeries([farm_polygon], crs=farm_boundary_crs).to_crs("EPSG:3857").iloc[0]

    bounds = farm_poly_crs.bounds

    # Generate initial planting grid
    initial_grid = generate_planting_points(farm_poly_crs, "EPSG:3857", bounds, spacing_m)

    # Rotate grid to find optimal angle
    final_grid, optimal_angle = rotate_grid(farm_poly_crs, initial_grid, spacing_m)

    if not rotation_tester(final_grid, initial_grid):
        raise ValueError("Rotated grid failed validation")

    # Compute slope from DEM array
    slope_array = compute_slope_from_array(dem_array, 1, 1)

    if not slope_tester(slope_array):
        raise ValueError("Slope validation failed")

    # Apply slope rules to filter planting points
    final_grid = apply_slope_rules(slope_array, final_grid, dem_transform)

    # Ensure GeoDataFrame structure
    if final_grid.empty:
        final_grid = gpd.GeoDataFrame(geometry=[], crs="EPSG:3857")
    else:
        final_grid = gpd.GeoDataFrame(final_grid, geometry=final_grid.geometry.name, crs="EPSG:3857")

    # Convert back to geographic CRS for storage/output
    final_grid = final_grid.to_crs("EPSG:4326")

    # Debug output (optional)
    if debug:
        print(f"Optimal Rotation Angle: {optimal_angle}°")
        print(f"Final Sapling Count: {len(final_grid)}")

    return {
        "final_grid": final_grid,
        "slope_array": slope_array,
        "optimal_angle": optimal_angle,
    }