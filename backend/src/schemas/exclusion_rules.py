from typing import List, Union

from pydantic import BaseModel, ConfigDict, Field


class SpeciesExclusionRuleBase(BaseModel):
    feature: str = Field(..., description="The farm feature to check (e.g., 'ph', 'rainfall_mm', 'soil_texture')")
    operator: str = Field(..., description="The logical operator: '<', '>', '==', '!=', 'in_set', 'not_in_set'")
    # Union allows the JSON column to accept diverse types
    value: Union[float, str, List[str]] = Field(..., description="The threshold value (number, single string, or list of strings)")
    reason: str = Field(..., description="The narrative reason for exclusion (e.g., 'elevation is too high')")


class SpeciesExclusionRuleCreate(SpeciesExclusionRuleBase):
    species_id: int


class SpeciesExclusionRuleRead(SpeciesExclusionRuleBase):
    id: int
    species_id: int

    model_config = ConfigDict(from_attributes=True)


class SpeciesDependencyBase(BaseModel):
    focal_species_id: int
    required_partner_id: int


class SpeciesDependencyCreate(SpeciesDependencyBase):
    """No extra fields needed, but separates creation from reading."""

    pass


class SpeciesDependencyRead(SpeciesDependencyBase):
    id: int
    model_config = ConfigDict(from_attributes=True)
