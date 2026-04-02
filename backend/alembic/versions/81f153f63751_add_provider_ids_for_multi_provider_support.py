"""Add provider_ids for multi-provider support

Revision ID: 81f153f63751
Revises: 6c746b59cf94
Create Date: 2026-04-02 14:00:00.000000

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy import text
from sqlalchemy.dialects import postgresql, sqlite

# revision identifiers, used by Alembic.
revision: str = "81f153f63751"
down_revision: Union[str, None] = "6c746b59cf94"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add provider_ids JSON column and migrate data from provider_id."""
    # Get database connection
    conn = op.get_bind()
    dialect = conn.dialect.name

    # Add provider_ids column as JSON
    if dialect == "postgresql":
        # PostgreSQL has native JSON support
        op.add_column(
            "rooms",
            sa.Column(
                "provider_ids",
                postgresql.JSON,
                server_default="[8]",
                nullable=False,
            ),
        )
    else:
        # SQLite uses JSON type
        op.add_column(
            "rooms",
            sa.Column(
                "provider_ids",
                sa.JSON,
                server_default=sa.text("'[8]'"),
                nullable=False,
            ),
        )

    # Migrate existing data: convert provider_id to JSON array
    if dialect == "postgresql":
        # PostgreSQL uses json_build_array
        op.execute(
            text(
                """
            UPDATE rooms
            SET provider_ids = CASE
                WHEN provider_id IS NOT NULL THEN json_build_array(provider_id)
                ELSE '[8]'::json
            END
            """
            )
        )
    else:
        # SQLite uses json_array
        op.execute(
            text(
                """
            UPDATE rooms
            SET provider_ids = CASE
                WHEN provider_id IS NOT NULL THEN json_array(provider_id)
                ELSE '[8]'
            END
            """
            )
        )


def downgrade() -> None:
    """Remove provider_ids column."""
    op.drop_column("rooms", "provider_ids")
