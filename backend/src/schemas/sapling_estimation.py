from pydantic import BaseModel, ConfigDict
from typing import Optional


class SaplingEstimationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)
    status: str = "success"
    id: Optional[int] = None

    sapling_count: Optional[int] = None

    optimal_angle: Optional[int] = None
