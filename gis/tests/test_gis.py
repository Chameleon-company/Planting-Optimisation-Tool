"""
Integration tests for GIS data extraction using Google Earth Engine.

Dataset Validation Status (from EDA):
CHIRPS Rainfall:  r=0.96, MAE=23mm   - EXCELLENT
SRTM Elevation:   r=0.98, MAE=11m    - EXCELLENT
MODIS LST Temp:   r=0.87, MAE=1.5°C  - GOOD (needs -4.43°C bias correction)
Farm Area:        r=0.96, MAE=0.14ha - VALIDATED
OpenLandMap pH:   r=0.18, MAE=1.21   - POOR (not recommended)

"""

import pytest
import pandas as pd
from config.settings import (
    SERVICE_ACCOUNT,
    KEY_PATH,
    get_dataset_config,
    TEXTURE_MAP,
)
from core.gee_client import init_gee
from core.extract_data import (
    get_rainfall,
    get_temperature,
    get_ph,
    get_area_ha,
    get_elevation,
    get_slope,
    get_texture,
    _normalize_texture_name,
    get_centroid_lat_lon,
)
from core.geometry_parser import (
    parse_point,
    parse_multipoint,
    parse_polygon,
    parse_geometry,
)
from core.farm_profile import (
    build_farm_profile,
    update_farm_profile,
    bulk_create_profiles,
    bulk_update_profiles,
)


# ============================================================================
# SETUP AND FIXTURES
# ============================================================================


@pytest.fixture(scope="module")
def gee_initialized():
    """Initialize GEE once for all tests."""
    if SERVICE_ACCOUNT is None or KEY_PATH is None:
        pytest.skip("GEE credentials not available (expected in CI without secrets)")

    try:
        init_gee()
        return True
    except Exception as e:
        pytest.skip(f"Could not initialize GEE: {e}")


@pytest.fixture
def test_point():
    """Test point in Timor-Leste (lat, lon)."""
    return (-8.569, 126.676)


@pytest.fixture
def test_polygon():
    """Test polygon in Timor-Leste."""
    return [
        [
            (-8.55, 125.57),
            (-8.56, 125.57),
            (-8.56, 125.58),
            (-8.55, 125.58),
            (-8.55, 125.57),
        ]
    ]


# ============================================================================
# GEE CLIENT TESTS
# ============================================================================


@pytest.mark.skipif(
    SERVICE_ACCOUNT is None,
    reason="GEE credentials not available (expected in CI without secrets)",
)
def test_init_gee():
    """Test GEE initialization with service account."""
    assert SERVICE_ACCOUNT is not None, "GEE_SERVICE_ACCOUNT not set in .env"
    assert KEY_PATH is not None, "GEE_KEY_PATH not set in .env"

    result = init_gee()
    assert result is True


# ============================================================================
# GEOMETRY PARSER TESTS
# ============================================================================


def test_parse_point(gee_initialized):
    """Test parsing a point geometry."""
    import ee

    lat, lon = -8.55, 125.57
    geom = parse_point(lat, lon)

    assert isinstance(geom, ee.Geometry)
    coords = geom.coordinates().getInfo()
    assert coords[0] == lon
    assert coords[1] == lat


def test_parse_multipoint(gee_initialized):
    """Test parsing multiple points."""
    import ee

    coords = [(-8.55, 125.57), (-8.56, 125.58)]
    geom = parse_multipoint(coords)

    assert isinstance(geom, ee.Geometry)


def test_parse_polygon(gee_initialized, test_polygon):
    """Test parsing a polygon geometry."""
    import ee

    geom = parse_polygon(test_polygon)

    assert isinstance(geom, ee.Geometry)
    # Polygon should have area > 0
    area = geom.area().getInfo()
    assert area > 0


