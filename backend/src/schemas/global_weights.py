from datetime import datetime
from typing import List
from uuid import UUID

from pydantic import BaseModel, Field, model_validator


class GlobalWeightItemSchema(BaseModel):
    feature: str = Field(
        title="Feature",
        description="Name of the feature",
    )

    mean_weight: float = Field(
        title="Mean global weight",
        description="Mean global importance of the feature",
        ge=0.0,
        le=1.0,
    )

    ci_lower: float = Field(
        title="Lower confidence bound",
        description="Lower confidence bound of the global weight (clipped at zero)",
        ge=0.0,
        le=1.0,
    )

    ci_upper: float = Field(
        title="Upper confidence bound",
        description="Upper confidence bound of the global weight",
        ge=0.0,
        le=1.0,
    )

    ci_width: float = Field(
        title="CI width",
        description="Width of the confidence interval",
        ge=0.0,
        le=1.0,
    )

    touches_zero: bool = Field(
        title="Touches zero",
        description="Whether the lower CI bound is zero (weak or uncertain importance)",
    )


class GlobalWeightsRunSummarySchema(BaseModel):
    run_id: UUID = Field(
        title="Run ID",
        description="Unique identifier for this global weight computation run",
    )
    created_at: datetime = Field(
        title="Created at",
        description="Timestamp when the global weights were computed",
    )
    bootstraps: int = Field(
        title="RF bootstraps",
        description="Number of Random Forest bootstrap samples used",
        ge=1,
    )
    bootstrap_early_stopped: bool = Field(
        title="RF early stopped",
        description="Whether RF bootstrapping stopped early due to convergence",
    )
    source: str | None = Field(
        title="Source",
        description="Optional source information (e.g. 'Imported from CSV')",
        default=None,
    )


class GlobalWeightsRunDetailSchema(GlobalWeightsRunSummarySchema):
    weights: List[GlobalWeightItemSchema] = Field(
        title="Global weights",
        description="List of global importance weights",
    )


class GlobalWeightsCSVMeta(BaseModel):
    bootstraps: int = Field(ge=1)
    bootstrap_early_stopped: bool


class GlobalWeightsCSVRow(BaseModel):
    feature: str
    mean_weight: float = Field(ge=0.0, le=1.0)
    ci_lower: float = Field(ge=0.0, le=1.0)
    ci_upper: float = Field(ge=0.0, le=1.0)

    @model_validator(mode="after")
    def validate_ci_order(self):
        if not (self.ci_lower <= self.mean_weight <= self.ci_upper):
            raise ValueError("Expected ci_lower ≤ mean_weight ≤ ci_upper")
        return self

    @model_validator(mode="after")
    def validate_feature_not_blank(self):
        if not self.feature.strip():
            raise ValueError("Feature name must not be empty")
        return self
