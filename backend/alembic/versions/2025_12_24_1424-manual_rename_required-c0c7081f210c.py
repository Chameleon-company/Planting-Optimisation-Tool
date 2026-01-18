"""MANUAL_RENAME_REQUIRED

Revision ID: c0c7081f210c
Revises: a21b8babef99
Create Date: 2025-12-24 14:24:22.201558

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c0c7081f210c'
down_revision: Union[str, Sequence[str], None] = 'a21b8babef99'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
