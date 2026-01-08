import numpy as np
import rasterio
from rasterio.mask import mask
import geopandas as gpd
from shapely.geometry import Point

# The slope raster function accepts the DEM and boundary data of all farms, along with the coordinates of the farm where we want to calculate its slope data, and the output file.
# The function first finds the farm polygon based on its coordinates and clips the DEM data onto the polygon.
# To compute slope, the DEM data is read to compute x and y gradient for computing magnitude.
# The magnitude is then converted to angle then degrees, forming the slope data.


def compute_farm_slope(
    DEM_path: str,
    farm_boundary_path: str,
    farm_lon: float,
    farm_lat: float,
    output_path: str,
):
    # Load farm boundaries data and checks if the file has a Coordinate Reference System (CRS)
    all_farm_boundaries = gpd.read_file(farm_boundary_path)
    if all_farm_boundaries.crs is None:  # Prints an error if file does not have a CRS
        raise ValueError(
            "ERROR: Farm boundary data has no CRS, please check farm boundary file."
        )

    # Create a point based on the given coordinates to find the farm's polygon
    # Converts CRS code of coordinates to match the farm boundaries' (EPSG:3857)
    farm_point = gpd.GeoSeries([Point(farm_lon, farm_lat)], crs="EPSG:4326").to_crs(
        all_farm_boundaries.crs
    )

    # Finds polygon that contains the point
    polygon_in_point = all_farm_boundaries[
        all_farm_boundaries.geometry.contains(farm_point.iloc[0])
    ]
    if len(polygon_in_point) == 0:  # Checks if there is a polygon match
        raise ValueError("ERROR: No farm polygon matches given coordinates.")
    farm_polygon = polygon_in_point.geometry.iloc[
        0
    ]  # Extract geometry of the matched farm polygon

    # Load DEM file and reproject the farm polygon into to DEM CRS
    with rasterio.open(DEM_path) as src:
        DEM_crs = src.crs  # Reads CRS of DEM data
        if DEM_crs is None:
            raise ValueError("ERROR: DEM data has no CRS, please check DEM file.")
        farm_poly_dem = (
            gpd.GeoSeries([farm_polygon], crs=all_farm_boundaries.crs)
            .to_crs(DEM_crs)
            .iloc[0]
        )  # Reprojects polygon to DEM CRS

        # Clips DEM to the farm polygon extent using the mask function
        # Returns Array dem_clipped containing elevation values for the farm polygon,
        # And Mapping dem_transform for mapping array to coordinates
        dem_clipped, dem_transform = mask(src, [farm_poly_dem], crop=True)
        elevation = dem_clipped[0].astype(
            float
        )  # Extract elevation data in first layer of DEM file

        # Compute slope in degrees on the clipped DEM only
        width, height = src.res  # Get size(resolution) of a single pixel
        y_grad, x_grad = np.gradient(
            elevation, height, width
        )  # Compute x and y gradient
        # Computes magnitude based on x and y gradient, which is converted into an angle, then degree
        slope = np.degrees(np.arctan(np.sqrt(x_grad**2 + y_grad**2)))

        # Prepare farm profile for output
        profile = src.profile.copy()
        profile.update(
            height=slope.shape[0],
            width=slope.shape[1],
            transform=dem_transform,
            dtype=rasterio.float32,
            count=1,
        )
        slope = slope.astype(np.float32)

    # Save slope raster
    with rasterio.open(
        output_path, "w", **profile
    ) as dest:  # Save updated data into output file path
        dest.write(slope, 1)  # Write slope data
    print(f"Farm slope raster saved to {output_path}")


# Tester Code
# Checks that the slope.tif DEM does not contain NaN or infinite values, negative or > 90 degree values.


def slope_tester(farm_DEM_path: str):
    with rasterio.open(farm_DEM_path) as src:
        slope = src.read(
            1
        )  # Read data in first layer of slope file & write into array 'slope'
    valid = True

    # NaN or Inf value check
    if np.any(np.isnan(slope)):
        print("ERROR: Data contains NaN values")
        valid = False
    if np.any(np.isinf(slope)):
        print("ERROR: Data contains infinite values")
        valid = False

    # Range checks
    if np.any(slope < 0.0):
        print("ERROR: Data contains negative slope values")
        valid = False
    if np.any(slope > 90.0):
        print("ERROR: Data contains slope values greater than 90 degrees")
        valid = False

    return valid
