"""add soil ph table

Revision ID: d01f4ba0e99b
Revises: 2c230e5a4440
Create Date: 2026-04-24 16:33:25.480484

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from geoalchemy2 import Geometry

# revision identifiers, used by Alembic.
revision: str = 'd01f4ba0e99b'
down_revision: Union[str, Sequence[str], None] = '2c230e5a4440'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "soil_ph",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("ph", sa.Float(), nullable=True),
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
    )

    op.create_index(
        "idx_soil_ph_geometry",
        "soil_ph",
        ["geometry"],
        postgresql_using="gist",
    )


def downgrade() -> None:
    op.drop_index("idx_soil_ph_geometry", table_name="soil_ph")
    op.drop_table("soil_ph")
