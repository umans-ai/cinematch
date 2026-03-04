"""Fix participant session_id unique constraint

Revision ID: a1b2c3d4e5f6
Revises: cdc82f99bace
Create Date: 2026-03-04 00:00:00.000000

Drop the global unique constraint on session_id and replace it with a
composite unique constraint on (room_id, session_id), allowing a user
to participate in multiple rooms with the same session.
"""
from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, None] = 'cdc82f99bace'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_constraint('participants_session_id_key', 'participants', type_='unique')
    op.create_unique_constraint(
        'uq_participants_room_id_session_id',
        'participants',
        ['room_id', 'session_id'],
    )


def downgrade() -> None:
    op.drop_constraint('uq_participants_room_id_session_id', 'participants', type_='unique')
    op.create_unique_constraint('participants_session_id_key', 'participants', ['session_id'])
