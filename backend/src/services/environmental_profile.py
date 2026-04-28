from core.farm_profile import build_farm_profile
from geoalchemy2.shape import to_shape
from shapely.geometry import MultiPolygon, Polygon
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.boundaries import FarmBoundary
from src.models.farm import Farm
from src.services.soil_ph import get_soil_ph_for_point
from src.services.soil_texture_spatial import get_soil_texture_for_point


class EnvironmentalProfileService:
    @staticmethod
    async def run_environmental_profile(db: AsyncSession, farm_id: int):
        # Fetch the boundary data
        result = await db.execute(select(FarmBoundary).where(FarmBoundary.id == farm_id))
        boundary_record = result.scalar_one_or_none()

        if not boundary_record:
            return None

        farm_result = await db.execute(select(Farm).where(Farm.id == farm_id))
        farm_record = farm_result.scalar_one_or_none()

        if not farm_record:
            return None

        # Geometry parsing
        shapely_geom = to_shape(boundary_record.boundary)

        target_poly = None

        if isinstance(shapely_geom, MultiPolygon):
            target_poly = list(shapely_geom.geoms)[0]
        elif isinstance(shapely_geom, Polygon):
            target_poly = shapely_geom
        else:
            return None

        # Format for GIS parser
        lat_lon_ring = [(lat, lon) for (lon, lat) in list(target_poly.exterior.coords)]
        formatted_geometry = [lat_lon_ring]

        # Get centroid
        centroid = target_poly.centroid
        lat = centroid.y
        lon = centroid.x

        # Get local soil pH from PostGIS
        local_ph = await get_soil_ph_for_point(db, lat, lon)

        # Get local soil texture from PostGIS
        local_texture = await get_soil_texture_for_point(db, lat, lon)

        # Call GEE + Hybrid logic
        profile = build_farm_profile(geometry=formatted_geometry, farm_id=farm_id, soil_ph=local_ph, soil_texture=local_texture)

        if profile and profile.get("status") != "failed":
            profile["data_source"] = "gee"

        if not profile or profile.get("status") == "failed":
            profile = {
                "id": farm_id,
                "rainfall_mm": farm_record.rainfall_mm,
                "temperature_celsius": farm_record.temperature_celsius,
                "elevation_m": farm_record.elevation_m,
                "soil_ph": local_ph if local_ph is not None else farm_record.ph,
                "soil_texture_id": farm_record.soil_texture_id,
                "soil_texture": local_texture,
                "area_ha": farm_record.area_ha,
                "latitude": farm_record.latitude,
                "longitude": farm_record.longitude,
                "coastal": farm_record.coastal,
                "riparian": farm_record.riparian,
                "nitrogen_fixing": farm_record.nitrogen_fixing,
                "shade_tolerant": farm_record.shade_tolerant,
                "bank_stabilising": farm_record.bank_stabilising,
                "slope_degrees": farm_record.slope,
                "status": "success",
                "data_source": "fallback",
            }

        # Data Normalization to enforce pydantic schema

        # Round temp to int
        if profile.get("temperature_celsius") is not None:
            profile["temperature_celsius"] = int(round(float(profile["temperature_celsius"])))

        # Round rainfall to int
        if profile.get("rainfall_mm") is not None:
            profile["rainfall_mm"] = int(round(float(profile["rainfall_mm"])))

        # Round pH to 1 decimal place
        if profile.get("soil_ph") is not None:
            profile["soil_ph"] = round(float(profile["soil_ph"]), 1)

        # Round slope to 2 decimal places
        if profile.get("slope_degrees") is not None:
            profile["slope_degrees"] = round(float(profile["slope_degrees"]), 2)

        return profile
