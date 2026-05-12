from decimal import Decimal
from typing import Annotated, List, Optional

from pydantic import BaseModel, ConfigDict, Field

from src.schemas.constants import (
    AREA_MAX,
    AREA_MIN,
    ELEVATION_MAX,
    ELEVATION_MIN,
    LATITUDE_MAX,
    LATITUDE_MIN,
    LONGITUDE_MAX,
    LONGITUDE_MIN,
    RAINFALL_MAX,
    RAINFALL_MIN,
    SLOPE_MAX,
    SLOPE_MIN,
    SOIL_PH_MAX,
    SOIL_PH_MIN,
    TEMPERATURE_MAX,
    TEMPERATURE_MIN,
    AgroforestryTypeID,
    SoilTextureID,
)
from src.schemas.nested_models import (
    AgroforestryTypeReadNested,
    SoilTextureReadNested,
    UserReadNested,
)


# Base Farm model used for validation
class FarmBase(BaseModel):
    rainfall_mm: int = Field(
        title="Annual rainfall in millimetres",
        description="Annual rainfall in millimetres",
        ge=RAINFALL_MIN,  # ge means greater than or equal to, >=
        le=RAINFALL_MAX,  # le means less than or equal to, <=
    )
    temperature_celsius: int = Field(
        title="Annual average temperature",
        description="Average temperature in Celsius",
        ge=TEMPERATURE_MIN,
        le=TEMPERATURE_MAX,
    )
    elevation_m: int = Field(
        title="Elevation above sea level",
        description="Elevation in metres",
        ge=ELEVATION_MIN,
        le=ELEVATION_MAX,
    )
    ph: Decimal = Field(
        title="Soil acidity/alkalinity",
        description="pH value",
        ge=SOIL_PH_MIN,
        le=SOIL_PH_MAX,
        max_digits=2,
        decimal_places=1,
    )
    soil_texture_id: SoilTextureID = Field(
        title="Soil texture ID",
        description="Soil texture ID number",
    )
    area_ha: Decimal = Field(
        title="Farm area",
        description="Total size of the farm in hectares",
        ge=AREA_MIN,
        le=AREA_MAX,
        decimal_places=3,
    )
    latitude: Decimal = Field(
        title="Latitude",
        description="Geographic latitude",
        ge=LATITUDE_MIN,
        le=LATITUDE_MAX,
        decimal_places=5,
    )
    longitude: Decimal = Field(
        title="Longitude",
        description="Geographic longitude",
        ge=LONGITUDE_MIN,
        le=LONGITUDE_MAX,
        decimal_places=5,
    )
    coastal: bool = Field(
        title="Coastal",
        description="Is a coastal environment",
    )
    riparian: bool = Field(
        title="Riparian",
        description="Is a riparian environment",
    )
    nitrogen_fixing: bool = Field(
        title="Nitrogen fixing",
        description="Needs Nitrogen-fixing species",
    )
    shade_tolerant: bool = Field(
        title="Shade Tolerant",
        description="Needs shade tolerant species",
    )
    bank_stabilising: bool = Field(
        title="Bank Stabilising",
        description="Needs erosion control species",
    )
    slope: Decimal = Field(
        title="Slope",
        description="Indicates how steep the farm terrain is, based on elevation gradients.",
        ge=SLOPE_MIN,
        le=SLOPE_MAX,
        decimal_places=2,
    )
    agroforestry_type_ids: Optional[List[AgroforestryTypeID]] = None
    external_id: Optional[int] = Field(default=None, title="Temporary identifier for CSV import")


# Inherits from Base class, provides functionality to create a new farm.
class FarmCreate(FarmBase):
    pass


class FarmRead(FarmBase):
    # This is still WIP, I don't completely understand the impacts it has yet
    # I think it is the fields being exposed to the end-user
    # Of which these existing values would be useless
    id: int = Field(..., description="The unique database ID of the farm.")
    user_id: Optional[int] = Field(None, description="User ID")
    farm_supervisor: Optional[UserReadNested] = Field(None, description="Details of the farm supervisor.")
    soil_texture: SoilTextureReadNested = Field(..., description="The soil texture name and ID.")
    agroforestry_type: List[AgroforestryTypeReadNested] = Field(
        default_factory=list,  # default value if none currently exist will be [].
        description="List of associated agroforestry types with names.",
    )

    model_config = ConfigDict(from_attributes=True)


class FarmUpdate(BaseModel):
    # Annotated is used to restate validators explicitly, as Pydantic v2 does not
    # enforce Field constraints on Optional fields without it.
    rainfall_mm: Optional[Annotated[int, Field(ge=RAINFALL_MIN, le=RAINFALL_MAX)]] = None
    temperature_celsius: Optional[Annotated[int, Field(ge=TEMPERATURE_MIN, le=TEMPERATURE_MAX)]] = None
    elevation_m: Optional[Annotated[int, Field(ge=ELEVATION_MIN, le=ELEVATION_MAX)]] = None
    ph: Optional[Annotated[Decimal, Field(ge=SOIL_PH_MIN, le=SOIL_PH_MAX, max_digits=2, decimal_places=1)]] = None
    soil_texture_id: Optional[SoilTextureID] = None
    area_ha: Optional[Annotated[Decimal, Field(ge=AREA_MIN, le=AREA_MAX, decimal_places=3)]] = None
    latitude: Optional[Annotated[Decimal, Field(ge=LATITUDE_MIN, le=LATITUDE_MAX, decimal_places=5)]] = None
    longitude: Optional[Annotated[Decimal, Field(ge=LONGITUDE_MIN, le=LONGITUDE_MAX, decimal_places=5)]] = None
    coastal: Optional[bool] = None
    riparian: Optional[bool] = None
    nitrogen_fixing: Optional[bool] = None
    shade_tolerant: Optional[bool] = None
    bank_stabilising: Optional[bool] = None
    slope: Optional[Annotated[Decimal, Field(ge=SLOPE_MIN, le=SLOPE_MAX, decimal_places=2)]] = None
    agroforestry_type_ids: Optional[List[AgroforestryTypeID]] = None
    external_id: Optional[int] = Field(default=None, title="Temporary identifier for CSV import")


class FarmBoundaryResponse(BaseModel):
    type: str
    geometry: dict
    properties: dict
