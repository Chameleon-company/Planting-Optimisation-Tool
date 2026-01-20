"""
Extract environmental data from various sources.

Uses config/settings.py for all dataset configurations.
"""

import ee
from config.settings import get_dataset_config, TEXTURE_MAP
from core.geometry_parser import parse_geometry


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================


def _ee_to_float(value):
    """Convert an ee.Number or Python scalar to Python float, handling None safely."""
    if value is None:
        return None
    if hasattr(value, "getInfo"):
        value = value.getInfo()
    return float(value) if value is not None else None


def _apply_post_process(value, post_process: str):
    """Apply post-processing to extracted value."""
    if value is None:
        return None

    if post_process == "round_int":
        return int(round(value))
    elif post_process == "round_1dp":
        return round(value, 1)
    elif post_process == "round_2dp":
        return round(value, 2)
    elif post_process == "round_3dp":
        return round(value, 3)

    return value


def _get_reducer(reducer_name: str):
    """Get Earth Engine reducer from name."""
    reducers = {
        "mean": ee.Reducer.mean(),
        "sum": ee.Reducer.sum(),
        "median": ee.Reducer.median(),
        "min": ee.Reducer.min(),
        "max": ee.Reducer.max(),
    }
    return reducers.get(reducer_name, ee.Reducer.mean())


# ============================================================================
# RASTER EXTRACTION
# ============================================================================


def _extract_from_raster(geometry, dataset_name: str, year: int | None = None):
    """
    Generic function to extract value from raster dataset.
    """
    config = get_dataset_config(dataset_name)
    geometry = parse_geometry(geometry)

    # Load dataset
    if year and config.get("temporal", False):
        # For temporal datasets, filter by year
        collection = ee.ImageCollection(config["asset_id"])
        collection = collection.filterDate(f"{year}-01-01", f"{year}-12-31")

        # Select band first, then reduce
        collection = collection.select(config["band"])

        # Reduce collection based on reducer type
        reducer_name = config.get("reducer", "mean")
        if reducer_name == "sum":
            img = collection.sum()
        else:
            img = collection.mean()

        # After reduction, the band name is preserved
        band_name = config["band"]
    else:
        # Single image
        img = ee.Image(config["asset_id"]).select(config["band"])
        band_name = config["band"]

    # Extract value
    reducer = _get_reducer(config.get("reducer", "mean"))
    stats = img.reduceRegion(
        reducer=reducer,
        geometry=geometry,
        scale=config["scale"],
        maxPixels=1e9,
    )

    value = _ee_to_float(stats.get(band_name))

    if value is None:
        return None

    # Apply transformations
    if "scale_factor" in config:
        value *= config["scale_factor"]

    if "offset" in config:
        value += config["offset"]

    if "bias_correction" in config:
        value += config["bias_correction"]

    # Apply post-processing
    if "post_process" in config:
        value = _apply_post_process(value, config["post_process"])

    return value


# ============================================================================
# VECTOR EXTRACTION
# ============================================================================


def _extract_from_vector(geometry, dataset_name: str):
    """
    Generic function to extract value from vector dataset.
    """
    config = get_dataset_config(dataset_name)
    geometry = parse_geometry(geometry)

    # Load FeatureCollection
    fc = ee.FeatureCollection(config["asset_id"])

    # Find intersecting feature
    feature = fc.filterBounds(geometry).first()

    if feature is None:
        return None

    # Get field value
    value = feature.get(config["field"])
    value = _ee_to_float(value)

    if value is None:
        return None

    # Apply transformations
    if "scale_factor" in config:
        value *= config["scale_factor"]

    # Apply post-processing
    if "post_process" in config:
        value = _apply_post_process(value, config["post_process"])

    return value


# ============================================================================
# PUBLIC API - Keep same function names for compatibility
# ============================================================================


def get_rainfall(geometry, year: int | None = None):
    """
    Return mean annual rainfall (mm) for a given geometry.

    Dataset: CHIRPS (Pearson r=0.96, MAE=23mm)
    """
    return _extract_from_raster(geometry, "rainfall", year=year or 2024)