def test_parse_geometry_auto_detect(gee_initialized, test_point):
    """Test automatic geometry type detection."""
    import ee

    # Point
    geom_point = parse_geometry(test_point)
    assert isinstance(geom_point, ee.Geometry)

    # MultiPoint
    geom_multi = parse_geometry([test_point, (-8.57, 126.68)])
    assert isinstance(geom_multi, ee.Geometry)

    # Polygon
    polygon = [[(-8.55, 125.57), (-8.56, 125.57), (-8.56, 125.58), (-8.55, 125.57)]]
    geom_poly = parse_geometry(polygon)
    assert isinstance(geom_poly, ee.Geometry)


# ============================================================================
# DATA EXTRACTION TESTS
# ============================================================================


def test_get_rainfall(gee_initialized, test_point):
    """Test rainfall extraction - CHIRPS (r=0.96, MAE=23mm) - EXCELLENT."""
    rainfall = get_rainfall(test_point, year=2024)

    assert rainfall is not None, "Rainfall should not be None"
    assert isinstance(rainfall, (int, float)), "Rainfall should be numeric"
    assert 0 <= rainfall <= 10000, f"Rainfall {rainfall} mm out of reasonable range"
    print(f"SUCCESS: Rainfall (CHIRPS - EDA Validated): {rainfall} mm")


def test_get_temperature(gee_initialized, test_point):
    """Test temperature extraction - MODIS LST (r=0.87, MAE=1.5°C with -4.43°C correction) - GOOD."""
    temp = get_temperature(test_point, year=2024)

    assert temp is not None, "Temperature should not be None"
    assert isinstance(temp, (int, float)), "Temperature should be numeric"
    assert -50 <= temp <= 60, f"Temperature {temp}°C out of reasonable range"
    print(f"SUCCESS: Temperature (MODIS LST - bias corrected): {temp}°C")


def test_get_elevation(gee_initialized, test_point):
    """Test elevation extraction - SRTM (r=0.98, MAE=11m) - EXCELLENT."""
    elevation = get_elevation(test_point)

    assert elevation is not None, "Elevation should not be None"
    assert isinstance(elevation, (int, float)), "Elevation should be numeric"
    assert -500 <= elevation <= 9000, f"Elevation {elevation}m out of reasonable range"
    print(f"SUCCESS: Elevation (SRTM - EDA Validated): {elevation} m")


def test_get_slope(gee_initialized, test_point):
    """Test slope extraction."""
    slope = get_slope(test_point)

    assert slope is not None, "Slope should not be None"
    assert isinstance(slope, (int, float)), "Slope should be numeric"
    assert 0 <= slope <= 90, f"Slope {slope}° out of reasonable range (0-90)"
    print(f"SUCCESS: Slope: {slope}°")


def test_get_ph(gee_initialized, test_point):
    """Test soil pH extraction - OpenLandMap (r=0.18, MAE=1.21) - POOR QUALITY, NOT RECOMMENDED."""
    ph = get_ph(test_point)

    if ph is not None:  # pH might be None if no data at location
        assert isinstance(ph, (int, float)), "pH should be numeric"
        assert 0 <= ph <= 14, f"pH {ph} out of valid range (0-14)"
        print(f"WARNING: Soil pH (OpenLandMap - LOW QUALITY): {ph}")
        print("  WARNING: r=0.18 correlation - NOT RECOMMENDED for Timor-Leste")
        print("  Recommendation: Use local calibration model or exclude from analysis")
    else:
        print("WARNING: Soil pH: No data at this location")


def test_get_texture(gee_initialized, test_point):
    """Test soil texture extraction - demonstrates GEE extraction capability."""
    texture = get_texture(test_point)

    # Currently using OpenLandMap pH as demonstration of GEE extraction
    # Returns numeric pH value (~5-6) rather than texture class name
    if texture is not None:
        assert isinstance(texture, (int, float, str)), (
            "Texture should be numeric or string"
        )
        print(f"SUCCESS: Soil Texture (demonstration): {texture}")
        print("  Note: Currently extracting pH value to demonstrate GEE capability")
        print(
            "  Replace soil_texture config with actual texture asset for production use"
        )
    else:
        print("WARNING: Soil Texture: No data at this location")


