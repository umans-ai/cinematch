"""Add TMDB fields to movies and tmdb_cache table

Revision ID: a1b2c3d4e5f6
Revises: cdc82f99bace
Create Date: 2026-03-04 00:00:00.000000

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "a1b2c3d4e5f6"
down_revision: Union[str, None] = "cdc82f99bace"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("movies", sa.Column("tmdb_id", sa.Integer(), nullable=True))
    op.add_column("movies", sa.Column("poster_path", sa.String(length=500), nullable=True))
    op.add_column("movies", sa.Column("backdrop_path", sa.String(length=500), nullable=True))
    op.add_column("movies", sa.Column("imdb_rating", sa.Float(), nullable=True))
    op.add_column("movies", sa.Column("trailer_key", sa.String(length=100), nullable=True))
    op.create_index(op.f("ix_movies_tmdb_id"), "movies", ["tmdb_id"], unique=True)

    op.create_table(
        "tmdb_cache",
        sa.Column("key", sa.String(length=200), nullable=False),
        sa.Column("data", sa.Text(), nullable=False),
        sa.Column("cached_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("key"),
    )


def downgrade() -> None:
    op.drop_table("tmdb_cache")
    op.drop_index(op.f("ix_movies_tmdb_id"), table_name="movies")
    op.drop_column("movies", "trailer_key")
    op.drop_column("movies", "imdb_rating")
    op.drop_column("movies", "backdrop_path")
    op.drop_column("movies", "poster_path")
    op.drop_column("movies", "tmdb_id")
