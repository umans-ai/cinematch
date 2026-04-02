"""fix provider_ids json handling in postgresql

Revision ID: a1b2c3d4e5f7
Revises: 6e49429586cd
Create Date: 2026-04-02 23:12:52.148370

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a1b2c3d4e5f7'
down_revision: Union[str, None] = '6e49429586cd'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Ensure all rooms have valid provider_ids JSON array."""
    conn = op.get_bind()
    dialect = conn.dialect.name

    if dialect == "postgresql":
        # For PostgreSQL: fix any invalid provider_ids values
        # Handle both NULL and the JSON null value
        # Use jsonb to check for null JSON values since json = json comparison not supported
        op.execute(
            sa.text("""
                UPDATE rooms
                SET provider_ids = to_jsonb(COALESCE(json_build_array(provider_id), '[8]'::json))
                WHERE provider_ids IS NULL
                   OR provider_ids::jsonb = 'null'::jsonb
                   OR jsonb_array_length(COALESCE(provider_ids::jsonb, '[]'::jsonb)) = 0
            """)
        )
    else:
        # For SQLite
        op.execute(
            sa.text("""
                UPDATE rooms
                SET provider_ids = json_array(COALESCE(provider_id, 8))
                WHERE provider_ids IS NULL
                   OR provider_ids = 'null'
                   OR provider_ids = '[]'
            """)
        )


def downgrade() -> None:
    pass