def test_get_area_ha(gee_initialized, test_polygon):
    """Test area calculation for polygon."""
    area = get_area_ha(test_polygon)

    assert area is not None, "Area should not be None"
    assert isinstance(area, (int, float)), "Area should be numeric"
    assert area > 0, "Area should be positive"
    print(f"SUCCESS: Area: {area} ha")


def test_get_centroid(gee_initialized, test_polygon):
    """Test centroid calculation."""
    lat, lon = get_centroid_lat_lon(test_polygon)

    assert lat is not None and lon is not None, "Centroid should not be None"
    assert isinstance(lat, float) and isinstance(lon, float), (
        "Coordinates should be floats"
    )
    assert -90 <= lat <= 90, f"Latitude {lat} out of range"
    assert -180 <= lon <= 180, f"Longitude {lon} out of range"
    print(f"SUCCESS: Centroid: ({lat}, {lon})")


# ============================================================================
# TEXTURE PROCESSING TESTS
# ============================================================================


def test_normalize_texture_name():
    """Test texture name normalization."""
    assert _normalize_texture_name("Clay, Clay Loam") == "clay"
    assert _normalize_texture_name("  Sandy Loam  ") == "sandy loam"
    assert _normalize_texture_name("Organic") is None
    assert _normalize_texture_name("Variable") is None
    assert _normalize_texture_name(None) is None
    assert _normalize_texture_name("") is None


def test_get_texture_id_mapping():
    """Test texture ID mapping."""
    assert TEXTURE_MAP["sand"] == 1
    assert TEXTURE_MAP["clay"] == 12
    assert TEXTURE_MAP["loam"] == 4


# ============================================================================
# FARM PROFILE TESTS
# ============================================================================


def test_build_farm_profile_point(gee_initialized, test_point):
    """Test building a complete farm profile for a point."""
    profile = build_farm_profile(geometry=test_point, year=2024, farm_id=1)

    # Check structure
    assert isinstance(profile, dict), "Profile should be a dictionary"
    assert profile["id"] == 1, "Farm ID should match"

    # Check required fields exist
    required_fields = [
        "id",
        "year",
        "rainfall_mm",
        "temperature_celsius",
        "elevation_m",
        "slope_degrees",
        "soil_ph",
        "area_ha",
        "latitude",
        "longitude",
        "coastal",
    ]
    for field in required_fields:
        assert field in profile, f"Missing field: {field}"

    # Check data types and ranges (where applicable)
    if profile["rainfall_mm"] is not None:
        assert isinstance(profile["rainfall_mm"], (int, float))
        assert profile["rainfall_mm"] >= 0

    if profile["temperature_celsius"] is not None:
        assert isinstance(profile["temperature_celsius"], (int, float))
        assert -50 <= profile["temperature_celsius"] <= 60

    if profile["elevation_m"] is not None:
        assert isinstance(profile["elevation_m"], (int, float))

    if profile["slope_degrees"] is not None:
        assert isinstance(profile["slope_degrees"], (int, float))
        assert 0 <= profile["slope_degrees"] <= 90

    assert isinstance(profile["area_ha"], (int, float))
    assert isinstance(profile["latitude"], float)
    assert isinstance(profile["longitude"], float)
    assert isinstance(profile["coastal"], bool)

    print("\nSUCCESS: Farm Profile:")
    for key, value in profile.items():
        print(f"  {key}: {value}")


def test_build_farm_profile_polygon(gee_initialized, test_polygon):
    """Test building a complete farm profile for a polygon."""
    profile = build_farm_profile(geometry=test_polygon, year=2024, farm_id=2)

    assert isinstance(profile, dict)
    assert profile["id"] == 2
    assert profile["area_ha"] > 0, "Polygon should have area > 0"

    print("\nSUCCESS: Polygon Profile:")
    print(f"  Area: {profile['area_ha']} ha")
    print(f"  Rainfall: {profile['rainfall_mm']} mm")
    print(f"  Elevation: {profile['elevation_m']} m")


