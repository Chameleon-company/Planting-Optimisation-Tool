"""add soil texture spatial table

Revision ID: febd9265a636
Revises: d01f4ba0e99b
Create Date: 2026-04-27 19:00:18.751682

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from geoalchemy2 import Geometry

# revision identifiers, used by Alembic.
revision: str = 'febd9265a636'
down_revision: Union[str, Sequence[str], None] = 'd01f4ba0e99b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    op.create_table(
        "soil_texture_spatial",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("texture", sa.String(length=100), nullable=True),
        sa.Column("source", sa.String(length=100), nullable=True),
        sa.Column(
            "geometry",
            Geometry(
                geometry_type="MULTIPOLYGON", 
                srid=4326,
                spatial_index=False
            ),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_index(
        "idx_soil_texture_spatial_geom",
        "soil_texture_spatial",
        ["geometry"],
        postgresql_using="gist",
    )


def downgrade() -> None:
    """Downgrade schema."""

    op.drop_index("idx_soil_texture_spatial_geom", table_name="soil_texture_spatial")
    op.drop_table("soil_texture_spatial")
