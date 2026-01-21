from slope_raster import compute_farm_slope, slope_tester
from planting_points import generate_planting_points
from rotation import rotate_grid, rotation_tester
from slope_rules import apply_slope_rules

# The sapling estimation function accepts the DEM and boundary data of all farms, along with the farm coordinates and spacing rules (in meters).
# This function is the main/orchestrator of the Sapling Estimation Feature, it calls all core functions to produce the final planting plan.


def sapling_estimation(
    DEM_path: str,
    farm_boundary_path: str,
    farm_lon: float,
    farm_lat: float,
    spacing_m: float,
):
    # Compute slope raster for the given farm, output as farm_slope.tif
    compute_farm_slope(
        "DEM.tif", "farm_boundaries.gpkg", farm_lon, farm_lat, "farm_slope.tif"
    )
    if not slope_tester("farm_slope.tif"):  # Validate slope raster
        raise ValueError("ERROR: Slope raster failed validation checks.")

    # Generate planting points grid, output as farm_grid.shp
    generate_planting_points(
        "farm_slope.tif", "farm_boundaries.gpkg", spacing_m, "farm_grid.shp"
    )

    # Rotate planting points grid, output as rotated_grid.shp
    optimal_angle = rotate_grid(
        "farm_grid.shp", "farm_boundaries.gpkg", spacing_m, "rotated_grid.shp"
    )
    if not rotation_tester(
        "rotated_grid.shp", "farm_grid.shp"
    ):  # Validate rotated planting grid
        raise ValueError("ERROR: Slope raster failed validation checks.")

    # Apply slope rules to the planting grid
    sapling_count = apply_slope_rules(
        "rotated_grid.shp", "farm_slope.tif", "final_grid.shp"
    )

    # Print planting plan
    print(f"Optimal Rotation Angle: {optimal_angle}°")
    print(f"Final Sapling Count: {sapling_count}")

    return {"sapling_count": sapling_count, "optimal_angle": optimal_angle}
