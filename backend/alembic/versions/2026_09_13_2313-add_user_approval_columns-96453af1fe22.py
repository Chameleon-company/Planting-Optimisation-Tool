"""add user approval columns

Revision ID: 96453af1fe22
Revises: 2b55f7b03139
Create Date: 2026-09-13 23:13:31.791875

"""
from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = '96453af1fe22'
down_revision: Union[str, Sequence[str], None] = '2b55f7b03139'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    """Upgrade schema."""
    # requested_role is nullable, so it can be added as-is with no backfill.
    op.add_column('users', sa.Column('requested_role', sa.String(length=50), nullable=True))

    # Add is_approved as NULLABLE first
    op.add_column('users', sa.Column('is_approved', sa.Boolean(), nullable=True))

    # Backfill: every user who already exists predates the approval gate, so
    # grandfather them all in as approved
    op.execute("UPDATE users SET is_approved = true")

    # Now that every row has a value, enforce NOT NULL and set the DB-level default
    # so future inserts default to unapproved.
    op.alter_column(
        'users',
        'is_approved',
        nullable=False,
        server_default=sa.text('false'),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('users', 'is_approved')
    op.drop_column('users', 'requested_role')
