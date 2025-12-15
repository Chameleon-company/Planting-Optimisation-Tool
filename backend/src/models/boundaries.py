from sqlalchemy import ForeignKey
from ..database import Base
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship
from geoalchemy2 import Geometry
from .farm import Farm


class FarmBoundary(Base):
    __tablename__ = "boundary"
    # Column names
    id: Mapped[int] = mapped_column(
        ForeignKey("farms.id", ondelete="CASCADE"),
        primary_key=True,
        nullable=False,
    )
    boundary: Mapped[str] = mapped_column(
        Geometry(
            geometry_type="POLYGON",
            srid=4326,
            nullable=False,
        )
    )
    # Relationships
    farm: Mapped["Farm"] = relationship(
        back_populates="boundary",
        # Data is loaded only when the relationship attribute is accessed for the first time.
        # Not required for all operations on a farm so it's kept separate.
        lazy="select",
    )

    def __repr__(self) -> str:
        return f"FarmBoundary(id={self.id!r}, boundary={self.boundary!r})"
