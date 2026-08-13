"""add wallet transactions and audit logs

Revision ID: b2c3d4e5f6g7
Revises: a1b2c3d4e5f6
Create Date: 2024-12-08 22:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b2c3d4e5f6g7'
down_revision: Union[str, None] = 'a1b2c3d4e5f6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create wallet_transactions table
    op.create_table(
        'wallet_transactions',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('transaction_type', sa.Enum('DEPOSIT', 'WITHDRAWAL', 'TRANSFER_OUT', 'TRANSFER_IN', 'ADMIN_CREDIT', 'ADMIN_DEBIT', name='transactiontype'), nullable=False),
        sa.Column('amount', sa.Float(), nullable=False),
        sa.Column('balance_before', sa.Float(), nullable=False),
        sa.Column('balance_after', sa.Float(), nullable=False),
        sa.Column('deposit_id', sa.Integer(), nullable=True),
        sa.Column('withdrawal_id', sa.Integer(), nullable=True),
        sa.Column('transfer_id', sa.Integer(), nullable=True),
        sa.Column('description', sa.String(length=512), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_wallet_tx_user_created', 'wallet_transactions', ['user_id', 'created_at'])
    op.create_index('idx_wallet_tx_type', 'wallet_transactions', ['transaction_type'])
    op.create_index(op.f('ix_wallet_transactions_user_id'), 'wallet_transactions', ['user_id'])

    # Create audit_logs table
    op.create_table(
        'audit_logs',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('action', sa.Enum('USER_REGISTERED', 'DEPOSIT_CREATED', 'DEPOSIT_APPROVED', 'DEPOSIT_REJECTED', 'WITHDRAWAL_CREATED', 'WITHDRAWAL_APPROVED', 'WITHDRAWAL_REJECTED', 'TRANSFER_CREATED', 'TRANSFER_EXECUTED', 'WALLET_CREDITED', 'WALLET_DEBITED', 'ADMIN_ACTION', name='auditaction'), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('admin_id', sa.BigInteger(), nullable=True),
        sa.Column('deposit_id', sa.Integer(), nullable=True),
        sa.Column('withdrawal_id', sa.Integer(), nullable=True),
        sa.Column('transfer_id', sa.Integer(), nullable=True),
        sa.Column('amount', sa.Float(), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('extra_data', sa.Text(), nullable=True),
        sa.Column('ip_address', sa.String(length=45), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_audit_user_created', 'audit_logs', ['user_id', 'created_at'])
    op.create_index('idx_audit_action', 'audit_logs', ['action'])
    op.create_index('idx_audit_admin', 'audit_logs', ['admin_id'])
    op.create_index(op.f('ix_audit_logs_user_id'), 'audit_logs', ['user_id'])


def downgrade() -> None:
    op.drop_index(op.f('ix_audit_logs_user_id'), table_name='audit_logs')
    op.drop_index('idx_audit_admin', table_name='audit_logs')
    op.drop_index('idx_audit_action', table_name='audit_logs')
    op.drop_index('idx_audit_user_created', table_name='audit_logs')
    op.drop_table('audit_logs')
    op.execute('DROP TYPE auditaction')

    op.drop_index(op.f('ix_wallet_transactions_user_id'), table_name='wallet_transactions')
    op.drop_index('idx_wallet_tx_type', table_name='wallet_transactions')
    op.drop_index('idx_wallet_tx_user_created', table_name='wallet_transactions')
    op.drop_table('wallet_transactions')
    op.execute('DROP TYPE transactiontype')
