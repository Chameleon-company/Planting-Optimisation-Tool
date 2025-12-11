# Farm table model and reference tables
from sqlalchemy import ForeignKey
from ..database import Base
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship
from .association import farm_agroforestry_association

# For type hinting only, not runtime
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .soil_texture import SoilTexture
    from .agroforestry_type import AgroforestryType


class Farm(Base):
    __tablename__ = "farms"
    # Column names
    id: Mapped[int] = mapped_column(primary_key=True)

    rainfall_mm: Mapped[int] = mapped_column()
    temperature_celsius: Mapped[int] = mapped_column()
    elevation_m: Mapped[int] = mapped_column()
    ph: Mapped[float] = mapped_column()  # 1 decimal point, enforced by Pydantic model
    soil_texture_id: Mapped[int] = mapped_column(
        ForeignKey("soil_textures.id", ondelete="CASCADE")
    )
    area_ha: Mapped[float] = mapped_column()  # 3 decimal points
    latitude: Mapped[float] = mapped_column()  # 5 decimal points
    longitude: Mapped[float] = mapped_column()  # 5 decimal points
    coastal: Mapped[bool] = mapped_column()
    riparian: Mapped[bool] = mapped_column()
    nitrogen_fixing: Mapped[bool] = mapped_column()
    shade_tolerant: Mapped[bool] = mapped_column()
    bank_stabilising: Mapped[bool] = mapped_column()
    slope: Mapped[float] = mapped_column()

    # Relationships
    # -------------
    # Links a Farm object to its corresponding SoilTexture object
    soil_texture: Mapped["SoilTexture"] = relationship(back_populates="farms")
    # Links a Farm object to a list of AgroforestryType objects (M:M)
    agroforestry_type: Mapped[list["AgroforestryType"]] = relationship(
        secondary=farm_agroforestry_association, back_populates="farms"
    )

    def __repr__(self) -> str:
        """
        Returns the official string representation of the Farm object.
        Used primarily for debugging, logging, inspection.
        """
        return f"Farms(id={self.id!r}, rainfall_mm{self.rainfall_mm!r}, temp_c{self.temperature_celsius!r})"
