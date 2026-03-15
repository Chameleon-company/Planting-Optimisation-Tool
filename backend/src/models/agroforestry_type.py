# Agroforestry types model and references tables
from typing import TYPE_CHECKING

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database import Base
from src.models.association import (
    farm_agroforestry_association,
    species_agroforestry_association,
)

if TYPE_CHECKING:
    from src.models.farm import Farm
    from src.models.species import Species


class AgroforestryType(Base):
    __tablename__ = "agroforestry_types"
    # Column names
    id: Mapped[int] = mapped_column(primary_key=True)
    type_name: Mapped[str] = mapped_column(String(15), unique=True)

    # Relationships
    # -------------
    # Links an AgroforestryType object back to a Farm object
    farms: Mapped[list["Farm"]] = relationship(secondary=farm_agroforestry_association, back_populates="agroforestry_type")

    # Links an AgroforestryType object back to a Farm object
    species_agroforestry_type: Mapped[list["Species"]] = relationship(secondary=species_agroforestry_association, back_populates="agroforestry_types")

    def __repr__(self) -> str:
        """Returns the official string representation of the Agroforestry_types object.
        Used primarily for debugging, logging, inspection.
        """
        return f"Agroforestry_types(id={self.id!r}, type{self.type_name!r})"