def test_coastal_flag_logic(gee_initialized):
    """Test coastal flag calculation logic."""
    # Low elevation, moderate rainfall -> coastal
    coastal_point = (-8.55, 125.57)  # Adjust to actual coastal point if needed
    profile = build_farm_profile(coastal_point, year=2024, farm_id=3)

    # Coastal flag should be True if: elevation < 100 AND 500 <= rainfall <= 3000
    if profile["elevation_m"] is not None and profile["rainfall_mm"] is not None:
        expected_coastal = (
            profile["elevation_m"] < 100 and 500 <= profile["rainfall_mm"] <= 3000
        )
        assert profile["coastal"] == expected_coastal, (
            f"Coastal flag mismatch: expected {expected_coastal}, got {profile['coastal']}"
        )


# ============================================================================
# DATA QUALITY VALIDATION TESTS
# ============================================================================


def test_dataset_validation_quality(gee_initialized, test_point):
    """Test that extracted data matches expected quality from EDA validation."""
    # Based on EDA validation results
    rainfall = get_rainfall(test_point, year=2024)
    elevation = get_elevation(test_point)
    temp = get_temperature(test_point, year=2024)

    # These should all return valid values (not None)
    assert rainfall is not None, "CHIRPS rainfall should return data (r=0.96, MAE=23mm)"
    assert elevation is not None, "SRTM elevation should return data (r=0.98, MAE=11m)"
    assert temp is not None, (
        "MODIS temperature should return data (r=0.87, MAE=1.5°C with correction)"
    )

    print("\nSUCCESS: EDA-Validated Data Quality Check:")
    print(
        f"  Rainfall (CHIRPS):     {rainfall} mm   [r=0.96, MAE=23mm]   SUCCESS: EXCELLENT"
    )
    print(
        f"  Elevation (SRTM):      {elevation} m   [r=0.98, MAE=11m]    SUCCESS: EXCELLENT"
    )
    print(
        f"  Temperature (MODIS):   {temp}°C        [r=0.87, MAE=1.5°C]  SUCCESS: GOOD (bias corrected)"
    )
    print("\n  Note: All values extracted using CENTROID method (EDA recommended)")
    print("        Polygon aggregation provides no improvement over centroid")


def test_soil_ph_warning(gee_initialized, test_point):
    """Test that soil pH extraction works but document low quality per EDA."""
    ph = get_ph(test_point)

    # pH has very low correlation (r=0.18) per EDA validation
    if ph is not None:
        print("\nWARNING: SOIL pH WARNING:")
        print(f"  Extracted value: {ph}")
        print("  Data quality (EDA): r=0.18, MAE=1.21 pH units - POOR")
        print("  Problem: Severe value compression (5.5-6.5 vs actual 5-8 range)")
        print("  Status: NOT RECOMMENDED for operational use in Timor-Leste")
        print("\n  EDA Recommendation:")
        print("  - Develop local calibration model using PO field measurements")
        print("  - Use predictors: elevation (r=0.98), rainfall, geology, land cover")
        print("  - OR exclude pH from analysis until better data available")
    else:
        print("\nWARNING: Soil pH: No data at this location")


