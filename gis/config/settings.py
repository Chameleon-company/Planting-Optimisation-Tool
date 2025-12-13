import os
from dotenv import load_dotenv

# Path to .env inside the gis folder
ENV_PATH = os.path.join(
    os.path.dirname(os.path.dirname(__file__)),  # go up from config/ to gis/
    ".env",
)

load_dotenv(ENV_PATH)

SERVICE_ACCOUNT = os.getenv("GEE_SERVICE_ACCOUNT")
KEY_PATH = os.getenv("GEE_KEY_PATH")

# --- Environmental asset settings  ---
RAINFALL_ASSET_ID = os.getenv("RAINFALL_ASSET_ID")
RAINFALL_BAND = os.getenv("RAINFALL_BAND")
RAINFALL_SCALE = int(os.getenv("RAINFALL_SCALE", "30"))

TEMP_ASSET_ID = os.getenv("TEMP_ASSET_ID")
TEMP_BAND = os.getenv("TEMP_BAND")
TEMP_SCALE = int(os.getenv("TEMP_SCALE", "30"))

SOIL_PH_ASSET_ID = os.getenv("SOIL_PH_ASSET_ID")
SOIL_PH_FIELD = os.getenv("SOIL_PH_FIELD")

SOIL_TEXTURE_ASSET_ID = os.getenv("SOIL_TEXTURE_ASSET_ID")
SOIL_TEXTURE_FIELD = os.getenv("SOIL_TEXTURE_FIELD")

DEM_ASSET_ID = os.getenv("DEM_ASSET_ID")
DEM_BAND = os.getenv("DEM_BAND")
DEM_SCALE = int(os.getenv("DEM_SCALE", "30"))

SLOPE_BAND = os.getenv("SLOPE_BAND")

BOUNDARY_TIMOR_ASSET_ID = os.getenv("BOUNDARY_TIMOR_ASSET_ID")
