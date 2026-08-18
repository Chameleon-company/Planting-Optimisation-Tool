from typing import List, Literal, Optional, Union

from pydantic import BaseModel, ConfigDict, Field


class SpeciesExclusionRuleBase(BaseModel):
    feature: str = Field(
        ...,
        description="The farm feature to check (e.g., 'ph', 'rainfall_mm', 'soil_texture')",
    )
    operator: Literal["<", ">", "<=", ">=", "==", "!=", "in_set", "not_in_set"] = Field(
        ...,
        description="The comparison operator used by the exclusion engine",
    )
    # Union allows the JSON column to accept diverse types
    value: Union[float, str, List[str]] = Field(
        ...,
        description="The threshold value (number, single string, or list of strings)",
    )
    reason: str = Field(
        ...,
        description="The narrative reason for exclusion (e.g., 'elevation is too high')",
    )


class SpeciesExclusionRuleCreate(SpeciesExclusionRuleBase):
    species_id: int = Field(..., gt=0)


class SpeciesExclusionRuleUpdate(BaseModel):
    species_id: Optional[int] = Field(default=None, gt=0)
    feature: Optional[str] = Field(default=None, min_length=1)
    operator: Optional[Literal["<", ">", "<=", ">=", "==", "!=", "in_set", "not_in_set"]] = None
    value: Optional[Union[float, str, List[str]]] = None
    reason: Optional[str] = Field(default=None, min_length=1)


class SpeciesExclusionRuleRead(SpeciesExclusionRuleBase):
    id: int
    species_id: int

    model_config = ConfigDict(from_attributes=True)


class SpeciesDependencyBase(BaseModel):
    focal_species_id: int = Field(..., gt=0)
    required_partner_id: int = Field(..., gt=0)


class SpeciesDependencyCreate(SpeciesDependencyBase):
    """No extra fields needed, but separates creation from reading."""

    pass


class SpeciesDependencyUpdate(BaseModel):
    focal_species_id: Optional[int] = Field(default=None, gt=0)
    required_partner_id: Optional[int] = Field(default=None, gt=0)


class SpeciesDependencyRead(SpeciesDependencyBase):
    id: int
    model_config = ConfigDict(from_attributes=True)