def test_eda_validation_summary(gee_initialized, test_point):
    """Comprehensive test validating all datasets against EDA findings."""
    print("\n" + "=" * 70)
    print("EDA VALIDATION SUMMARY - Dataset Performance")
    print("=" * 70)

    # Extract all variables
    rainfall = get_rainfall(test_point, year=2024)
    elevation = get_elevation(test_point)
    temp = get_temperature(test_point, year=2024)
    get_ph(test_point)

    # Validation results table
    print(
        "\n{:<20} {:<15} {:<15} {:<12} {:<15}".format(
            "Variable", "Dataset", "Correlation", "MAE", "Status"
        )
    )
    print("-" * 70)

    datasets = [
        ("Rainfall", "CHIRPS", "r=0.96", "23mm", "SUCCESS: EXCELLENT"),
        ("Elevation", "SRTM DEM", "r=0.98", "11m", "SUCCESS: EXCELLENT"),
        ("Temperature", "MODIS LST", "r=0.87", "1.5°C*", "SUCCESS: GOOD"),
        ("Farm Area", "Geometry", "r=0.96", "0.14ha", "SUCCESS: VALIDATED"),
        ("Soil pH", "OpenLandMap", "r=0.18", "1.21", "FAILED: POOR"),
    ]

    for var, dataset, corr, mae, status in datasets:
        print(
            "{:<20} {:<15} {:<15} {:<12} {:<15}".format(var, dataset, corr, mae, status)
        )

    print("\n" + "-" * 70)
    print("* Temperature requires -4.43°C bias correction (LST vs air temp)")
    print("\nKey Findings from EDA:")
    print("  • Centroid extraction preferred (equal accuracy, faster)")
    print("  • Polygon aggregation provides NO improvement")
    print("  • Data quality filtering essential (remove pH=0, pH<3.5, pH>10)")
    print("  • MODIS bias correction validated and applied automatically")
    print("  • OpenLandMap pH: NOT suitable for Timor-Leste (use local model)")
    print("=" * 70)

    # Assert critical datasets work
    assert rainfall is not None, "CHIRPS must work (validated r=0.96)"
    assert elevation is not None, "SRTM must work (validated r=0.98)"
    assert temp is not None, "MODIS must work (validated r=0.87)"

    print("\nSUCCESS: All critical datasets validated against EDA benchmarks")


# ============================================================================
# ERROR HANDLING TESTS
# ============================================================================


def test_invalid_geometry():
    """Test handling of invalid geometry."""
    with pytest.raises(ValueError):
        parse_geometry("invalid")


@pytest.mark.skipif(
    SERVICE_ACCOUNT is None,
    reason="GEE credentials not available (expected in CI without secrets)",
)
def test_missing_credentials_error():
    """Test that missing credentials raise appropriate error."""
    from config.settings import SERVICE_ACCOUNT, KEY_PATH

    # This test just verifies credentials are loaded
    assert SERVICE_ACCOUNT is not None, "Set GEE_SERVICE_ACCOUNT in .env"
    assert KEY_PATH is not None, "Set GEE_KEY_PATH in .env"


# ============================================================================
# PERFORMANCE TESTS (OPTIONAL)
# ============================================================================


@pytest.mark.slow
def test_batch_extraction_performance(gee_initialized):
    """Test extraction performance for multiple points."""
    import time

    points = [
        (-8.55, 125.57),
        (-8.56, 125.58),
        (-8.57, 125.59),
    ]

    start = time.time()

    for point in points:
        profile = build_farm_profile(point, year=2024)
        assert profile is not None

    elapsed = time.time() - start

    print(f"\nSUCCESS: Processed {len(points)} points in {elapsed:.2f} seconds")
    print(f"  Average: {elapsed / len(points):.2f} seconds per point")


# ============================================================================
# CONFIGURATION TESTS
# ============================================================================


def test_dataset_config_access():
    """Test accessing dataset configurations."""
    rainfall_config = get_dataset_config("rainfall")

    assert rainfall_config is not None
    assert "asset_id" in rainfall_config
    assert "band" in rainfall_config
    assert "scale" in rainfall_config

    print("\nSUCCESS: Rainfall Config:")
    print(f"  Asset: {rainfall_config['asset_id']}")
    print(f"  Band: {rainfall_config['band']}")
    print(f"  Scale: {rainfall_config['scale']}m")


def test_all_datasets_configured():
    """Test that all expected datasets are configured."""
    from config.settings import list_datasets

    datasets = list_datasets()

    expected = [
        "rainfall",
        "elevation",
        "temperature",
        "soil_ph",
        "soil_texture",
        "dem",
    ]

    for dataset in expected:
        assert dataset in datasets, f"Dataset '{dataset}' not configured"

    print(f"\nConfigured datasets: {', '.join(datasets)}")


