from pydantic import Field, ConfigDict, field_validator
from typing import Optional
from decimal import Decimal
from src.schemas.farm import FarmBase


class FarmProfileResponse(FarmBase):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)
    status: str = "success"
    id: Optional[int] = None

    rainfall_mm: Optional[int] = None

    @field_validator("rainfall_mm", mode="before")
    @classmethod
    def validate_rainfall_bounds(cls, v):
        # If it's outside of the bounds of the data_dictionary
        # It is invalid and should return None
        if v is not None and (v < 1000 or v > 3000):
            return None
        return v

    temperature_celsius: Optional[int] = None

    @field_validator("temperature_celsius", mode="before")
    @classmethod
    def validate_temp_bounds(cls, v):
        # If it's outside of the bounds of the data_dictionary
        # It is invalid and should return None
        if v is not None and (v < 15 or v > 30):
            return None
        return v

    elevation_m: Optional[int] = None
    ph: Optional[Decimal] = Field(None, alias="ph", validation_alias="soil_ph")
    slope: Optional[Decimal] = Field(
        None, alias="slope", validation_alias="slope_degrees"
    )

    riparian: Optional[bool] = None
    nitrogen_fixing: Optional[bool] = None
    shade_tolerant: Optional[bool] = None
    bank_stabilising: Optional[bool] = None
    soil_texture_id: Optional[int] = None

    area_ha: Optional[Decimal] = None
    latitude: Optional[Decimal] = None
    longitude: Optional[Decimal] = None
    coastal: Optional[bool] = None
