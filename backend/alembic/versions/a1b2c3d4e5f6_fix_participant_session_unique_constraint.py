"""Fix participant session_id unique constraint to be composite with room_id

Revision ID: a1b2c3d4e5f6
Revises: cdc82f99bace
Create Date: 2026-03-04 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, None] = 'cdc82f99bace'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Drop the global unique constraint on session_id
    with op.batch_alter_table('participants') as batch_op:
        batch_op.drop_constraint('uq_participants_session_id', type_='unique')
        batch_op.create_unique_constraint(
            'uq_participants_room_session',
            ['room_id', 'session_id']
        )


def downgrade() -> None:
    with op.batch_alter_table('participants') as batch_op:
        batch_op.drop_constraint('uq_participants_room_session', type_='unique')
        batch_op.create_unique_constraint(
            'uq_participants_session_id',
            ['session_id']
        )
