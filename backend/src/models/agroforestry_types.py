# Agroforestry types model and references tables
'''
Unused for now, but may be used later after other parts are built.

from typing import List
from typing import Optional
from sqlalchemy import String
'''

from sqlalchemy import ForeignKey
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship

class Base(DeclarativeBase):
    pass

class Agroforestry_types(Base):
    __tablename__ = "agroforestry_types"
    # Column names
    id: Mapped[int] = mapped_column(primary_key=True)
    type: Mapped[str] = mapped_column()

    # Relationships
    # -------------
    # Links a species object to its corresponding soil_texture object
    soil_texture: Mapped["SoilTexture"] = relationship(
        back_populates="species_with_this_preffered_texture"
    )
    # Links a species object to its corresponding agroforestry_type object
    agroforestry_type: Mapped["AgroforestryType"] = relationship(
        back_populates="species_with_this_type")

    def __repr__(self) -> str:
        """
        Returns the official string representation of the Species object. 
        Used primarily for debugging, logging, inspection.
        """
        return f"Species(id={self.id!r}, name{self.name!r}, common_name{self.common_name!r})"