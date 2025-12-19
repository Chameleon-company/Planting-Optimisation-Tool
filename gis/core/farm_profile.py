from typing import Optional, Any, Dict

from core.extract_data import (
    get_rainfall,
    get_temperature,
    get_ph,
    get_area_ha,
    get_elevation,
    get_slope,
    get_texture_id,
    get_centroid_lat_lon,
)


def build_farm_profile(
    geometry, year: Optional[int] = None, farm_id: Optional[int] = None
):
    """Build a farm profile from coordinates (placeholder)."""
    rainfall = get_rainfall(geometry, year=year)
    temperature = get_temperature(geometry, year=year)
    ph = get_ph(geometry, year=year)
    elevation = get_elevation(geometry, year=year)
    slope = get_slope(geometry, year=year)
    area_ha = get_area_ha(geometry)
    texture_id = get_texture_id(geometry)
    lat, lon = get_centroid_lat_lon(geometry)

    if elevation < 100 and 500 <= rainfall <= 3000:
        coastal_flag = True
    else:
        coastal_flag = False

    profile: Dict[str, Any] = {
        "id": farm_id,
        "rainfall_mm": rainfall,
        "temperature_celsius": temperature,
        "elevation_m": elevation,
        "ph": ph,
        "soil_texture_id": texture_id,
        "area_ha": area_ha,
        "latitude": lat,
        "longitude": lon,
        "coastal": coastal_flag,
        "slope": slope,
    }

    return profile
