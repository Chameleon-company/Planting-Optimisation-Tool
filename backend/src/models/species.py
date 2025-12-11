# Species table model and reference tables
from sqlalchemy import ForeignKey
from ..database import Base
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship

# For type hinting only, not runtime
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .soil_texture import SoilTexture
    from .agroforestry_type import AgroforestryType
from .association import (
    species_agroforestry_association,
    species_soil_texture_association,
)


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
    # preferred_soil_texture_id: Mapped[int] = mapped_column(
    #     ForeignKey("soil_textures.id", ondelete="CASCADE")
    # )
    coastal: Mapped[bool] = mapped_column()
    riparian: Mapped[bool] = mapped_column()
    nitrogen_fixing: Mapped[bool] = mapped_column()
    shade_tolerant: Mapped[bool] = mapped_column()
    bank_stabilising: Mapped[bool] = mapped_column()

    # Relationships
    # -------------
    # Links a species object to its corresponding soil_texture object
    # preferred_soil_texture_link: Mapped["SoilTexture"] = relationship(
    #     back_populates="preferred_species_link"
    # )
    soil_textures: Mapped[list["SoilTexture"]] = relationship(
        secondary=species_soil_texture_association,
        back_populates="soil_textures_for_species",
    )

    # Links a species object to its corresponding agroforestry_type object
    agroforestry_types: Mapped[list["AgroforestryType"]] = relationship(
        secondary=species_agroforestry_association,
        back_populates="species_agroforestry_type",
    )

    def __repr__(self) -> str:
        """
        Returns the official string representation of the Species object.
        Used primarily for debugging, logging, inspection.
        """
        return f"Species(id={self.id!r}, name{self.name!r}, common_name{self.common_name!r})"
