# Farm table model and reference tables

# from sqlalchemy import ForeignKey
from ..database import Base
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column

# from sqlalchemy.orm import relationship
from geoalchemy2 import Geometry


class FarmBoundary(Base):
    __tablename__ = "boundary"
    # Column names
    id: Mapped[int] = mapped_column(primary_key=True)
    boundary: Mapped[str] = mapped_column(
        Geometry(
            geometry_type="POLYGON",
            srid=4326,
            nullable=False,
        )
    )
