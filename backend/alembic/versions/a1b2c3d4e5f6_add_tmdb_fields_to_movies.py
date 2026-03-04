"""add tmdb fields to movies

Revision ID: a1b2c3d4e5f6
Revises: cdc82f99bace
Create Date: 2026-03-04 00:00:00.000000

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "a1b2c3d4e5f6"
down_revision: Union[str, None] = "cdc82f99bace"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("movies", sa.Column("tmdb_id", sa.Integer(), nullable=True))
    op.add_column("movies", sa.Column("poster_path", sa.String(500), nullable=True))
    op.add_column("movies", sa.Column("backdrop_path", sa.String(500), nullable=True))
    op.add_column("movies", sa.Column("overview", sa.Text(), nullable=True))
    op.add_column("movies", sa.Column("vote_average", sa.Float(), nullable=True))
    op.add_column("movies", sa.Column("trailer_key", sa.String(100), nullable=True))
    op.add_column("movies", sa.Column("popularity", sa.Float(), nullable=True))
    op.add_column("movies", sa.Column("cached_at", sa.DateTime(timezone=True), nullable=True))
    op.create_index(op.f("ix_movies_tmdb_id"), "movies", ["tmdb_id"], unique=True)


def downgrade() -> None:
    op.drop_index(op.f("ix_movies_tmdb_id"), table_name="movies")
    op.drop_column("movies", "cached_at")
    op.drop_column("movies", "popularity")
    op.drop_column("movies", "trailer_key")
    op.drop_column("movies", "vote_average")
    op.drop_column("movies", "overview")
    op.drop_column("movies", "backdrop_path")
    op.drop_column("movies", "poster_path")
    op.drop_column("movies", "tmdb_id")
