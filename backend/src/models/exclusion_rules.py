# For type hinting only, not runtime
from typing import TYPE_CHECKING, Any

from sqlalchemy import JSON, ForeignKey
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


class SpeciesDependency(Base):
    """Maps focal species to their mandatory biological partners."""

    __tablename__ = "species_dependencies"
    # Column names
    id: Mapped[int] = mapped_column(primary_key=True)

    # The species that has the requirement
    focal_species_id: Mapped[int] = mapped_column(ForeignKey("species.id", ondelete="CASCADE"), nullable=False)

    # The species that must be present
    required_partner_id: Mapped[int] = mapped_column(ForeignKey("species.id", ondelete="CASCADE"), nullable=False)

    # Relationships
    # -------------
    # Links back to the main species table for the focal species
    focal_species: Mapped["Species"] = relationship("Species", foreign_keys=[focal_species_id], back_populates="dependencies")

    # Links to the partner species
    required_partner: Mapped["Species"] = relationship("Species", foreign_keys=[required_partner_id])

    def __repr__(self) -> str:
        return f"Dependency(focal={self.focal_species_id}, partner={self.required_partner_id})"
