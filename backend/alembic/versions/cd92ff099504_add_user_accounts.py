"""add user accounts

Revision ID: cd92ff099504
Revises: cdc82f99bace
Create Date: 2026-03-04 12:49:12.251333

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'cd92ff099504'
down_revision: Union[str, None] = 'cdc82f99bace'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create users table
    op.create_table('users',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('email', sa.String(length=255), nullable=False),
    sa.Column('name', sa.String(length=50), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=True),
    sa.Column('last_login', sa.DateTime(timezone=True), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)
    op.create_index(op.f('ix_users_id'), 'users', ['id'], unique=False)

    # Add user_id column to participants (use batch mode for SQLite)
    with op.batch_alter_table('participants', schema=None) as batch_op:
        batch_op.add_column(sa.Column('user_id', sa.Integer(), nullable=True))
        batch_op.create_foreign_key('fk_participants_user_id', 'users', ['user_id'], ['id'])


def downgrade() -> None:
    # Remove user_id column from participants (use batch mode for SQLite)
    with op.batch_alter_table('participants', schema=None) as batch_op:
        batch_op.drop_constraint('fk_participants_user_id', type_='foreignkey')
        batch_op.drop_column('user_id')

    # Drop users table
    op.drop_index(op.f('ix_users_id'), table_name='users')
    op.drop_index(op.f('ix_users_email'), table_name='users')
    op.drop_table('users')
