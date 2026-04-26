from core.farm_profile import build_farm_profile
from geoalchemy2.shape import to_shape
from imputation import TARGET_FEATURES, impute_missing
from shapely.geometry import MultiPolygon, Polygon
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.boundaries import FarmBoundary
from src.models.farm import Farm

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

        # Fetch Farm record early so riparian can be passed into build_farm_profile
        farm_result = await db.execute(select(Farm).where(Farm.id == farm_id))
        farm_record = farm_result.scalar_one_or_none()
        riparian = farm_record.riparian if farm_record is not None else None

        # Call the external GEE logic
        # Passing the boundary and farm_id
        profile = build_farm_profile(geometry=formatted_geometry, farm_id=farm_id, riparian=riparian)

        if not profile:
            return None

        # --- Imputation ---------------------------------------------------
        # Skip imputation if GEE failed — error profiles lack base features
        # (latitude, longitude, area_ha, coastal, riparian) entirely.
        if profile.get("status") == "failed":
            return profile
        # Null out values that the schema validators would reject as out of range,
        # so they are treated as missing and picked up by the imputer rather than
        # silently becoming None only after Pydantic validation.
        rainfall = profile.get("rainfall_mm")
        if rainfall is not None and not (1000 <= rainfall <= 3000):
            profile["rainfall_mm"] = None

        temp = profile.get("temperature_celsius")
        if temp is not None and not (15 <= temp <= 30):
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
