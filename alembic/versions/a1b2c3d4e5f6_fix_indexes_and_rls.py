
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, None] = '221ce4bdd0e2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ── 1. Remove duplicate/unused indexes ───────────────────────────────────

    # used_sms: drop the redundant explicit index on reference_number
    # (the UniqueConstraint 'uq_used_sms_reference' already enforces uniqueness + lookup)
    op.drop_index('ix_used_sms_reference_number', table_name='used_sms', if_exists=True)

    # users: username index is unused (queries filter by telegram_id / phone_number)
    op.drop_index('ix_users_username', table_name='users', if_exists=True)

    # deposits: low-cardinality status index is unused
    op.drop_index('ix_deposits_status', table_name='deposits', if_exists=True)

    # withdrawals: low-cardinality status index is unused
    op.drop_index('ix_withdrawals_status', table_name='withdrawals', if_exists=True)

    # transfers: low-cardinality status index is unused
    op.drop_index('ix_transfers_status', table_name='transfers', if_exists=True)

    # ── 2. Add missing FK index on used_sms.deposit_id ───────────────────────
    op.create_index('ix_used_sms_deposit_id', 'used_sms', ['deposit_id'], unique=False)

    # ── 3. Enable Row Level Security on all public tables ────────────────────
    # RLS prevents direct client API access; the app connects via service role key
    # which bypasses RLS, so this is safe for backend-only access.
    tables = ['users', 'deposits', 'withdrawals', 'transfers', 'used_sms', 'alembic_version']
    for table in tables:
        op.execute(f'ALTER TABLE public."{table}" ENABLE ROW LEVEL SECURITY;')


def downgrade() -> None:
    # ── Disable RLS ──────────────────────────────────────────────────────────
    tables = ['users', 'deposits', 'withdrawals', 'transfers', 'used_sms', 'alembic_version']
    for table in tables:
        op.execute(f'ALTER TABLE public."{table}" DISABLE ROW LEVEL SECURITY;')

    # ── Remove added FK index ─────────────────────────────────────────────────
    op.drop_index('ix_used_sms_deposit_id', table_name='used_sms')

    # ── Re-create previously dropped indexes ─────────────────────────────────
    op.create_index('ix_used_sms_reference_number', 'used_sms', ['reference_number'], unique=True)
    op.create_index('ix_users_username', 'users', ['username'], unique=False)
    op.create_index('ix_deposits_status', 'deposits', ['status'], unique=False)
    op.create_index('ix_withdrawals_status', 'withdrawals', ['status'], unique=False)
    op.create_index('ix_transfers_status', 'transfers', ['status'], unique=False)
