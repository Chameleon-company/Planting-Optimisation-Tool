"""merge dem_table migration with existing head

Revision ID: 2ab1fb393773
Revises: ceabc24ba301, 2d5aae317afd
Create Date: 2026-03-30 14:16:36.271523

"""
from typing import Sequence, Union

# revision identifiers, used by Alembic.
revision: str = '2ab1fb393773'
down_revision: Union[str, Sequence[str], None] = ('ceabc24ba301', '2d5aae317afd')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
