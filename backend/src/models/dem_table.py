from geoalchemy2 import Raster
from sqlalchemy.orm import Mapped, mapped_column

from src.database import Base


class DemTable(Base):
    __tablename__ = "dem_table"

    rid: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    rast: Mapped[bytes | None] = mapped_column(Raster, nullable=True)

    def __repr__(self) -> str:
        return f"DemTable(rid={self.rid!r})"
