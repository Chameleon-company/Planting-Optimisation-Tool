from pydantic import BaseModel, Field
from typing import List, Optional

from src.schemas.constants import SoilTextureID
from src.schemas.constants import AgroforestryTypeID

# from soil_texture import SoilTextureRead


# Base Farm model used for validation
class FarmBase(BaseModel):
    rainfall_mm: int = Field(
        title="Annual rainfall in millimetres",
        description="Annual rainfall in millimetres - Accepted range 1000-3000.",
        ge=1000,  # ge means greater than or equal to, >=
        le=3000,  # le means less than or equal to, <=
    )
    temperature_celsius: int = Field(
        title="Annual average temperature",
        description="",
        ge=15,
        le=30,
    )
    elevation_m: int = Field(
        title="Elevation above sea level",
        description="",
        ge=0,
        le=2963,
    )
    ph: float = Field(
        title="Soil acidity/alkalinity",
        ge=4.0,
        le=8.5,
        max_digits=2,
        decimal_places=1,
    )
    soil_texture_id: SoilTextureID = Field(
        title="Soil texture ID",
        description="Soil texture ID number",
    )
    area_ha: float = Field(
        title="Farm area",
        description="Total size of the farm in hectares",
        ge=0,
        le=100,
        decimal_places=3,
    )
    latitude: float = Field(
        title="Latitude",
        description="Geographic latitude",
        ge=-90,
        le=90,
        decimal_places=5,
    )
    longitude: float = Field(
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
    slope: float = Field(
        title="Slope",
        description="Indicates how steep the farm terrain is, based on elevation gradients.",
        ge=0,
        le=90,
        decimal_places=2,
    )
    agroforestry_type_ids: Optional[List[AgroforestryTypeID]] = None


# Inherits from Base class, provides functionality to create a new farm.
class FarmCreate(FarmBase):
    # WIP
    pass


class FarmRead(FarmBase):
    # This is still WIP, I don't completely understand the impacts it has yet
    # I think it is the fields being exposed to the end-user
    # Of which these existing values would be useless
    id: int = Field(..., description="The unique database ID of the farm.")
    user_id: int = Field(..., description="The ID of the user who owns this farm.")
    agroforestry_type_ids: List[int] = Field(
        default_factory=list,
        description="List of IDs representing the agroforestry types associated with the farm.",
    )


# Updating a field of a farm doesn't require all other fields being passed too
# Therefore this class inherits the validation criteria from Base while making each field optional.
class FarmUpdate(FarmBase):
    rainfall_mm: Optional[int] = None
    temperature_celsius: Optional[int] = None
    elevation_m: Optional[int] = None
    ph: Optional[float] = None
    soil_texture_id: Optional[SoilTextureID] = None
    area_ha: Optional[float] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    coastal: Optional[bool] = None
    riparian: Optional[bool] = None
    nitrogen_fixing: Optional[bool] = None
    shade_tolerant: Optional[bool] = None
    bank_stabilising: Optional[bool] = None
    slope: Optional[float] = None
    agroforestry_type_ids: Optional[List[AgroforestryTypeID]] = None
