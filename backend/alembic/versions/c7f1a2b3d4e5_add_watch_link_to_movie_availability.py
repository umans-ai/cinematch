"""Add watch link to movie availability

Revision ID: c7f1a2b3d4e5
Revises: b2c3d4e5f6a1
Create Date: 2026-07-01

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c7f1a2b3d4e5'
down_revision: Union[str, None] = 'b2c3d4e5f6a1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        'movie_availabilities',
        sa.Column('link', sa.String(length=500), nullable=True),
    )


def downgrade() -> None:
    op.drop_column('movie_availabilities', 'link')
