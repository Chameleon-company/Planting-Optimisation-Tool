from core.farm_profile import build_farm_profile
from geoalchemy2.shape import to_shape
from imputation import TARGET_FEATURES, impute_missing
from shapely.geometry import MultiPolygon, Polygon
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.boundaries import FarmBoundary
from src.models.farm import Farm
from src.models.soil_texture import SoilTexture
from src.schemas.constants import (
    RAINFALL_MAX,
    RAINFALL_MIN,
    SOIL_PH_MAX,
    SOIL_PH_MIN,
    TEMPERATURE_MAX,
    TEMPERATURE_MIN,
)
from src.services.soil_ph import get_soil_ph_for_point
from src.services.soil_texture_spatial import get_soil_texture_for_point

# Maps from farm_profile.py output keys to imputation service keys
_TO_IMPUTER = {"slope_degrees": "slope", "soil_ph": "ph"}
_FROM_IMPUTER = {v: k for k, v in _TO_IMPUTER.items()}


class ImputationError(Exception):
    """Raised when imputation fails or produces implausible values."""


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

        # Get centroid for local raster queries
        centroid = target_poly.centroid
        lat, lon = centroid.y, centroid.x

        riparian = farm_record.riparian if farm_record is not None else None

        # Get local soil pH from PostGIS
        local_ph = await get_soil_ph_for_point(db, lat, lon)

        # Validate local pH (dataset range: 5–8.5)
        if local_ph is not None and not (SOIL_PH_MIN <= local_ph <= SOIL_PH_MAX):
            local_ph = None

        # Get local soil texture from PostGIS
        local_texture = await get_soil_texture_for_point(db, lat, lon)

        # If local raster not available, fetch from DB
        if local_texture is None and farm_record.soil_texture_id is not None:
            result = await db.execute(select(SoilTexture).where(SoilTexture.id == farm_record.soil_texture_id))
            texture = result.scalar_one_or_none()

            if texture:
                local_texture = texture.name

        # Call GEE + Hybrid logic
        profile = build_farm_profile(
            geometry=formatted_geometry,
            farm_id=farm_id,
            riparian=riparian,
            soil_ph=local_ph,
            soil_texture=local_texture,
        )

        if profile and profile.get("status") != "failed":
            profile["data_source"] = "hybrid"

        if profile is None:
            return None

        if profile.get("status") == "failed":
            profile = {
                "id": farm_id,
                "rainfall_mm": farm_record.rainfall_mm,
                "temperature_celsius": farm_record.temperature_celsius,
                "elevation_m": farm_record.elevation_m,
                "soil_ph": (local_ph if local_ph is not None else (farm_record.ph if farm_record.ph is not None and 5 <= farm_record.ph <= 8.5 else None)),
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

        # --- Imputation ---------------------------------------------------
        # Skip imputation if GEE failed — error profiles lack base features
        # (latitude, longitude, area_ha, coastal, riparian) entirely.
        if profile.get("status") == "failed":
            return profile
        # Null out values that the schema validators would reject as out of range,
        # so they are treated as missing and picked up by the imputer rather than
        # silently becoming None only after Pydantic validation.
        rainfall = profile.get("rainfall_mm")
        if rainfall is not None and not (RAINFALL_MIN <= rainfall <= RAINFALL_MAX):
            profile["rainfall_mm"] = None

        temp = profile.get("temperature_celsius")
        if temp is not None and not (TEMPERATURE_MIN <= temp <= TEMPERATURE_MAX):
            profile["temperature_celsius"] = None

        # TARGET_FEATURES uses imputer naming (slope, ph).
        # farm_profile uses slope_degrees and soil_ph — remap before passing.
        imputer_profile = {_TO_IMPUTER.get(k, k): v for k, v in profile.items()}

        missing_targets = [f for f in TARGET_FEATURES if imputer_profile.get(f) is None]

        if missing_targets:
            try:
                filled, imputed_fields = impute_missing(imputer_profile)
            except RuntimeError as exc:
                raise ImputationError(f"Imputation model unavailable: {exc}") from exc

            # Merge filled values back, remapping imputer keys to profile keys
            for field in imputed_fields:
                profile_key = _FROM_IMPUTER.get(field, field)
                profile[profile_key] = filled[field]

            # Record which fields were imputed (using DB column naming)
            for field in imputed_fields:
                profile[f"{field}_imputed"] = True

            # Persist imputation flags to the Farm DB record
            if farm_record is not None:
                for field in imputed_fields:
                    setattr(farm_record, f"{field}_imputed", True)
                await db.commit()
        # ------------------------------------------------------------------

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
