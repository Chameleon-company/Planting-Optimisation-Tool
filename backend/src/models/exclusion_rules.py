# For type hinting only, not runtime
from typing import TYPE_CHECKING, Any

from sqlalchemy import ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database import Base

if TYPE_CHECKING:
    from src.models.species import Species


class SpeciesExclusionRule(Base):
    __tablename__ = "species_exclusion_rules"
    # Column names
    id: Mapped[int] = mapped_column(primary_key=True)

    species_id: Mapped[int] = mapped_column(ForeignKey("species.id", ondelete="CASCADE"))

    # Matches FarmRead attributes: 'ph', 'rainfall_mm', 'soil_texture'
    feature: Mapped[str] = mapped_column()

    # Matches logic: '<', '>', '==', 'in_set', etc.
    operator: Mapped[str] = mapped_column()

    # JSON type allows for float (6.0), string ("clay"), or list (["clay", "loam"])
    value: Mapped[Any] = mapped_column(JSON)

    # The narrative reason: "altitude is more than 1300m"
    reason: Mapped[str] = mapped_column()

    # Relationships
    # -------------
    # Species ID links back to species
    species: Mapped["Species"] = relationship(back_populates="exclusion_rules")

    def __repr__(self) -> str:
        """Official string representation for debugging."""
        return f"ExclusionRule(id={self.id!r}, species_id={self.species_id!r}, feature={self.feature!r}, op={self.operator!r})"
