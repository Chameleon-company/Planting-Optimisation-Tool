from typing import Optional
from pydantic import BaseModel, Field


class ParameterBase(BaseModel):
    id: int = Field(
        title="ID",
        description="Unique identifier for the parameter",
    )

    species_id: int = Field(
        title="Species ID",
        description="Species identifier",
    )
    feature: str = Field(
        title="Feature",
        description="Name of the feature",
    )
    score_method: str = Field(
        title="Score method",
        description="Scoring method of the feature",
    )
    weight: float = Field(
        title="Weight",
        description="Weight of the feature",
        ge=0.0,
        le=1.0,
    )
    trap_left_tol: Optional[float] = Field(
        default=None,
        title="Trapezoid left tolerance",
        description="Trapezoid left tolerance",
        ge=0,
        le=5000,
    )
    trap_right_tol: Optional[float] = Field(
        default=None,
        title="Trapezoid right tolerance",
        description="Trapezoid right tolerance",
        ge=0,
        le=5000,
    )
