"""add dem_table

Revision ID: ceabc24ba301
Revises: 95225d4be25d
Create Date: 2026-03-28 12:03:20.322197
"""

from typing import Sequence, Union

from alembic import op

revision: str = "ceabc24ba301"
down_revision: Union[str, Sequence[str], None] = "95225d4be25d"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS postgis;")
    op.execute("CREATE EXTENSION IF NOT EXISTS postgis_raster;")
    
    op.execute(
        """
        CREATE TABLE IF NOT EXISTS dem_table (
            rid SERIAL PRIMARY KEY,
            rast RASTER
        );
        """
    )


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS dem_table;")