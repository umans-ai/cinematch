"""Add clerk_user_id to participants

Revision ID: b3c8f1a2d9e4
Revises: cdc82f99bace
Create Date: 2026-03-04 00:00:00.000000

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "b3c8f1a2d9e4"
down_revision: Union[str, None] = "cdc82f99bace"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("participants", sa.Column("clerk_user_id", sa.String(length=100), nullable=True))


def downgrade() -> None:
    op.drop_column("participants", "clerk_user_id")
