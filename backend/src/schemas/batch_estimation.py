from typing import List, Optional

from pydantic import BaseModel, ConfigDict


class SaplingBatchEstimationRequest(BaseModel):
    spacing_x: float
    spacing_y: float
    max_slope: float


class SaplingBatchEstimationItem(BaseModel):  # Estimation result for a single farm
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)
    status: str = "success"

    farm_id: int

    pre_slope_count: Optional[int] = None
    aligned_count: Optional[int] = None
    optimal_angle: Optional[int] = None
    rotation_average: Optional[float] = None
    rotation_std_dev: Optional[float] = None


class SaplingBatchEstimationResponse(BaseModel):
    status: str = "success"
    farm_count: int
    results: List[SaplingBatchEstimationItem]
