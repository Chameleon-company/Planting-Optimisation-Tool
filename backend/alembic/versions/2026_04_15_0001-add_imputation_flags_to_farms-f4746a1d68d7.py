"""add imputation flags to farms

Revision ID: a1b2c3d4e5f6
Revises: 2c230e5a4440
Create Date: 2026-04-15 00:01:00.000000

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "f4746a1d68d7"
down_revision: Union[str, None] = "2c230e5a4440"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

_COLUMNS = [
    "elevation_m_imputed",
    "slope_imputed",
    "temperature_celsius_imputed",
    "rainfall_mm_imputed",
    "ph_imputed",
]


def upgrade() -> None:
    for col in _COLUMNS:
        op.add_column(
            "farms",
            sa.Column(col, sa.Boolean(), nullable=False, server_default=sa.text("false")),
        )


def downgrade() -> None:
    for col in _COLUMNS:
        op.drop_column("farms", col)
