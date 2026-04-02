"""Fix provider_ids data for existing rooms

Revision ID: 6e49429586cd
Revises: 81f153f63751
Create Date: 2026-04-02 22:49:49.133851

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '6e49429586cd'
down_revision: Union[str, None] = '81f153f63751'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Ensure all rooms have valid provider_ids."""
    conn = op.get_bind()
    dialect = conn.dialect.name

    if dialect == "postgresql":
        # For PostgreSQL: ensure provider_ids is set correctly
        # This fixes any rooms where provider_ids might be null or invalid
        # Use json_typeof to check for null JSON values (json = json comparison not supported)
        op.execute(
            sa.text("""
                UPDATE rooms
                SET provider_ids = json_build_array(provider_id)
                WHERE provider_ids IS NULL OR json_typeof(provider_ids) = 'null'
            """)
        )
    else:
        # For SQLite
        op.execute(
            sa.text("""
                UPDATE rooms
                SET provider_ids = json_array(provider_id)
                WHERE provider_ids IS NULL
            """)
        )


def downgrade() -> None:
    pass
