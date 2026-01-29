from sqlalchemy import ForeignKey, Float, Integer, String, DateTime, func
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.database import Base
from datetime import datetime
from src.models.farm import Farm
from src.models.species import Species


class Recommendation(Base):
    __tablename__ = "recommendations"

    id: Mapped[int] = mapped_column(primary_key=True)

    farm_id: Mapped[int] = mapped_column(
        ForeignKey("farms.id", ondelete="CASCADE"), nullable=False
    )

    species_id: Mapped[int] = mapped_column(
        ForeignKey("species.id", ondelete="CASCADE"), nullable=False
    )

    rank_overall: Mapped[int] = mapped_column(Integer, nullable=False)

    score_mcda: Mapped[float] = mapped_column(Float, nullable=False)

    # Using PostgreSQL ARRAY of Strings for the diagnostic messages
    key_reasons: Mapped[list[str]] = mapped_column(ARRAY(String), nullable=False)

    # timestamp
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    # Relationships
    farm: Mapped["Farm"] = relationship(back_populates="recommendations")
    species: Mapped["Species"] = relationship()

    def __repr__(self) -> str:
        return f"Recommendation(farm={self.farm_id}, species={self.species_id}, rank={self.rank_overall})"
