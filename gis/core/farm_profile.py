"""
Farm Profile Module - Complete implementation for individual and bulk operations.

Functions:
    - build_farm_profile: Create a single farm profile
    - update_farm_profile: Update specific fields in a farm profile
    - bulk_create_profiles: Create profiles for multiple farms in parallel
    - bulk_update_profiles: Update profiles for multiple farms in parallel
"""

from typing import Optional, List, Dict, Any, Callable
from datetime import datetime
import pandas as pd
from concurrent.futures import ThreadPoolExecutor, as_completed
import time

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


# ============================================================================
# INDIVIDUAL FARM OPERATIONS
# ============================================================================


def build_farm_profile(
    geometry,
    year: Optional[int] = None,
    farm_id: Optional[int] = None,
    **additional_fields,
) -> Dict[str, Any]:
    """
    Build a complete farm profile from geometry.

    Args:
        geometry: Farm geometry (point, polygon, or coordinates)
        year: Year for temporal data extraction (default: 2024)
        farm_id: Unique farm identifier
        **additional_fields: Any additional custom fields (e.g., farmer_name)

    Returns:
        Dictionary with complete farm profile

    Example:
        profile = build_farm_profile(
            geometry=(-8.569, 126.676),
            farm_id=1,
            year=2024,
            farmer_name="John Doe"
        )
    """
    year = year or 2024

    try:
        # Extract environmental data
        rainfall = get_rainfall(geometry, year=year)
        temperature = get_temperature(geometry, year=year)
        ph = get_ph(geometry, year=year)
        elevation = get_elevation(geometry, year=year)
        slope = get_slope(geometry, year=year)
        area_ha = get_area_ha(geometry)
        texture_id = get_texture_id(geometry)
        lat, lon = get_centroid_lat_lon(geometry)

        # Calculate coastal flag
        if elevation is not None and rainfall is not None:
            coastal_flag = elevation < 100 and 500 <= rainfall <= 3000
        else:
            coastal_flag = False

        # Build profile
        profile: Dict[str, Any] = {
            "id": farm_id,
            "year": year,
            "rainfall_mm": rainfall,
            "temperature_celsius": temperature,
            "elevation_m": elevation,
            "slope_degrees": slope,
            "soil_ph": ph,
            "soil_texture_id": texture_id,
            "area_ha": area_ha,
            "latitude": lat,
            "longitude": lon,
            "coastal": coastal_flag,
            "updated_at": datetime.now().isoformat(),
            "status": "success",
        }

        # Add custom fields
        profile.update(additional_fields)

        return profile

    except Exception as e:
        return {
            "id": farm_id,
            "year": year,
            "status": "failed",
            "error": str(e),
            "updated_at": datetime.now().isoformat(),
        }


def update_farm_profile(
    existing_profile: Dict[str, Any],
    geometry,
    fields: Optional[List[str]] = None,
    year: Optional[int] = None,
) -> Dict[str, Any]:
    """
    Update specific fields in an existing farm profile.

    Args:
        existing_profile: Current profile dictionary
        geometry: Farm geometry
        fields: List of fields to update (None = update all fields)
        year: Year for temporal data

    Returns:
        Updated profile dictionary

    Example:
        updated = update_farm_profile(
            existing_profile=old_profile,
            geometry=farm_geometry,
            fields=["rainfall_mm", "temperature_celsius"],
            year=2025
        )
    """
    year = year or existing_profile.get("year", 2024)
    farm_id = existing_profile.get("id")

    # If no fields specified, update all
    if fields is None:
        return build_farm_profile(geometry, year, farm_id)

    # Field extraction functions
    field_extractors = {
        "rainfall_mm": lambda: get_rainfall(geometry, year=year),
        "temperature_celsius": lambda: get_temperature(geometry, year=year),
        "soil_ph": lambda: get_ph(geometry, year=year),
        "elevation_m": lambda: get_elevation(geometry, year=year),
        "slope_degrees": lambda: get_slope(geometry, year=year),
        "area_ha": lambda: get_area_ha(geometry),
        "soil_texture_id": lambda: get_texture_id(geometry),
    }

    updated_profile = existing_profile.copy()

    try:
        for field in fields:
            if field in field_extractors:
                updated_profile[field] = field_extractors[field]()
            elif field == "coastal":
                updated_profile["coastal"] = (
                    updated_profile.get("elevation_m", 1000) < 100
                    and 500 <= updated_profile.get("rainfall_mm", 0) <= 3000
                )
            elif field in ["latitude", "longitude"]:
                lat, lon = get_centroid_lat_lon(geometry)
                updated_profile["latitude"] = lat
                updated_profile["longitude"] = lon

        updated_profile["updated_at"] = datetime.now().isoformat()
        updated_profile["year"] = year
        updated_profile["status"] = "success"

        return updated_profile

    except Exception as e:
        updated_profile["status"] = "partial_update"
        updated_profile["error"] = str(e)
        return updated_profile


# ============================================================================
# BULK OPERATIONS
# ============================================================================


