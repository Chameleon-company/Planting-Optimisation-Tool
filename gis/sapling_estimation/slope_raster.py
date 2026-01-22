import numpy as np
import rasterio
from rasterio.mask import mask
import geopandas as gpd

# The slope raster function accepts the DEM and boundary data (polygon) of the input farm.
# The function first finds the farm polygon based on its coordinates and clips the DEM data onto the polygon.
# To compute slope, the DEM data is read to compute x and y gradient for computing magnitude.
# The magnitude is then converted to angle then degrees, forming the slope data.


def compute_farm_slope(dem_src, farm_gdf: gpd.GeoDataFrame):
    # Checks if the files have a Coordinate Reference System (CRS)
    if dem_src.crs is None:
        raise ValueError("ERROR: DEM data has no CRS, please check DEM file.")
    if farm_gdf.crs is None:
        raise ValueError(
            "ERROR: Input farm polygon has no CRS, please check farm polygon file."
        )

    farm_poly_dem = farm_gdf.to_crs(dem_src.crs).geometry.iloc[
        0
    ]  # Reprojects polygon to DEM CRS

    # Clips DEM to the farm polygon extent using the mask function
    # Returns Array dem_clipped containing elevation values for the farm polygon,
    # And Mapping dem_transform for mapping array to coordinates
    dem_clipped, dem_transform = mask(dem_src, [farm_poly_dem], crop=True)
    elevation = dem_clipped[0].astype(
        float
    )  # Extract elevation data in first layer of DEM file

    # Compute slope in degrees on the clipped DEM only
    width, height = dem_src.res  # Get size(resolution) of a single pixel
    y_grad, x_grad = np.gradient(elevation, height, width)  # Compute x and y gradient

    # Computes magnitude based on x and y gradient, which is converted into an angle, then degree
    slope = np.degrees(np.arctan(np.sqrt(x_grad**2 + y_grad**2)))

    # Prepare metadata(profile) for output
    profile = {
        "height": slope.shape[0],
        "width": slope.shape[1],
        "transform": dem_transform,
        "dtype": rasterio.float32,
        "count": 1,
    }

    return slope, dem_transform, profile


# Tester Code
# Checks that the slope.tif DEM does not contain NaN or infinite values, negative or > 90 degree values.


def slope_tester(slope_array: np.ndarray):
    valid = True

    # NaN or Inf value check
    if np.any(np.isnan(slope_array)):
        raise ValueError("ERROR: Data contains NaN values")
        valid = False
    if np.any(np.isinf(slope_array)):
        raise ValueError("ERROR: Data contains infinite values")
        valid = False

    # Range checks
    if np.any(slope_array < 0.0):
        raise ValueError("ERROR: Data contains negative slope values")
        valid = False
    if np.any(slope_array > 90.0):
        raise ValueError("ERROR: Data contains slope values greater than 90 degrees")
        valid = False

    return valid
