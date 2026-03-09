"""add missing movie columns

Revision ID: b23a4f49a125
Revises: a1b2c3d4e5f6
Create Date: 2026-03-09 23:34:14.992383

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b23a4f49a125'
down_revision: Union[str, None] = 'a1b2c3d4e5f6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add missing columns to movies table
    op.add_column('movies', sa.Column('tmdb_id', sa.Integer(), nullable=True))
    op.add_column('movies', sa.Column('backdrop_url', sa.String(length=500), nullable=True))
    op.add_column('movies', sa.Column('rating', sa.Integer(), nullable=True))
    op.add_column('movies', sa.Column('trailer_key', sa.String(length=50), nullable=True))

    # Create unique index on tmdb_id
    op.create_index(op.f('ix_movies_tmdb_id'), 'movies', ['tmdb_id'], unique=True)


def downgrade() -> None:
    # Drop the index first
    op.drop_index(op.f('ix_movies_tmdb_id'), table_name='movies')

    # Drop columns
    op.drop_column('movies', 'trailer_key')
    op.drop_column('movies', 'rating')
    op.drop_column('movies', 'backdrop_url')
    op.drop_column('movies', 'tmdb_id')
