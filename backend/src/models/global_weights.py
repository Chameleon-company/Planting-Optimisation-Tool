# For type hinting only, not runtime
from typing import TYPE_CHECKING
from uuid import uuid4

from sqlalchemy import DateTime, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from src.database import Base

if TYPE_CHECKING:
    from src.models.global_weights import GlobalWeights


class GlobalWeightsRun(Base):
    __tablename__ = "global_weights_runs"

    id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )

    # Provenance / lifecycle
    created_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    dataset_hash: Mapped[str] = mapped_column(nullable=False)

    # RF bootstrap metadata
    bootstraps: Mapped[int] = mapped_column(nullable=False)
    bootstrap_early_stopped: Mapped[bool] = mapped_column(nullable=False)

    # Optional source info (e.g. Imported from CSV)
    source: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Relationships
    weights: Mapped[list["GlobalWeights"]] = relationship(
        back_populates="run",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"GlobalWeightsRun(id={self.id!r}, created_at={self.created_at!r}, dataset_hash={self.dataset_hash!r})"


class GlobalWeights(Base):
    __tablename__ = "global_weights"

    id: Mapped[int] = mapped_column(primary_key=True)

    # Foreign key to run
    run_id: Mapped[UUID] = mapped_column(
        ForeignKey("global_weights_runs.id", ondelete="CASCADE"),
        nullable=False,
    )

    feature: Mapped[str] = mapped_column(nullable=False)

    # Combined summary
    mean_weight: Mapped[float] = mapped_column(nullable=False)
    ci_lower: Mapped[float] = mapped_column(nullable=False)
    ci_upper: Mapped[float] = mapped_column(nullable=False)

    # Derived / UI helpers
    ci_width: Mapped[float] = mapped_column(nullable=False)
    touches_zero: Mapped[bool] = mapped_column(nullable=False)

    # Relationships
    run: Mapped["GlobalWeightsRun"] = relationship(back_populates="weights")

    def __repr__(self) -> str:
        return f"GlobalWeights(id={self.id!r}, feature={self.feature!r}, mean_weight={self.mean_weight!r})"