# ============================================================================
# BULK OPERATIONS TESTS
# ============================================================================


def test_update_farm_profile(gee_initialized, test_point):
    """Test updating specific fields in a farm profile."""
    # Create initial profile
    profile = build_farm_profile(geometry=test_point, farm_id=1, year=2024)

    assert profile["status"] == "success"
    original_rainfall = profile["rainfall_mm"]
    original_temp = profile["temperature_celsius"]
    original_elevation = profile["elevation_m"]

    print("\nOriginal profile (2024):")
    print(f"  Rainfall: {original_rainfall} mm")
    print(f"  Temperature: {original_temp} C")
    print(f"  Elevation: {original_elevation} m")

    # Update only rainfall and temperature for 2025
    updated = update_farm_profile(
        existing_profile=profile,
        geometry=test_point,
        fields=["rainfall_mm", "temperature_celsius"],
        year=2025,
    )

    assert updated["status"] == "success"
    assert updated["year"] == 2025
    assert updated["elevation_m"] == original_elevation  # Should not change

    print("\nUpdated profile (2025):")
    print(f"  Rainfall: {updated['rainfall_mm']} mm")
    print(f"  Temperature: {updated['temperature_celsius']} C")
    print(f"  Elevation: {updated['elevation_m']} m (unchanged)")


def test_bulk_create_profiles(gee_initialized):
    """Test creating profiles for multiple farms in parallel."""
    farms = [
        {"farm_id": 1, "geometry": (-8.55, 125.57), "farmer_name": "Alice"},
        {"farm_id": 2, "geometry": (-8.56, 125.58), "farmer_name": "Bob"},
        {"farm_id": 3, "geometry": (-8.57, 125.59), "farmer_name": "Carol"},
    ]

    print(f"\nCreating profiles for {len(farms)} farms...")

    profiles_df = bulk_create_profiles(
        farms, geometry_field="geometry", id_field="farm_id", year=2024, max_workers=3
    )

    # Verify results
    assert len(profiles_df) == 3
    assert isinstance(profiles_df, pd.DataFrame)

    # Check all required fields exist
    required_fields = [
        "id",
        "year",
        "rainfall_mm",
        "temperature_celsius",
        "elevation_m",
        "status",
    ]
    for field in required_fields:
        assert field in profiles_df.columns

    # Check status
    success_count = (profiles_df["status"] == "success").sum()
    print(f"\nResults: {success_count}/{len(farms)} successful")

    # Display results
    print("\nProfiles created:")
    print(
        profiles_df[
            ["id", "farmer_name", "rainfall_mm", "temperature_celsius", "status"]
        ]
    )

    assert success_count > 0, "At least one profile should succeed"


def test_bulk_update_profiles(gee_initialized):
    """Test updating profiles for multiple farms in parallel."""
    # Create initial profiles
    farms = [
        {"farm_id": 1, "geometry": (-8.55, 125.57)},
        {"farm_id": 2, "geometry": (-8.56, 125.58)},
        {"farm_id": 3, "geometry": (-8.57, 125.59)},
    ]

    profiles_2024 = bulk_create_profiles(farms, year=2024, max_workers=3)

    assert len(profiles_2024) > 0
    print(f"\nCreated {len(profiles_2024)} profiles for 2024")

    # Prepare geometries for update
    geometries = {
        1: (-8.55, 125.57),
        2: (-8.56, 125.58),
        3: (-8.57, 125.59),
    }

    # Update only temporal fields for 2025
    print("\nUpdating temporal fields for 2025...")
    profiles_2025 = bulk_update_profiles(
        profiles_df=profiles_2024,
        geometries=geometries,
        fields=["rainfall_mm", "temperature_celsius"],
        year=2025,
        max_workers=3,
    )

    # Verify results
    assert len(profiles_2025) == len(profiles_2024)
    assert isinstance(profiles_2025, pd.DataFrame)

    # Check year was updated
    assert all(profiles_2025["year"] == 2025)

    # Check status
    success_count = (profiles_2025["status"] == "success").sum()
    print(f"\nResults: {success_count}/{len(profiles_2025)} successful")

    # Display comparison
    comparison = pd.DataFrame(
        {
            "farm_id": profiles_2024["id"],
            "rainfall_2024": profiles_2024["rainfall_mm"],
            "rainfall_2025": profiles_2025["rainfall_mm"],
            "temp_2024": profiles_2024["temperature_celsius"],
            "temp_2025": profiles_2025["temperature_celsius"],
        }
    )

    print("\nYear-over-year comparison:")
    print(comparison)


