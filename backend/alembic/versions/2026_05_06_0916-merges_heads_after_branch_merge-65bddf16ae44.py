"""merges heads after branch merge

Revision ID: 65bddf16ae44
Revises: 076b5e30a1a2, aee157e85e9c
Create Date: 2026-05-06 09:16:04.270460

"""
from typing import Sequence, Union

# revision identifiers, used by Alembic.
revision: str = '65bddf16ae44'
down_revision: Union[str, Sequence[str], None] = ('076b5e30a1a2', 'aee157e85e9c')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
