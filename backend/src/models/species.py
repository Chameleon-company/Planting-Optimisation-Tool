# Species table model and references tables
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

class Species(Base):
    __tablename__ = "species"
    # Column names
    id: Mapped[int] = mapped_column(primary_key=True)
    
    name: Mapped[str] = mapped_column()
    common_name: Mapped[str] = mapped_column()
    min_rainfall_mm: Mapped[int] = mapped_column() 
    max_rainfall_mm: Mapped[int] = mapped_column() 
    min_temp_c: Mapped[int] = mapped_column()  
    max_temp_c: Mapped[int] = mapped_column() 
    min_elevation_m: Mapped[int] = mapped_column()
    max_elevation_m: Mapped[int] = mapped_column()
    min_ph: Mapped[float] = mapped_column() # 1 decimal
    max_ph: Mapped[float] = mapped_column() # 1 decimal
    preferred_soil_texture: Mapped[int] = mapped_column(ForeignKey('soil_texture.id')) 
    coastal: Mapped[bool] = mapped_column() 
    riparian: Mapped[bool] = mapped_column() 
    nitrogen_fixing: Mapped[bool] = mapped_column() 
    shade_tolerant: Mapped[bool] = mapped_column() 
    bank_stabilising: Mapped[bool] = mapped_column()
    agroforestry_type_id: Mapped[int] = mapped_column(ForeignKey('agroforestry_types.id'))

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