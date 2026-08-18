"""add bingo game tables

Revision ID: c3d4e5f6g7h8
Revises: b2c3d4e5f6g7
Create Date: 2026-08-13 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'c3d4e5f6g7h8'
down_revision = 'b2c3d4e5f6g7'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create enums
    gamestatus_enum = postgresql.ENUM('WAITING', 'STARTING', 'PLAYING', 'PAUSED', 'FINISHED', 'CANCELLED', name='gamestatus', create_type=False)
    gamestatus_enum.create(op.get_bind(), checkfirst=True)
    
    playerstatus_enum = postgresql.ENUM('JOINED', 'ACTIVE', 'DISCONNECTED', 'LEFT', 'WINNER', name='playerstatus', create_type=False)
    playerstatus_enum.create(op.get_bind(), checkfirst=True)
    
    gameeventtype_enum = postgresql.ENUM(
        'GAME_CREATED', 'PLAYER_JOINED', 'PLAYER_LEFT', 'GAME_STARTING', 'GAME_STARTED',
        'NUMBER_CALLED', 'GAME_PAUSED', 'GAME_RESUMED', 'WINNER_DECLARED', 'PRIZE_PAID',
        'GAME_FINISHED', 'GAME_CANCELLED', 'REFUND_ISSUED',
        name='gameeventtype', create_type=False
    )
    gameeventtype_enum.create(op.get_bind(), checkfirst=True)
    
    winpattern_enum = postgresql.ENUM('ROW', 'COLUMN', 'DIAGONAL', 'FULL_CARD', name='winpattern', create_type=False)
    winpattern_enum.create(op.get_bind(), checkfirst=True)

    # BingoGame table
    op.create_table(
        'bingo_games',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('game_number', sa.String(length=64), nullable=False),
        sa.Column('entry_fee', sa.Float(), nullable=False),
        sa.Column('prize_pool', sa.Float(), nullable=False),
        sa.Column('max_players', sa.Integer(), nullable=False),
        sa.Column('min_players', sa.Integer(), nullable=False),
        sa.Column('status', sa.Enum('WAITING', 'STARTING', 'PLAYING', 'PAUSED', 'FINISHED', 'CANCELLED', name='gamestatus'), nullable=False),
        sa.Column('current_number', sa.Integer(), nullable=True),
        sa.Column('numbers_called_count', sa.Integer(), nullable=False),
        sa.Column('started_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('finished_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('paused_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('prize_distribution', sa.Text(), nullable=True),
        sa.Column('created_by', sa.BigInteger(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('game_number'),
        sa.CheckConstraint('entry_fee >= 0', name='ck_bingo_game_entry_fee_positive'),
        sa.CheckConstraint('prize_pool >= 0', name='ck_bingo_game_prize_pool_positive'),
        sa.CheckConstraint('max_players > 0', name='ck_bingo_game_max_players_positive'),
        sa.CheckConstraint('min_players > 0', name='ck_bingo_game_min_players_positive'),
    )
    op.create_index('idx_bingo_game_status', 'bingo_games', ['status'])
    op.create_index('idx_bingo_game_created', 'bingo_games', ['created_at'])
    op.create_index('idx_bingo_game_number', 'bingo_games', ['game_number'], unique=True)

    # Cartela table
    op.create_table(
        'cartelas',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('game_id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('numbers', sa.Text(), nullable=False),
        sa.Column('cartela_number', sa.String(length=64), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['game_id'], ['bingo_games.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('game_id', 'user_id', name='uq_cartela_game_user'),
    )
    op.create_index('idx_cartela_game', 'cartelas', ['game_id'])
    op.create_index('idx_cartela_user', 'cartelas', ['user_id'])
    op.create_index('idx_cartela_number', 'cartelas', ['cartela_number'])

    # GamePlayer table
    op.create_table(
        'game_players',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('game_id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('cartela_id', sa.Integer(), nullable=True),
        sa.Column('entry_fee', sa.Float(), nullable=False),
        sa.Column('prize_amount', sa.Float(), nullable=False),
        sa.Column('status', sa.Enum('JOINED', 'ACTIVE', 'DISCONNECTED', 'LEFT', 'WINNER', name='playerstatus'), nullable=False),
        sa.Column('is_winner', sa.Boolean(), nullable=False),
        sa.Column('winning_position', sa.Integer(), nullable=True),
        sa.Column('win_pattern', sa.Enum('ROW', 'COLUMN', 'DIAGONAL', 'FULL_CARD', name='winpattern'), nullable=True),
        sa.Column('marked_numbers', sa.Text(), nullable=True),
        sa.Column('joined_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('left_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['game_id'], ['bingo_games.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['cartela_id'], ['cartelas.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('game_id', 'user_id', name='uq_game_player'),
        sa.CheckConstraint('entry_fee >= 0', name='ck_game_player_entry_fee_positive'),
        sa.CheckConstraint('prize_amount >= 0', name='ck_game_player_prize_positive'),
    )
    op.create_index('idx_game_player_game', 'game_players', ['game_id'])
    op.create_index('idx_game_player_user', 'game_players', ['user_id'])
    op.create_index('idx_game_player_status', 'game_players', ['status'])

    # CalledNumber table
    op.create_table(
        'called_numbers',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('game_id', sa.Integer(), nullable=False),
        sa.Column('number', sa.Integer(), nullable=False),
        sa.Column('sequence', sa.Integer(), nullable=False),
        sa.Column('column_letter', sa.String(length=1), nullable=False),
        sa.Column('called_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['game_id'], ['bingo_games.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('game_id', 'number', name='uq_called_number_game'),
        sa.CheckConstraint('number >= 1 AND number <= 75', name='ck_called_number_range'),
        sa.CheckConstraint('sequence > 0', name='ck_called_number_sequence_positive'),
    )
    op.create_index('idx_called_number_game', 'called_numbers', ['game_id'])
    op.create_index('idx_called_number_sequence', 'called_numbers', ['game_id', 'sequence'])

    # GameEvent table
    op.create_table(
        'game_events',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('game_id', sa.Integer(), nullable=False),
        sa.Column('event_type', sa.Enum(
            'GAME_CREATED', 'PLAYER_JOINED', 'PLAYER_LEFT', 'GAME_STARTING', 'GAME_STARTED',
            'NUMBER_CALLED', 'GAME_PAUSED', 'GAME_RESUMED', 'WINNER_DECLARED', 'PRIZE_PAID',
            'GAME_FINISHED', 'GAME_CANCELLED', 'REFUND_ISSUED',
            name='gameeventtype'
        ), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('player_id', sa.Integer(), nullable=True),
        sa.Column('event_data', sa.Text(), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['game_id'], ['bingo_games.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('idx_game_event_game', 'game_events', ['game_id'])
    op.create_index('idx_game_event_type', 'game_events', ['event_type'])
    op.create_index('idx_game_event_created', 'game_events', ['created_at'])


def downgrade() -> None:
    # Drop tables
    op.drop_index('idx_game_event_created', table_name='game_events')
    op.drop_index('idx_game_event_type', table_name='game_events')
    op.drop_index('idx_game_event_game', table_name='game_events')
    op.drop_table('game_events')
    
    op.drop_index('idx_called_number_sequence', table_name='called_numbers')
    op.drop_index('idx_called_number_game', table_name='called_numbers')
    op.drop_table('called_numbers')
    
    op.drop_index('idx_game_player_status', table_name='game_players')
    op.drop_index('idx_game_player_user', table_name='game_players')
    op.drop_index('idx_game_player_game', table_name='game_players')
    op.drop_table('game_players')
    
    op.drop_index('idx_cartela_number', table_name='cartelas')
    op.drop_index('idx_cartela_user', table_name='cartelas')
    op.drop_index('idx_cartela_game', table_name='cartelas')
    op.drop_table('cartelas')
    
    op.drop_index('idx_bingo_game_number', table_name='bingo_games')
    op.drop_index('idx_bingo_game_created', table_name='bingo_games')
    op.drop_index('idx_bingo_game_status', table_name='bingo_games')
    op.drop_table('bingo_games')
    
    # Drop enums
    sa.Enum(name='winpattern').drop(op.get_bind(), checkfirst=True)
    sa.Enum(name='gameeventtype').drop(op.get_bind(), checkfirst=True)
    sa.Enum(name='playerstatus').drop(op.get_bind(), checkfirst=True)
    sa.Enum(name='gamestatus').drop(op.get_bind(), checkfirst=True)
