# Soil texture reference table
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .farm import Farm
    from .species import Species
from sqlalchemy import String
from ..database import Base
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship


class SoilTexture(Base):
    __tablename__ = "soil_textures"
    # Column names
    id: Mapped[int] = mapped_column(primary_key=True)
    texture_name: Mapped[str] = mapped_column(String(15), unique=True)

    # Relationships
    # -------------
    # Links a SoilTexture object back to the Farm objects
    farms: Mapped[list["Farm"]] = relationship(back_populates="soil_texture")

    soil_textures_for_species: Mapped[list["Species"]] = relationship(
        secondary="species_soil_texture_association", back_populates="soil_textures"
    )

    def __repr__(self) -> str:
        """
        Returns the official string representation of the Agroforestry_types object.
        Used primarily for debugging, logging, inspection.
        """
        return f"soil_textures(id={self.id!r}, type{self.texture_name!r})"
