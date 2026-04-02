"""merge waterways migration with existing head

Revision ID: 5f7393003635
Revises: a7c7bc65cef4, 2ab1fb393773
Create Date: 2026-04-01 10:00:00.000000

"""
from typing import Sequence, Union

# revision identifiers, used by Alembic.
revision: str = "5f7393003635"
down_revision: Union[str, Sequence[str], None] = ("a7c7bc65cef4", "2ab1fb393773")
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
