from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class ParameterBase(BaseModel):
    species_id: int = Field(
        title="Species ID",
        description="ID of the species this parameter belongs to",
    )
    feature: str = Field(
        title="Feature",
        description="Name of the environmental feature (e.g. 'rainfall', 'temperature')",
    )
    score_method: str = Field(
        title="Score method",
        description="Scoring method used for this feature (e.g. 'trapezoid')",
    )
    weight: float = Field(
        title="Weight",
        description="Relative importance weight of this feature, between 0 and 1",
        ge=0.0,
        le=1.0,
    )
    trap_left_tol: Optional[float] = Field(
        default=None,
        title="Trapezoid left tolerance",
        description="Left tolerance value for trapezoid scoring",
        ge=0,
        le=5000,
    )
    trap_right_tol: Optional[float] = Field(
        default=None,
        title="Trapezoid right tolerance",
        description="Right tolerance value for trapezoid scoring",
        ge=0,
        le=5000,
    )


class ParameterCreate(ParameterBase):
    pass


class ParameterUpdate(ParameterBase):
    species_id: Optional[int] = None
    feature: Optional[str] = None
    score_method: Optional[str] = None
    weight: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    trap_left_tol: Optional[float] = Field(default=None, ge=0, le=5000)
    trap_right_tol: Optional[float] = Field(default=None, ge=0, le=5000)


class ParameterRead(ParameterBase):
    id: int = Field(title="ID", description="Unique identifier for the parameter")
    score_method: Optional[str] = None
    weight: Optional[float] = None

    model_config = ConfigDict(from_attributes=True)