def bulk_create_profiles(
    farms: List[Dict[str, Any]],
    geometry_field: str = "geometry",
    id_field: str = "farm_id",
    year: Optional[int] = None,
    max_workers: int = 5,
    progress_callback: Optional[Callable[[int, int], None]] = None,
) -> pd.DataFrame:
    """
    Create profiles for multiple farms in parallel.

    Args:
        farms: List of farm dictionaries containing geometry and ID
        geometry_field: Field name containing geometry (default: "geometry")
        id_field: Field name containing farm ID (default: "farm_id")
        year: Year for data extraction (default: 2024)
        max_workers: Maximum parallel workers (default: 5)
        progress_callback: Optional callback function(current, total)

    Returns:
        DataFrame with all farm profiles

    Example:
        farms = [
            {"farm_id": 1, "geometry": (-8.55, 125.57)},
            {"farm_id": 2, "geometry": (-8.56, 125.58)},
        ]
        profiles_df = bulk_create_profiles(farms, year=2024)
        profiles_df.to_csv("profiles_2024.csv", index=False)
    """
    year = year or 2024
    profiles = []
    total = len(farms)

    print(f"\nStarting bulk profile creation for {total} farms...")
    start_time = time.time()

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Submit all tasks
        future_to_farm = {
            executor.submit(
                build_farm_profile,
                farm[geometry_field],
                year,
                farm.get(id_field),
                **{
                    k: v for k, v in farm.items() if k not in [geometry_field, id_field]
                },
            ): farm
            for farm in farms
        }

        # Collect results
        completed = 0
        for future in as_completed(future_to_farm):
            profile = future.result()
            profiles.append(profile)
            completed += 1

            if progress_callback:
                progress_callback(completed, total)

            # Print progress every 10%
            if completed % max(1, total // 10) == 0:
                elapsed = time.time() - start_time
                rate = completed / elapsed
                remaining = (total - completed) / rate if rate > 0 else 0
                print(
                    f"  Progress: {completed}/{total} ({completed / total * 100:.1f}%) "
                    f"- {rate:.1f} farms/sec - ETA: {remaining:.0f}s"
                )

    elapsed = time.time() - start_time
    success_count = sum(1 for p in profiles if p.get("status") == "success")

    print("\nBulk creation complete!")
    print(f"  Total time: {elapsed:.1f}s")
    print(f"  Rate: {total / elapsed:.1f} farms/sec")
    print(f"  Success: {success_count}/{total} ({success_count / total * 100:.1f}%)")
    print(f"  Failed: {total - success_count}")

    return pd.DataFrame(profiles)


def bulk_update_profiles(
    profiles_df: pd.DataFrame,
    geometries: Dict[int, Any],
    fields: Optional[List[str]] = None,
    year: Optional[int] = None,
    max_workers: int = 5,
    progress_callback: Optional[Callable[[int, int], None]] = None,
) -> pd.DataFrame:
    """
    Update specific fields for multiple farms in parallel.

    Args:
        profiles_df: DataFrame with existing profiles
        geometries: Dictionary mapping farm_id to geometry
        fields: List of fields to update (None = all fields)
        year: Year for data extraction (default: 2024)
        max_workers: Maximum parallel workers (default: 5)
        progress_callback: Optional callback function(current, total)

    Returns:
        DataFrame with updated profiles

    Example:
        geometries = {1: geom1, 2: geom2, 3: geom3}
        updated_df = bulk_update_profiles(
            profiles_df=old_profiles,
            geometries=geometries,
            fields=["rainfall_mm", "temperature_celsius"],
            year=2025
        )
        updated_df.to_csv("profiles_2025.csv", index=False)
    """
    year = year or 2024
    updated_profiles = []
    total = len(profiles_df)

    print(f"\nStarting bulk profile update for {total} farms...")
    print(f"  Fields to update: {fields or 'ALL'}")
    start_time = time.time()

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Submit all tasks
        future_to_id = {}
        for _, profile in profiles_df.iterrows():
            farm_id = profile.get("id")
            if farm_id in geometries:
                future = executor.submit(
                    update_farm_profile,
                    profile.to_dict(),
                    geometries[farm_id],
                    fields,
                    year,
                )
                future_to_id[future] = farm_id

        # Collect results
        completed = 0
        for future in as_completed(future_to_id):
            profile = future.result()
            updated_profiles.append(profile)
            completed += 1

            if progress_callback:
                progress_callback(completed, total)

            if completed % max(1, total // 10) == 0:
                elapsed = time.time() - start_time
                rate = completed / elapsed
                remaining = (total - completed) / rate if rate > 0 else 0
                print(
                    f"  Progress: {completed}/{total} ({completed / total * 100:.1f}%) "
                    f"- {rate:.1f} farms/sec - ETA: {remaining:.0f}s"
                )

    elapsed = time.time() - start_time
    success_count = sum(1 for p in updated_profiles if p.get("status") == "success")

    print("\nBulk update complete!")
    print(f"  Total time: {elapsed:.1f}s")
    print(
        f"  Success: {success_count}/{len(updated_profiles)} "
        f"({success_count / len(updated_profiles) * 100:.1f}%)"
    )

    return pd.DataFrame(updated_profiles)
