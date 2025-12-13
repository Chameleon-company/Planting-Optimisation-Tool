from config.settings import (
    RAINFALL_ASSET_ID,
    RAINFALL_BAND,
    RAINFALL_SCALE,
    TEMP_ASSET_ID,
    TEMP_BAND,
    TEMP_SCALE,
    SOIL_PH_ASSET_ID,
    SOIL_PH_FIELD,
    DEM_ASSET_ID,
    DEM_BAND,
    DEM_SCALE,
    SLOPE_BAND,
    SOIL_TEXTURE_ASSET_ID,
    SOIL_TEXTURE_FIELD,
    BOUNDARY_TIMOR_ASSET_ID,
)

from core.geometry_parser import parse_geometry


# Function return to float
def _ee_to_float(value):
    """Convert an ee.Number or Python scalar to Python float, handling None safely."""
    if value is None:
        return None
    if hasattr(value, "getInfo"):
        value = value.getInfo()
    return float(value) if value is not None else None


def get_rainfall(geometry, year: int | None = None):
    """
    Return mean annual rainfall (mm) for a given geometry (point or polygon).

    Parameters
    ----------
    geometry : ee.Geometry
        ee.Geometry.Point or ee.Geometry.Polygon for the farm.
    year : int, optional
        Target year. Currently we only have a 5-year average (2020–2024),
        so `year` is accepted for future extension but not used yet.
    """
    import ee

    geometry = parse_geometry(geometry)

    # Select rainfall dataset
    img = ee.Image(RAINFALL_ASSET_ID).select(RAINFALL_BAND)

    stats = img.reduceRegion(
        reducer=ee.Reducer.mean(),
        geometry=geometry,
        scale=RAINFALL_SCALE,
        maxPixels=1e9,
    )

    value = stats.get(RAINFALL_BAND)
    value = int(round(_ee_to_float(value))) if value is not None else None
    return value


def get_temperature(geometry: list[list], year: int | None = None):
    """
    Return mean annual temperature for a given geometry (point or polygon).

    Parameters
    ----------
    geometry : ee.Geometry.Point or ee.Geometry.Polygon for the farm.
    year : int, optional
        Target year. Currently we only have a 5-year average (2020–2024),
        so `year` is accepted for future extension but not used yet.
    """
    import ee

    geometry = parse_geometry(geometry)

    # Select rainfall dataset
    img = ee.Image(TEMP_ASSET_ID).select(TEMP_BAND)

    stats = img.reduceRegion(
        reducer=ee.Reducer.mean(),
        geometry=geometry,
        scale=TEMP_SCALE,
        maxPixels=1e9,
    )

    value = stats.get(TEMP_BAND)
    value = int(round(_ee_to_float(value))) if value is not None else None
    return value


def get_ph(geometry: list[list], year: int | None = None):
    """
    Return soil pH for a given geometry (point or polygon).

    Parameters
    ----------
    geometry : ee.Geometry.Point or ee.Geometry.Polygon for the farm.
    year : int, optional
        Reserved for future use if soil pH becomes time-varying.
        Currently ignored.
    """
    import ee

    geometry = parse_geometry(geometry)

    # Load soil pH FeatureCollection
    file = ee.FeatureCollection(SOIL_PH_ASSET_ID)

    # Find the polygon that intersects this geometry
    feature = file.filterBounds(geometry).first()
    if feature is None:
        return None

    # Read the 'ph' attribute from the feature
    value = feature.get(SOIL_PH_FIELD)
    return _ee_to_float(value)


def get_elevation(geometry: list[list], year: int | None = None):
    """
    Return mean elevation (m) for point a point or polygon from DEM asset.

    Parameters
    ----------
    geometry : ee.Geometry.Point or ee.Geometry.Polygon for the farm.
    year : int, optional
        Reserved for future use if DEM data becomes time-varying.
        Currently ignored.
    """
    import ee

    geometry = parse_geometry(geometry)

    # Load DEM
    img = ee.Image(DEM_ASSET_ID).select(DEM_BAND)

    # Find the polygon that intersects this geometry
    stats = img.reduceRegion(
        reducer=ee.Reducer.mean(), geometry=geometry, scale=DEM_SCALE, maxPixels=1e9
    )

    value = stats.get(DEM_BAND)
    value = int(round(_ee_to_float(value))) if value is not None else None
    return value


def get_slope(geometry: list[list], year: int | None = None):
    """
    Return mean slope (degrees) for point a point or polygon from DEM asset.

    Parameters
    ----------
    geometry : ee.Geometry.Point or ee.Geometry.Polygon for the farm.
    year : int, optional
        Reserved for future use if DEM data becomes time-varying.
        Currently ignored.
    """
    import ee

    geometry = parse_geometry(geometry)

    # Load DEM
    img = ee.Image(DEM_ASSET_ID).select(DEM_BAND)

    # Create slope image
    slope_img = ee.Terrain.slope(img)

    # Find the polygon that intersects this geometry
    stats = slope_img.reduceRegion(
        reducer=ee.Reducer.mean(), geometry=geometry, scale=DEM_SCALE, maxPixels=1e9
    )

    value = stats.get(SLOPE_BAND)
    return round(_ee_to_float(value), 3)


def get_texture(geometry: list[list], year: int | None = None):
    """
    Return soil texture for a given geometry (point or polygon).

    Parameters
    ----------
    geometry : ee.Geometry.Point or ee.Geometry.Polygon for the farm.
    year : int, optional
        Reserved for future use if soil texture becomes time-varying.
        Currently ignored.
    """
    import ee

    geometry = parse_geometry(geometry)

    # Load soil texture FeatureCollection
    file = ee.FeatureCollection(SOIL_TEXTURE_ASSET_ID)

    # Find the polygon that intersects this geometry
    feature = file.filterBounds(geometry).first()
    if feature is None:
        return None

    # Read the 'ph' attribute from the feature
    value = feature.get(SOIL_TEXTURE_FIELD)

    # Convert into string
    if hasattr(value, "getInfo"):
        value = value.getInfo()

    return value


def get_area_ha(geometry: list[list]):
    """
    Return area of the input geometry in hectares.

    Parameters
    ----------
    geometry : ee.Geometry.Point or ee.Geometry.Polygon for the farm.
    """

    geometry = parse_geometry(geometry)

    # Call area based on point and polygon
    value = geometry.area(maxError=1)

    # Convert into string
    if hasattr(value, "getInfo"):
        value = value.getInfo()

    return round(float(value) / 10_000.0, 3)


def get_dist_to_coast(geometry: list[list]):
    """
    Return distance to coast_boundary by measure the distance of the centroild point to timor boundary

    Parameters
    ----------
    geometry : ee.Geometry.Point or ee.Geometry.Polygon for the farm.
    """

    import ee

    geometry = parse_geometry(geometry)

    # Get centroid point
    centroid = geometry.centroid(maxError=1)

    # Timor Boundary
    boundary_fc = ee.FeatureCollection(BOUNDARY_TIMOR_ASSET_ID)
    country_geom = boundary_fc.geometry()

    value = centroid.distance(country_geom, 100)

    return round(_ee_to_float(value) / 1000.0, 3)
