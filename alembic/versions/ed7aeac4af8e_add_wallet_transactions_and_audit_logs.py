"""add_wallet_transactions_and_audit_logs

Revision ID: ed7aeac4af8e
Revises: a1b2c3d4e5f6
Create Date: 2026-08-13 06:04:40.653652

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ed7aeac4af8e'
down_revision: Union[str, None] = 'a1b2c3d4e5f6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
