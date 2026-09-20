"""add farm_owners join table and farm name column

Revision ID: 2b55f7b03139
Revises: 56260d49e7ae
Create Date: 2026-09-01 15:49:24.743367

"""
from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = '2b55f7b03139'
down_revision: Union[str, Sequence[str], None] = '56260d49e7ae'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Create the new many-to-many join table first
    op.create_table('farm_owners',
    sa.Column('farm_id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['farm_id'], ['farms.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('farm_id', 'user_id')
    )

    # Add the new name column
    op.add_column('farms', sa.Column('name', sa.String(), nullable=True))

    # Backfill: copy every existing farm -> user_id link into farm_owners
    # BEFORE dropping the old column, so no ownership data is lost.
    op.execute(
        """
        INSERT INTO farm_owners (farm_id, user_id)
        SELECT id, user_id FROM farms WHERE user_id IS NOT NULL
        """
    )

    # Now safe to remove the old single-owner column
    op.drop_constraint(op.f('farms_user_id_fkey'), 'farms', type_='foreignkey')
    op.drop_column('farms', 'user_id')


def downgrade() -> None:
    """Downgrade schema."""
    # Recreate the old single-owner column
    op.add_column('farms', sa.Column('user_id', sa.INTEGER(), autoincrement=False, nullable=True))
    op.create_foreign_key(op.f('farms_user_id_fkey'), 'farms', 'users', ['user_id'], ['id'], ondelete='CASCADE')

    # Best-effort backfill back to 1:1: picks one arbitrary owner per farm
    # if a farm had multiple owners under the new schema. This IS lossy —
    # any farm with more than one owner will only keep one on downgrade.
    op.execute(
        """
        UPDATE farms
        SET user_id = fo.user_id
        FROM (
            SELECT DISTINCT ON (farm_id) farm_id, user_id
            FROM farm_owners
            ORDER BY farm_id, user_id
        ) fo
        WHERE farms.id = fo.farm_id
        """
    )

    op.drop_column('farms', 'name')
    op.drop_table('farm_owners')