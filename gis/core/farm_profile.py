from typing import Optional, Any, Dict

from core.extract_data import (
    get_rainfall,
    get_temperature,
    get_ph,
    get_area_ha,
    get_dist_to_coast,
    get_elevation,
    get_slope,
    get_texture,
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
    texture = get_texture(geometry, year=year)
    area_ha = get_area_ha(geometry)
    dist_to_coast = get_dist_to_coast(geometry)

    if dist_to_coast is None:
        coastal_flag = None
    elif dist_to_coast <= 30:
        coastal_flag = True
    else:
        coastal_flag = False

    profile: Dict[str, Any] = {
        "id": farm_id,
        "geometry": geometry,
        "temperature_celsius": temperature,
        "rainfall_mm": rainfall,
        "ph": ph,
        "area_ha": area_ha,
        "soil_textures": texture,
        "elevation_m": elevation,
        "slope": slope,
        "dist_to_coast_km": dist_to_coast,
        "coastal region": coastal_flag,
    }

    return profile
