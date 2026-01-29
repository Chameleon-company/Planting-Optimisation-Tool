# Species parameters table model and reference tables
from sqlalchemy import ForeignKey
from src.database import Base
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship

# For type hinting only, not runtime
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.models.species import Species


class Parameter(Base):
    __tablename__ = "parameters"
    # Column names
    id: Mapped[int] = mapped_column(primary_key=True)

    species_id: Mapped[int] = mapped_column(
        ForeignKey("species.id", ondelete="CASCADE")
    )
    feature: Mapped[str] = mapped_column()
    score_method: Mapped[str] = mapped_column(nullable=True)
    weight: Mapped[float | None] = mapped_column(nullable=True)
    trap_left_tol: Mapped[float | None] = mapped_column(nullable=True)
    trap_right_tol: Mapped[float | None] = mapped_column(nullable=True)

    # Relationships
    # -------------
    # Species ID links back to species
    species: Mapped["Species"] = relationship(back_populates="parameters")

    def __repr__(self) -> str:
        """
        Returns the official string representation of the Parameter object.
        Used primarily for debugging, logging, inspection.
        """
        return f"Parameter(id={self.id!r}, name{self.species_id!r}, common_name{self.feature!r})"
