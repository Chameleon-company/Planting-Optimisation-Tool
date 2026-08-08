from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class PlantingGridResponse(BaseModel):
    type: str
    features: list[dict]


class SaplingEstimationRequest(BaseModel):
    farm_ids: list[int] = Field(min_length=1)
    spacing_x: float
    spacing_y: float
    max_slope: float


class SaplingEstimationItem(BaseModel):  # Estimation result for a single farm
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    status: str = "success"
    farm_id: int
    message: Optional[str] = None

    pre_slope_count: Optional[int] = None
    aligned_count: Optional[int] = None
    baseline_tree_count: Optional[int] = None
    additional_sapling_count: Optional[int] = None

    optimal_angle: Optional[int] = None

    # added rotational
    rotation_average: Optional[float] = None
    rotation_std_dev: Optional[float] = None


class SaplingEstimationResponse(BaseModel):
    status: str = "success"
    farm_count: int
    results: list[SaplingEstimationItem]
