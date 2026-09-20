"""enable pg_trgm for farm name search

Revision ID: 072333b0bdf6
Revises: 96453af1fe22
Create Date: 2026-09-16 15:23:35.689169

"""
from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = '072333b0bdf6'
down_revision: Union[str, Sequence[str], None] = '96453af1fe22'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS pg_trgm")
    # optional but cheap — makes fuzzy search index-backed:
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_farms_name_trgm "
        "ON farms USING gin (name gin_trgm_ops)"
    )

def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS ix_farms_name_trgm")
    op.execute("DROP EXTENSION IF EXISTS pg_trgm")