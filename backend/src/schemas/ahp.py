from typing import Dict, List

from pydantic import BaseModel


# AHP calculation request and response models
class AhpCalculationRequest(BaseModel):
    species_id: int
    matrix: List[List[float]]


class AhpResponse(BaseModel):
    weights: Dict[str, float]
    consistency_ratio: float
    is_consistent: bool
    message: str
