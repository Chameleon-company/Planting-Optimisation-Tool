"""create waterways table

Revision ID: a7c7bc65cef4
Revises: 769fc9c97e25
Create Date: 2026-03-29 23:52:31.223745

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import geoalchemy2

# revision identifiers, used by Alembic.
revision: str = 'a7c7bc65cef4'
down_revision: Union[str, Sequence[str], None] = '2d5aae317afd'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
    'waterways',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(), nullable=True),
    sa.Column('waterway', sa.String(), nullable=True), 
    sa.Column(
        'geometry',
        geoalchemy2.types.Geometry(
            geometry_type='GEOMETRY',
            srid=4326,
            dimension=2,
            spatial_index=False,
            from_text='ST_GeomFromEWKT',
            name='geometry',
            nullable=False,
        ),
        nullable=False,
    ),
    sa.PrimaryKeyConstraint('id'),
)
    
    op.create_index(
        'idx_waterways_geometry',
        'waterways',
        ['geometry'],
        postgresql_using='gist',
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index('idx_waterways_geometry', table_name='waterways')
    op.drop_table('waterways')