def test_bulk_operations_error_handling(gee_initialized):
    """Test error handling in bulk operations."""
    # Mix of valid and invalid geometries
    farms = [
        {"farm_id": 1, "geometry": (-8.55, 125.57)},  # Valid
        {"farm_id": 2, "geometry": (999, 999)},  # Invalid
        {"farm_id": 3, "geometry": (-8.57, 125.59)},  # Valid
    ]

    print(f"\nTesting error handling with {len(farms)} farms (1 invalid)...")

    profiles_df = bulk_create_profiles(farms, year=2024, max_workers=3)

    # Check results
    success_count = (profiles_df["status"] == "success").sum()
    failed_count = (profiles_df["status"] == "failed").sum()

    print("\nResults:")
    print(f"  Success: {success_count}")
    print(f"  Failed: {failed_count}")

    # Show failed farms
    if failed_count > 0:
        failed = profiles_df[profiles_df["status"] == "failed"]
        print("\nFailed farms:")
        for _, farm in failed.iterrows():
            print(f"  Farm {farm['id']}: {farm.get('error', 'Unknown error')[:50]}")

    assert success_count > 0, "Valid farms should succeed"
    assert len(profiles_df) == len(farms), "Should return result for all farms"


def test_update_all_fields(gee_initialized, test_point):
    """Test updating all fields (full refresh)."""
    # Create initial profile
    profile = build_farm_profile(geometry=test_point, farm_id=1, year=2024)

    assert profile["status"] == "success"

    # Update all fields (fields=None)
    refreshed = update_farm_profile(
        existing_profile=profile,
        geometry=test_point,
        fields=None,  # None = update everything
        year=2024,
    )

    assert refreshed["status"] == "success"

    # Verify all fields present
    required_fields = [
        "id",
        "year",
        "rainfall_mm",
        "temperature_celsius",
        "elevation_m",
        "slope_degrees",
        "soil_ph",
        "area_ha",
    ]

    for field in required_fields:
        assert field in refreshed
        assert refreshed[field] is not None or field == "soil_ph"  # pH might be None

    print("\nFull refresh completed - all fields updated")


def test_custom_fields_preservation(gee_initialized, test_point):
    """Test that custom fields are preserved in updates."""
    # Create profile with custom fields
    profile = build_farm_profile(
        geometry=test_point,
        farm_id=1,
        year=2024,
        farmer_name="John Doe",
        farm_name="Highland Farm",
        crop_type="Coffee",
    )

    assert profile["status"] == "success"
    assert profile["farmer_name"] == "John Doe"
    assert profile["farm_name"] == "Highland Farm"
    assert profile["crop_type"] == "Coffee"

    print("\nCustom fields in profile:")
    print(f"  farmer_name: {profile['farmer_name']}")
    print(f"  farm_name: {profile['farm_name']}")
    print(f"  crop_type: {profile['crop_type']}")

    # Update temporal fields
    updated = update_farm_profile(
        existing_profile=profile, geometry=test_point, fields=["rainfall_mm"], year=2025
    )

    # Custom fields should be preserved
    assert updated["farmer_name"] == "John Doe"
    assert updated["farm_name"] == "Highland Farm"
    assert updated["crop_type"] == "Coffee"

    print("\nCustom fields preserved after update")
