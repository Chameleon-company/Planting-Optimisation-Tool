from pydantic import BaseModel, Field
from typing import List, Optional
from decimal import Decimal
from src.schemas.constants import SoilTextureID
from src.schemas.constants import AgroforestryTypeID
from src.schemas.nested_models import AgroforestryTypeReadNested, SoilTextureReadNested


class SpeciesBase(BaseModel):
    name: str = Field(
        title="Name",
        description="Scientific name of the species",
    )
    common_name: str = Field(
        title="Common name",
        description="Common name of the species",
    )
    rainfall_mm_min: int = Field(
        title="Minimum rainfall",
        description="Minimum preferred annual rainfall",
        ge=200,
        le=5000,
    )
    rainfall_mm_max: int = Field(
        title="Maximum rainfall",
        description="Maximum preferred annual rainfall",
        ge=200,
        le=5000,
    )
    temperature_celsius_min: int = Field(
        title="Minimum temperature",
        description="Minimum preferred temperature in celsius",
        ge=10,
        le=40,
    )
    temperature_celsius_max: int = Field(
        title="Maximum temperature",
        description="Maximum preferred temperature in celsius",
        ge=10,
        le=40,
    )
    elevation_m_min: int = Field(
        title="Minimum elevation",
        description="Minimum preferred altitude",
        ge=0,
        le=3000,
    )
    elevation_m_max: int = Field(
        title="Maximum elevation",
        description="Maximum preferred altitude",
        ge=0,
        le=3000,
    )
    ph_min: Decimal = Field(
        title="Minimum pH",
        description="Minimum preferred soil pH",
        ge=4.0,
        le=7.0,
    )
    ph_max: Decimal = Field(
        title="Maximum pH",
        description="Maximum preferred soil pH",
        ge=7.0,
        le=8.5,
    )
    coastal: bool = Field(
        title="Coastal",
        description="Suitable for coastal environment",
    )
    riparian: bool = Field(
        title="Riparian",
        description="Suitable for wetlands adjacent to rivers and streams",
    )
    nitrogen_fixing: bool = Field(
        title="Nitrogen fixing",
        description="Provides Nitrogen-fixing function",
    )
    shade_tolerant: bool = Field(
        title="Shade tolerant",
        description="Is tolerant to shade",
    )
    bank_stabilising: bool = Field(
        title="Bank stabilising",
        description="Can be used for erosion control",
    )
    soil_textures: Optional[List[SoilTextureID]] = None
    agroforestry_types: Optional[List[AgroforestryTypeID]] = None


class SpeciesCreate(SpeciesBase):
    # Not needed yet, as we're using the existing dataset provided.
    pass


class SpeciesRead(SpeciesBase):
    id: int = Field(..., description="Unique database ID of the species.")

    # Shows the Names of the soil textures instead of the ID number
    soil_textures: List[SoilTextureReadNested] = Field(
        default_factory=list, description="List of compatible soil textures with names."
    )

    # Shows the Names of the Agroforestry types instead of the ID number
    agroforestry_types: List[AgroforestryTypeReadNested] = Field(
        default_factory=list,
        description="List of compatible agroforestry uses with names.",
    )

    class Config:
        from_attributes = True


class SpeciesUpdate(SpeciesBase):
    # Updating a species' attributes will inherit all fields from base, but optionally.
    name: Optional[str] = None
    common_name: Optional[str] = None
    rainfall_mm_min: Optional[int] = None
    rainfall_mm_max: Optional[int] = None
    temperature_celsius_min: Optional[int] = None
    temperature_celsius_max: Optional[int] = None
    elevation_m_min: Optional[int] = None
    elevation_m_max: Optional[int] = None
    ph_min: Optional[Decimal] = None
    ph_max: Optional[Decimal] = None
    coastal: Optional[bool] = None
    riparian: Optional[bool] = None
    nitrogen_fixing: Optional[bool] = None
    shade_tolerant: Optional[bool] = None
    bank_stabilising: Optional[bool] = None
    soil_textures: Optional[List[SoilTextureID]] = None
    agroforestry_types: Optional[List[AgroforestryTypeID]] = None
