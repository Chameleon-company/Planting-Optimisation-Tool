# Farm table model and reference tables
from typing import Optional
from sqlalchemy import ForeignKey
from sqlalchemy import Boolean, text, Integer
from src.database import Base
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship
from src.models.association import farm_agroforestry_association

# For type hinting only, not runtime
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.models.soil_texture import SoilTexture
    from src.models.agroforestry_type import AgroforestryType
    from src.models.boundaries import FarmBoundary
    from src.models.user import User
    from src.models.recommendations import Recommendation


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
    coastal: Mapped[bool] = mapped_column(
        Boolean, default=False, server_default=text("false")
    )
    riparian: Mapped[bool] = mapped_column(
        Boolean, default=False, server_default=text("false")
    )
    nitrogen_fixing: Mapped[bool] = mapped_column(
        Boolean, default=False, server_default=text("false")
    )
    shade_tolerant: Mapped[bool] = mapped_column(
        Boolean, default=False, server_default=text("false")
    )
    bank_stabilising: Mapped[bool] = mapped_column(
        Boolean, default=False, server_default=text("false")
    )
    slope: Mapped[float] = mapped_column()  # 2 decimal points
    user_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE")
    )
    external_id: Mapped[int | None] = mapped_column(
        Integer, unique=True, nullable=True, default=None
    )

    # Relationships
    # -------------
    # Links a Farm object to its corresponding SoilTexture object (1:1)
    soil_texture: Mapped["SoilTexture"] = relationship(back_populates="farms")

    # Links a Farm object to a list of AgroforestryType objects (M:M)
    agroforestry_type: Mapped[list["AgroforestryType"]] = relationship(
        secondary=farm_agroforestry_association, back_populates="farms"
    )
    # Links the farm to it's boundary Polygon entry in the boundary table
    boundary: Mapped["FarmBoundary"] = relationship(
        back_populates="farm",
        uselist=False,  # Apparently critical for 1:1
        cascade="all, delete-orphan",
    )

    recommendations: Mapped[list["Recommendation"]] = relationship(
        back_populates="farm", cascade="all, delete-orphan"
    )

    # Links farm owner/user to farm (1:1)
    farm_supervisor: Mapped["User"] = relationship(back_populates="farms")

    def __repr__(self) -> str:
        """
        Returns the official string representation of the Farm object.
        Used primarily for debugging, logging, inspection.
        """
        return f"Farms(id={self.id!r}, rainfall_mm{self.rainfall_mm!r}, temp_c{self.temperature_celsius!r})"
