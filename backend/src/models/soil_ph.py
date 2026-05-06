from geoalchemy2 import Geometry
from sqlalchemy import Float, Index, String
from sqlalchemy.orm import Mapped, mapped_column

from src.database import Base


class SoilPH(Base):
    __tablename__ = "soil_ph"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    ph: Mapped[float | None] = mapped_column(Float, nullable=True)
    source: Mapped[str | None] = mapped_column(String(100), nullable=True)

    geometry: Mapped[str] = mapped_column(
        Geometry(geometry_type="MULTIPOLYGON", srid=4326),
        nullable=False,
    )

    __table_args__ = (Index("idx_soil_ph_geometry", "geometry", postgresql_using="gist"),)
