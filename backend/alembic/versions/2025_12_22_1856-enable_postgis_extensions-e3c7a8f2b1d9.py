"""Enable PostGIS extensions

Revision ID: e3c7a8f2b1d9
Revises:
Create Date: 2025-12-22 18:56:00.000000

"""
from alembic import op

revision: str = 'e3c7a8f2b1d9'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS postgis")
    op.execute("CREATE EXTENSION IF NOT EXISTS postgis_raster")


def downgrade() -> None:
    pass