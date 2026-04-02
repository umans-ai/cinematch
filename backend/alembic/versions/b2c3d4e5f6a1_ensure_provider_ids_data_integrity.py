"""ensure provider_ids data integrity

Revision ID: b2c3d4e5f6a1
Revises: a1b2c3d4e5f7
Create Date: 2026-04-02 23:18:41.422253

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b2c3d4e5f6a1'
down_revision: Union[str, None] = 'a1b2c3d4e5f7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Ensure all rooms have valid provider_ids as non-empty JSON array."""
    conn = op.get_bind()
    dialect = conn.dialect.name

    if dialect == "postgresql":
        # For PostgreSQL: use jsonb for safe comparison
        # Handle NULL, JSON null, empty array, or invalid values
        op.execute(
            sa.text("""
                UPDATE rooms
                SET provider_ids = COALESCE(
                    NULLIF(provider_ids::jsonb, 'null'::jsonb),
                    '[8]'::jsonb
                )
                WHERE provider_ids IS NULL
                   OR provider_ids::jsonb = 'null'::jsonb
                   OR provider_ids::jsonb = '[]'::jsonb
                   OR jsonb_array_length(COALESCE(provider_ids::jsonb, '[]'::jsonb)) = 0
            """)
        )

        # Also ensure any room with NULL provider_id gets a default
        op.execute(
            sa.text("""
                UPDATE rooms
                SET provider_ids = '[8]'::jsonb
                WHERE provider_ids IS NULL
                   OR provider_ids::jsonb = 'null'::jsonb
            """)
        )
    else:
        # For SQLite: simpler NULL and 'null' string checks
        op.execute(
            sa.text("""
                UPDATE rooms
                SET provider_ids = '[8]'
                WHERE provider_ids IS NULL
                   OR provider_ids = 'null'
                   OR provider_ids = '[]'
                   OR provider_ids = ''
            """)
        )


def downgrade() -> None:
    pass
