"""merge heads

Revision ID: 076b5e30a1a2
Revises: f4746a1d68d7, febd9265a636
Create Date: 2026-04-29 01:25:38.962680

"""
from typing import Sequence, Union

# revision identifiers, used by Alembic.
revision: str = '076b5e30a1a2'
down_revision: Union[str, Sequence[str], None] = ('f4746a1d68d7', 'febd9265a636')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
