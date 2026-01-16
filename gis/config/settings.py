"""
Configuration Settings

Loads GEE authentication from .env and defines all dataset configurations.
"""

import os
from dotenv import load_dotenv

# Path to .env inside the gis folder
ENV_PATH = os.path.join(
    os.path.dirname(os.path.dirname(__file__)),  # go up from config/ to gis/
    ".env",
)

load_dotenv(ENV_PATH)

# ============================================================================
# GEE AUTHENTICATION
# ============================================================================

SERVICE_ACCOUNT = os.getenv("GEE_SERVICE_ACCOUNT")
KEY_PATH = os.getenv("GEE_KEY_PATH")


# ============================================================================
# DATASET CONFIGURATIONS
# ============================================================================

DATASETS = {
    "rainfall": {
        "type": "raster",
        "asset_id": "UCSB-CHG/CHIRPS/DAILY",
        "band": "precipitation",
        "scale": 5566,
        "reducer": "sum",  # Sum daily values for annual rainfall
        "description": "CHIRPS Daily Rainfall - Validated (r=0.96, MAE=23mm)",
        "unit": "mm",
        "post_process": "round_int",
        "temporal": True,
        "validation_status": "excellent",
    },
    "elevation": {
        "type": "raster",
        "asset_id": "CGIAR/SRTM90_V4",  # or "USGS/SRTMGL1_003" for 30m
        "band": "elevation",
        "scale": 90,
        "reducer": "mean",
        "description": "SRTM DEM 90m - Validated (r=0.98, MAE=11m)",
        "unit": "m",
        "post_process": "round_int",
        "validation_status": "excellent",
    },
    "temperature": {
        "type": "raster",
        "asset_id": "MODIS/061/MOD11A2",  # 8-day composite
        "band": "LST_Day_1km",
        "scale": 1000,
        "reducer": "mean",
        "description": "MODIS LST - Validated (r=0.87, MAE=1.5°C with correction)",
        "unit": "celsius",
        "scale_factor": 0.02,
        "offset": -273.15,  # Kelvin to Celsius
        "bias_correction": -4.43,  # Critical: validated bias correction from EDA
        "post_process": "round_1dp",
        "temporal": True,
        "validation_status": "good",
        "note": "Requires -4.43°C bias correction (LST vs air temp difference)",
    },
    "soil_ph": {
        "type": "raster",
        "asset_id": "OpenLandMap/SOL/SOL_PH-H2O_USDA-4C1A2A_M/v02",
        "band": "b0",  # 0cm depth
        "scale": 250,
        "reducer": "mean",
        "description": "OpenLandMap Soil pH - NOT RECOMMENDED (r=0.18, MAE=1.21)",
        "unit": "pH",
        "scale_factor": 0.1,
        "post_process": "round_1dp",
        "validation_status": "poor",
        "warning": "Low correlation (r=0.18) - Not suitable for Timor-Leste. Use local calibration model or exclude from analysis.",
    },
    "soil_texture": {
        "type": "raster",
        "asset_id": "OpenLandMap/SOL/SOL_PH-H2O_USDA-4C1A2A_M/v02",  # Using pH as proxy to demonstrate extraction
        "band": "b0",
        "scale": 250,
        "reducer": "mean",
        "description": "Placeholder using OpenLandMap pH - demonstrates GEE extraction capability",
        "unit": "pH_value",
        "scale_factor": 0.1,
        "note": "This is a demonstration placeholder. Replace with actual soil texture asset when available.",
    },
    "dem": {
        "type": "raster",
        "asset_id": "CGIAR/SRTM90_V4",
        "band": "elevation",
        "scale": 90,
        "description": "DEM for slope calculation (same as elevation)",
    },
}


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================


def get_dataset_config(name: str) -> dict:
    """Get configuration for a dataset."""
    if name not in DATASETS:
        raise ValueError(f"Unknown dataset: {name}. Available: {list(DATASETS.keys())}")
    return DATASETS[name]


def get_dataset_info(name: str) -> str:
    """Get description of a dataset."""
    config = get_dataset_config(name)
    return f"{name}: {config.get('description', 'No description')}"


def update_dataset(name: str, **kwargs):
    """
    Update configuration for a specific dataset.

    Example:
        update_dataset('rainfall',
                      asset_id='projects/your-project/your-rainfall',
                      band='precipitation',
                      scale=5000)
    """
    if name not in DATASETS:
        raise ValueError(f"Unknown dataset: {name}")

    DATASETS[name].update(kwargs)


# ============================================================================
# TEXTURE MAPPING
# ============================================================================

TEXTURE_MAP = {
    "sand": 1,
    "loamy sand": 2,
    "sandy loam": 3,
    "loam": 4,
    "silt loam": 5,
    "silt": 6,
    "sandy clay loam": 7,
    "clay loam": 8,
    "silty clay loam": 9,
    "sandy clay": 10,
    "silty clay": 11,
    "clay": 12,
}


def list_datasets():
    """Return list of all configured dataset names."""
    return list(DATASETS.keys())
