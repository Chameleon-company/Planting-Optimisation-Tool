from decimal import Decimal
from enum import Enum, IntEnum


# User role definitions
# Roles define permission levels in the system with a hierarchical structure:
# - OFFICER (level 1): Basic user with limited permissions
# - SUPERVISOR (level 2): Can view and manage users and resources
# - ADMIN (level 3): Full system access, can create/update/delete all resources
class Role(str, Enum):
    """Enumeration of user roles with hierarchical permissions."""

    OFFICER = "officer"
    SUPERVISOR = "supervisor"
    ADMIN = "admin"


class SoilTextureID(IntEnum):
    SAND = 1
    LOAMY_SAND = 2
    SANDY_LOAM = 3
    LOAM = 4
    SILTY_LOAM = 5
    SILT = 6
    SANDY_CLAY_LOAM = 7
    CLAY_LOAM = 8
    SILTY_CLAY_LOAM = 9
    SANDY_CLAY = 10
    SILTY_CLAY = 11
    CLAY = 12


class AgroforestryTypeID(IntEnum):
    BLOCK = 1
    BOUNDARY = 2
    INTERCROPPING = 3
    MOSAIC = 4


# Validation Constants

# Soil pH
SOIL_PH_MIN = Decimal("5.0")
SOIL_PH_MAX = Decimal("8.5")

# Rainfall
RAINFALL_MIN = 500
RAINFALL_MAX = 3000

# Temperature
TEMPERATURE_MIN = 15
TEMPERATURE_MAX = 30

# Elevation
ELEVATION_MIN = 0
ELEVATION_MAX = 2963

# Area
AREA_MIN = 0
AREA_MAX = 100

# Latitude
LATITUDE_MIN = -90
LATITUDE_MAX = 90

# Longitude
LONGITUDE_MIN = -180
LONGITUDE_MAX = 180

# Slope
SLOPE_MIN = 0
SLOPE_MAX = 90

# CRS for riparian analysis
CRS_ANALYSIS = 32751  # UTM 51S

# Riparian buffer distance in meters
RIPARIAN_BUFFER_M: float = 15.0