def get_temperature(geometry, year: int | None = None):
    """
    Return mean annual temperature (°C) for a given geometry.

    Dataset: MODIS LST (Pearson r=0.87, MAE=1.5°C with -4.43°C correction)
    """
    return _extract_from_raster(geometry, "temperature", year=year or 2024)


def get_elevation(geometry, year: int | None = None):
    """
    Return mean elevation (m) for a given geometry.

    Dataset: SRTM DEM (Pearson r=0.98, MAE=11m)
    """
    return _extract_from_raster(geometry, "elevation")


def get_ph(geometry, year: int | None = None):
    """
    Return soil pH for a given geometry.

    Dataset: OpenLandMap (Pearson r=0.18, MAE=1.21)
    WARNING: Low correlation - consider using local data instead.
    """
    return _extract_from_raster(geometry, "soil_ph")


def get_slope(geometry, year: int | None = None):
    """
    Return mean slope (degrees) for a given geometry.

    Derived from SRTM DEM.
    """
    geometry = parse_geometry(geometry)
    config = get_dataset_config("dem")

    # Load DEM
    dem = ee.Image(config["asset_id"]).select(config["band"])

    # Calculate slope
    slope_img = ee.Terrain.slope(dem)

    # Extract value
    stats = slope_img.reduceRegion(
        reducer=ee.Reducer.mean(),
        geometry=geometry,
        scale=config["scale"],
        maxPixels=1e9,
    )

    value = _ee_to_float(stats.get("slope"))
    return round(value, 3) if value is not None else None


def get_texture(geometry, year: int | None = None):
    """
    Return soil texture value for a given geometry.
    Note: Currently using OpenLandMap pH as a demonstration of GEE extraction capability.
    Replace with actual soil texture asset when available.
    """
    config = get_dataset_config("soil_texture")

    # Check if this is using a raster dataset (like our pH proxy)
    if config["type"] == "raster":
        # Extract as raster value
        return _extract_from_raster(geometry, "soil_texture", year=year)

    # Original vector-based extraction (for when actual texture asset is available)
    try:
        geometry = parse_geometry(geometry)

        fc = ee.FeatureCollection(config["asset_id"])
        feature = fc.filterBounds(geometry).first()

        if feature is None:
            return None

        value = feature.get(config["field"])

        if hasattr(value, "getInfo"):
            value = value.getInfo()

        return value
    except Exception as e:
        # Handle case where asset doesn't exist or other GEE errors
        print(f"Warning: Could not extract soil texture: {e}")
        return None


def _normalize_texture_name(value) -> str | None:
    """Normalize the texture name."""
    if value is None:
        return None

    txt = str(value).strip().lower()
    if not txt:
        return None

    if "," in txt:
        txt = txt.split(",")[0].strip()

    if txt in ("organic", "variable"):
        return None

    return txt


def get_texture_id(geometry, year: int | None = None) -> int | None:
    """
    Return soil texture ID (1-12) for a given geometry.
    Note: Currently using pH value as demonstration. Returns None for numeric pH values
    since they don't map to standard USDA texture classifications.
    """
    texture_value = get_texture(geometry, year=year)

    if texture_value is None:
        return None

    # If it's a numeric value (like pH), we can't map it to texture classes
    # This demonstrates successful GEE extraction but acknowledges data limitation
    if isinstance(texture_value, (int, float)):
        # pH values range 3-10, we could map to arbitrary texture IDs for demonstration
        # but it's more honest to return None since pH ≠ texture
        return None

    # Original texture name mapping (for when actual texture data is available)
    norm_name = _normalize_texture_name(texture_value)

    if norm_name is None:
        return None

    return TEXTURE_MAP.get(norm_name)


def get_area_ha(geometry):
    """
    Return area of the input geometry in hectares.
    """
    geometry = parse_geometry(geometry)
    area_m2 = geometry.area(maxError=1).getInfo()
    return round(float(area_m2) / 10_000.0, 3)


def get_centroid_lat_lon(geometry):
    """
    Return centroid as (lat, lon) rounded to 3 decimal places.
    """
    geom = parse_geometry(geometry)
    centroid = geom.centroid(maxError=1)
    coords = centroid.coordinates().getInfo()

    lon, lat = float(coords[0]), float(coords[1])
    return round(lat, 3), round(lon, 3)
