# Species table model and reference tables
# For type hinting only, not runtime
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database import Base

if TYPE_CHECKING:
    from src.models.agroforestry_type import AgroforestryType
    from src.models.soil_texture import SoilTexture
from src.models.association import (
    species_agroforestry_association,
    species_soil_texture_association,
)
from src.models.exclusion_rules import SpeciesDependency, SpeciesExclusionRule
from src.models.parameters import Parameter


class Species(Base):
    __tablename__ = "species"
    # Column names
    id: Mapped[int] = mapped_column(primary_key=True)

    name: Mapped[str] = mapped_column()
    common_name: Mapped[str] = mapped_column()
    rainfall_mm_min: Mapped[int] = mapped_column()
    rainfall_mm_max: Mapped[int] = mapped_column()
    temperature_celsius_min: Mapped[int] = mapped_column()
    temperature_celsius_max: Mapped[int] = mapped_column()
    elevation_m_min: Mapped[int] = mapped_column()
    elevation_m_max: Mapped[int] = mapped_column()
    ph_min: Mapped[float] = mapped_column()  # 1 decimal
    ph_max: Mapped[float] = mapped_column()  # 1 decimal
    coastal: Mapped[bool] = mapped_column()
    riparian: Mapped[bool] = mapped_column()
    nitrogen_fixing: Mapped[bool] = mapped_column()
    shade_tolerant: Mapped[bool] = mapped_column()
    bank_stabilising: Mapped[bool] = mapped_column()

    # Relationships
    # -------------
    # Links a species object to its corresponding soil_texture object
    soil_textures: Mapped[list["SoilTexture"]] = relationship(
        secondary=species_soil_texture_association,
        back_populates="soil_textures_for_species",
    )

    # Links a species object to its corresponding agroforestry_type object
    agroforestry_types: Mapped[list["AgroforestryType"]] = relationship(
        secondary=species_agroforestry_association,
        back_populates="species_agroforestry_type",
    )

    # Links a species object to parameter object
    parameters: Mapped[list["Parameter"]] = relationship(back_populates="species", cascade="all, delete-orphan")

    # Links a species object to its corresponding exclusion rules
    exclusion_rules: Mapped[list["SpeciesExclusionRule"]] = relationship(back_populates="species", cascade="all, delete-orphan")

    # Links a species object to its corresponding dependencies
    dependencies: Mapped[list["SpeciesDependency"]] = relationship(
        "SpeciesDependency", foreign_keys="[SpeciesDependency.focal_species_id]", back_populates="focal_species", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        """Returns the official string representation of the Species object.
        Used primarily for debugging, logging, inspection.
        """
        return f"Species(id={self.id!r}, name={self.name!r}, common_name={self.common_name!r})"
