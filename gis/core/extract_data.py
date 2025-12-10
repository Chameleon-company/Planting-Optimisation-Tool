def get_rainfall(lat: float, lon: float):
    """Returns the 5-year (2020 - 2024) average annual rainfall (mm) at a given point in Timor-Leste from PO's Dataset."""
    import ee

    # Create a point geometry from longitude (lon), latitude (lat)
    point = ee.Geometry.Point([lon, lat])

    # Rainfal from Annual Rainfall data from PO
    rain = ee.Image(
        "projects/scenic-block-466510-c5/assets/CHIRPS_5yr_Avg_Annual_Rainfall_2020_2024_30m"
    ).select("b1")

    rain_dict = rain.reduceRegion(
        reducer=ee.Reducer.mean(), geometry=point, scale=30, maxPixels=1e9
    )

    # Return as Python Float
    rain_value = rain_dict.get("b1")

    # Check it return Python Float
    if hasattr(rain_value, "getInfo"):
        rain_value = rain_value.getInfo()

    return float(rain_value) if rain_value is not None else None


def get_temperature(lat: float, lon: float):
    """Returns the 5-year (2020 - 2024) average land surface temperature (°C) at a given point in Timor-Leste from PO's Dataset."""
    import ee

    # Create a point geometry from longitude (lon), latitude (lat)
    point = ee.Geometry.Point([lon, lat])

    # Rainfal from Annual Rainfall data from PO
    temp = ee.Image(
        "projects/scenic-block-466510-c5/assets/MOD11A2_5yr_Avg_Annual_temperature_2020_2024_30m"
    ).select("b1")

    temp_dict = temp.reduceRegion(
        reducer=ee.Reducer.mean(), geometry=point, scale=30, maxPixels=1e9
    )

    # Return as Python Float
    temp_value = temp_dict.get("b1")

    # Check it return Python Float
    if hasattr(temp_value, "getInfo"):
        temp_value = temp_value.getInfo()

    return float(temp_value) if temp_value is not None else None


def get_ph(lat: float, lon: float):
    """Returns the soil pH value at a given point, based on a soil pH polygon layer from PO's Dataset."""
    import ee

    # Create point geometry
    point = ee.Geometry.Point([lon, lat])

    # Load soil pH FeatureCollection
    soil_ph_file = ee.FeatureCollection(
        "projects/scenic-block-466510-c5/assets/soil_ph_timor"
    )

    ph_field = "ph"

    # Find the polygon that intersects this point
    feature = soil_ph_file.filterBounds(point).first()

    # If no polygon covers this point, return None
    feature_info = feature.getInfo() if feature is not None else None
    if feature_info is None:
        return None

    # Read the 'ph' attribute from the feature
    ph_val = feature.get(ph_field)

    # Check it return Python Float
    if hasattr(ph_val, "getInfo"):
        ph_val = ph_val.getInfo()

    # Return as a Python float (or None if missing)
    return float(ph_val) if ph_val is not None else None


def get_elevation(lat: float, lon: float):
    """Returns the elevation (m) at a given point, from a DEM provided by the PO."""
    import ee

    # Create point geometry
    point = ee.Geometry.Point([lon, lat])

    # Load DEM
    dem = ee.Image("projects/scenic-block-466510-c5/assets/DEM").select("b1")

    elev_dict = dem.reduceRegion(
        reducer=ee.Reducer.mean(), geometry=point, scale=30, maxPixels=1e9
    )

    elev_value = elev_dict.get("b1")

    if hasattr(elev_value, "getInfo"):
        elev_value = elev_value.getInfo()

    return float(elev_value) if elev_value is not None else None


def get_landcover(lat: float, lon: float):
    """Returns the landcover class for the farm containing the point, including "forest" or "non_forest"."""
    import ee

    # Create point geometry
    point = ee.Geometry.Point([lon, lat])

    # Load landcover FeatureCollection
    landcover_file = ee.FeatureCollection(
        "projects/scenic-block-466510-c5/assets/farm_with_landcover"
    )

    landcover_field = "lc_class"

    # Find first farm polygon that intersects this point
    farm = landcover_file.filterBounds(point).first()

    # If no farm found → return None
    if farm is None:
        return None

    try:
        landcover_value = farm.get(landcover_field).getInfo()
    except Exception:
        return None

    return landcover_value


def get_NDVI(lat: float, lon: float):
    """turns the mean NDVI (Normalised Difference Vegetation Index, -1 to 1) at a point for the year 2025 from Modis Dataset."""
    import ee

    # Create point geometry
    point = ee.Geometry.Point([lon, lat])

    # Load MODIS NDVI collection
    ndvi_ic = (
        ee.ImageCollection("MODIS/061/MOD13Q1")
        .filterDate("2025-01-01", "2025-12-31")
        .select("NDVI")
    )

    # Compute mean NDVI image over the period
    ndvi_img = ndvi_ic.mean()

    ndvi_dict = ndvi_img.reduceRegion(
        reducer=ee.Reducer.mean(), geometry=point, scale=250, maxPixels=1e9
    )

    ndvi_raw = ndvi_dict.get("NDVI").getInfo()

    # Scale to get real NDVI in
    ndvi_mean = ndvi_raw * 1e-4

    return ndvi_mean
