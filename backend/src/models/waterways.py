# Waterway table model
# Stores HOT OSM Timor-Leste waterways dataset for riparian zone detection (US-018)
from typing import Optional

import geoalchemy2
from sqlalchemy.orm import Mapped, mapped_column

from src.database import Base


class Waterway(Base):
    __tablename__ = "waterways"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[Optional[str]] = mapped_column(nullable=True)
    waterway: Mapped[Optional[str]] = mapped_column(nullable=True)

    # PostGIS LINESTRING geometry in WGS84 (EPSG:4326)
    geometry: Mapped[object] = mapped_column(
        geoalchemy2.types.Geometry(
            geometry_type="GEOMETRY",
            srid=4326,
            dimension=2,
            spatial_index=False,
            from_text="ST_GeomFromEWKT",
            name="geometry",
            nullable=False,
        ),
        nullable=False,
    )

    def __repr__(self) -> str:
        return f"Waterway(id={self.id!r}, name={self.name!r}, waterway={self.waterway!r})"
