from geoalchemy2 import Geometry
from sqlalchemy import Float, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from src.database import Base


class PlantingEstimate(Base):
    __tablename__ = "planting_estimates"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    farm_id: Mapped[int] = mapped_column(
        ForeignKey("farms.id", ondelete="CASCADE"),
        nullable=False,
    )

    slope: Mapped[float | None] = mapped_column(Float, nullable=True)

    geometry: Mapped[str] = mapped_column(
        Geometry(geometry_type="POINT", srid=4326),
        nullable=False,
    )

    def __repr__(self):
        return f"PlantingEstimate(id={self.id}, farm_id={self.farm_id})"
