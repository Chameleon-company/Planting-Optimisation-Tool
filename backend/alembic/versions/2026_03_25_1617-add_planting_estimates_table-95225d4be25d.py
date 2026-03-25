"""add planting_estimates table

Revision ID: 95225d4be25d
Revises: 769fc9c97e25
Create Date: 2026-03-25 16:17:28.402569
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from geoalchemy2 import Geometry

# revision identifiers, used by Alembic.
revision: str = "95225d4be25d"
down_revision: Union[str, Sequence[str], None] = "769fc9c97e25"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create planting_estimates table with spatial index."""

    op.create_table(
        "planting_estimates",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column(
            "farm_id",
            sa.Integer(),
            sa.ForeignKey("farms.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("x_coord", sa.Float(), nullable=False),
        sa.Column("y_coord", sa.Float(), nullable=False),
        sa.Column("slope", sa.Float(), nullable=True),
        sa.Column(
            "geometry",
            Geometry(geometry_type="POINT", srid=4326),
            nullable=False,
        ),
    )

    # Add spatial index
    op.create_index(
        "idx_planting_estimates_geom",
        "planting_estimates",
        ["geometry"],
        postgresql_using="gist",
    )


def downgrade() -> None:
    """Drop planting_estimates table and index safely."""

    # no error if index not exists)
    op.execute("DROP INDEX IF EXISTS idx_planting_estimates_geom")

    op.drop_table("planting_estimates")