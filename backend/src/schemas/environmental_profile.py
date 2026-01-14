from pydantic import BaseModel
from typing import Optional


class FarmProfileResponse(BaseModel):
    id: Optional[int]
    rainfall_mm: int
    temperature_celsius: int
    elevation_m: int
    ph: float
    soil_texture_id: Optional[int]
    area_ha: float
    latitude: float
    longitude: float
    coastal: bool
    slope: float
