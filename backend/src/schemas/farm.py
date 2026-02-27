from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional
from decimal import Decimal

from src.schemas.constants import SoilTextureID
from src.schemas.constants import AgroforestryTypeID
from src.schemas.nested_models import (
    UserReadNested,
    AgroforestryTypeReadNested,
    SoilTextureReadNested,
)


# Base Farm model used for validation
class FarmBase(BaseModel):
    rainfall_mm: int = Field(
        title="Annual rainfall in millimetres",
        description="Annual rainfall in millimetres",
        ge=1000,  # ge means greater than or equal to, >=
        le=3000,  # le means less than or equal to, <=
    )
    temperature_celsius: int = Field(
        title="Annual average temperature",
        description="Average temperature in Celsius",
        ge=15,
        le=30,
    )
    elevation_m: int = Field(
        title="Elevation above sea level",
        description="Elevation in metres",
        ge=0,
        le=2963,
    )
    ph: Decimal = Field(
        title="Soil acidity/alkalinity",
        description="pH value",
        ge=4.0,
        le=8.5,
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
        ge=0,
        le=100,
        decimal_places=3,
    )
    latitude: Decimal = Field(
        title="Latitude",
        description="Geographic latitude",
        ge=-90,
        le=90,
        decimal_places=5,
    )
    longitude: Decimal = Field(
        title="Longitude",
        description="Geographic longitude",
        ge=-180,
        le=180,
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
        ge=0,
        le=90,
        decimal_places=2,
    )
    agroforestry_type_ids: Optional[List[AgroforestryTypeID]] = None
    external_id: Optional[int] = Field(
        default=None, title="Temporary identifier for CSV import"
    )


# Inherits from Base class, provides functionality to create a new farm.
class FarmCreate(FarmBase):
    pass


class FarmRead(FarmBase):
    # This is still WIP, I don't completely understand the impacts it has yet
    # I think it is the fields being exposed to the end-user
    # Of which these existing values would be useless
    id: int = Field(..., description="The unique database ID of the farm.")
    user_id: Optional[int] = Field(None, description="User ID")
    farm_supervisor: Optional[UserReadNested] = Field(
        None, description="Details of the farm supervisor."
    )
    soil_texture: SoilTextureReadNested = Field(
        ..., description="The soil texture name and ID."
    )
    agroforestry_type: List[AgroforestryTypeReadNested] = Field(
        default_factory=list,  # default value if none currently exist will be [].
        description="List of associated agroforestry types with names.",
    )

    model_config = ConfigDict(from_attributes=True)


# Updating a field of a farm doesn't require all other fields being passed too
# Therefore this class inherits the validation criteria from Base while making each field optional.
class FarmUpdate(FarmBase):
    rainfall_mm: Optional[int] = None
    temperature_celsius: Optional[int] = None
    elevation_m: Optional[int] = None
    ph: Optional[Decimal] = None
    soil_texture_id: Optional[SoilTextureID] = None
    area_ha: Optional[Decimal] = None
    latitude: Optional[Decimal] = None
    longitude: Optional[Decimal] = None
    coastal: Optional[bool] = None
    riparian: Optional[bool] = None
    nitrogen_fixing: Optional[bool] = None
    shade_tolerant: Optional[bool] = None
    bank_stabilising: Optional[bool] = None
    slope: Optional[Decimal] = None
    agroforestry_type_ids: Optional[List[AgroforestryTypeID]] = None
