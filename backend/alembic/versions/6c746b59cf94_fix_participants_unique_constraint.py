"""fix_participants_unique_constraint

Revision ID: 6c746b59cf94
Revises: b23a4f49a125
Create Date: 2026-03-17 13:59:15.458100

"""
from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = '6c746b59cf94'
down_revision: Union[str, None] = 'b23a4f49a125'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Fix participants unique constraint from global to composite.

    Changes from UNIQUE(session_id) to UNIQUE(room_id, session_id)
    allowing users to join multiple rooms with the same browser session.

    Note: This migration targets PostgreSQL (production). SQLite uses
    Base.metadata.create_all() which already creates the correct schema.
    """
    # Drop the old global unique constraint on session_id
    op.drop_constraint('participants_session_id_key', 'participants', type_='unique')

    # Create the new composite unique constraint
    op.create_unique_constraint(
        'uq_participants_room_session',
        'participants',
        ['room_id', 'session_id']
    )


def downgrade() -> None:
    """Revert to global unique constraint on session_id."""
    # Drop the composite constraint
    op.drop_constraint('uq_participants_room_session', 'participants', type_='unique')

    # Recreate the global unique constraint
    op.create_unique_constraint(
        'participants_session_id_key',
        'participants',
        ['session_id']
    )
