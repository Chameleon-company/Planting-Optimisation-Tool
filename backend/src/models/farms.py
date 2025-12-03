# Farm table model and reference tables

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

class Farm(Base):
    __tablename__ = "farms"
    # Column names
    id: Mapped[int] = mapped_column(primary_key=True)
    
    rainfall_mm: Mapped[int] = mapped_column()
    temp_c: Mapped[int] = mapped_column() 
    elevation_m: Mapped[int] = mapped_column() 
    soil_ph: Mapped[float] = mapped_column() # 1 decimal point, enforced by Pydantic model 
    soil_texture_id: Mapped[int] = mapped_column(ForeignKey('soil_texture.id')) 
    area_ha: Mapped[float] = mapped_column() # 3 decimal points 
    latitude: Mapped[float] = mapped_column() # 5 decimal points
    longitude: Mapped[float] = mapped_column() # 5 decimal points
    coastal: Mapped[bool] = mapped_column() 
    riparian: Mapped[bool] = mapped_column() 
    nitrogen_fixing: Mapped[bool] = mapped_column() 
    shade_tolerant: Mapped[bool] = mapped_column() 
    bank_stabilising: Mapped[bool] = mapped_column() 
    agroforestry_type_id: Mapped[int] = mapped_column(ForeignKey('agroforestry_types.id')) 

    # Relationships
    # -------------
    # Links a farm object to its corresponding soil_texture object
    soil_texture: Mapped["SoilTexture"] = relationship(
        back_populates='farms_with_this_texture'
    )
    # Links a farm object to its corresponding agroforestry_type object
    agroforestry_type: Mapped["AgroforestryType"] = relationship(
    back_populates="farms_with_this_type")

    def __repr__(self) -> str:
        """
        Returns the official string representation of the Farm object. 
        Used primarily for debugging, logging, inspection.
        """
        return f"Farms(id={self.id!r}, rainfall_mm{self.rainfall_mm!r}, temp_c{self.temp_c!r})"