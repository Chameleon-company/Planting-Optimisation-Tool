from typing import Optional

from pydantic import BaseModel, ConfigDict


class SaplingEstimationRequest(BaseModel):
    farm_id: int
    spacing_x: float
    spacing_y: float
    max_slope: float


class SaplingEstimationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)
    status: str = "success"
    id: Optional[int] = None

    pre_slope_count: Optional[int] = None
    aligned_count: Optional[int] = None

    optimal_angle: Optional[int] = None
