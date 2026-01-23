from pathlib import Path
import geopandas as gpd
import rasterio

from sapling_estimation.slope_raster import compute_farm_slope, slope_tester
from sapling_estimation.planting_points import generate_planting_points
from sapling_estimation.rotation import rotate_grid, rotation_tester
from sapling_estimation.slope_rules import apply_slope_rules

# The sapling estimation function accepts the farm polygon of the input farm and the spacing rules (in meters).
# This function is the main/orchestrator of the Sapling Estimation Feature, it calls all core functions to produce the final planting plan.


def sapling_estimation(
    farm_polygon, spacing_m: float, farm_boundary_crs="EPSG:4326", debug=False
):
    # Create a GeoDataFrame
    farm_gdf = gpd.GeoDataFrame(geometry=[farm_polygon], crs=farm_boundary_crs)

    # Load DEM file
    here = Path(__file__).resolve().parent

    # Allow tests to override DEM path
    here = Path(__file__).resolve().parent
    DEM_path = here / "data" / "DEM.tif"

    with rasterio.open(DEM_path) as dem_src:
        if dem_src.crs is None:
            raise ValueError("ERROR: DEM data has no CRS, please check DEM file.")

        # Compute slope in memory
        slope_array, slope_transform, profile_updates = compute_farm_slope(
            dem_src, farm_gdf
        )

        output_profile = dem_src.profile.copy()
        output_profile.update(profile_updates)

    if not slope_tester(slope_array):  # Validate slope array
        raise ValueError("ERROR: Slope raster failed validation checks.")

    # Reprojects polygon to DEM CRS and get the bounds of the farm polygon
    farm_poly_crs = (
        gpd.GeoSeries([farm_polygon], crs=farm_boundary_crs).to_crs(dem_src.crs).iloc[0]
    )
    bounds = farm_poly_crs.bounds

    # Generate planting points grid
    initial_grid = generate_planting_points(
        farm_poly_crs, dem_src.crs, bounds, spacing_m
    )

    # Rotate planting points grid
    rotated_grid, optimal_angle = rotate_grid(farm_poly_crs, initial_grid, spacing_m)
    if not rotation_tester(
        rotated_grid, initial_grid
    ):  # Validate rotated planting grid
        raise ValueError("ERROR: Rotated grid failed validation checks.")

    # Apply slope rules to the planting grid
    final_grid = apply_slope_rules(slope_array, rotated_grid, slope_transform)

    if debug:
        # Print planting plan
        print(f"Optimal Rotation Angle: {optimal_angle}°")
        print(f"Final Sapling Count: {len(final_grid)}")

        # Save the final planting grid to file
        final_grid.to_file("final_grid.shp")
        print(f"Final planting plan saved to {'final_grid.shp'}")

    return {"sapling_count": len(final_grid), "optimal_angle": optimal_angle}
