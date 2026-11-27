"""add user is_active

Revision ID: a3f1c9d27b64
Revises: 072333b0bdf6
Create Date: 2026-11-26 12:00:00.000000

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = 'a3f1c9d27b64'
down_revision: Union[str, Sequence[str], None] = '072333b0bdf6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # server_default fills every existing row with true, so no separate backfill
    # is needed and nobody is locked out by this migration.
    op.add_column(
        'users',
        sa.Column('is_active', sa.Boolean(), server_default=sa.text('true'), nullable=False),
    )


def downgrade() -> None:
    op.drop_column('users', 'is_active')
