
from __future__ import annotations

import enum
from datetime import datetime
from typing import Optional

from sqlalchemy import (
    BigInteger,
    Boolean,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    func,
    UniqueConstraint,
    Index,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.database.base import Base


# ── Enums ────────────────────────────────────────────────────────────────────


class DepositStatus(str, enum.Enum):
    PENDING = "PENDING"
    PENDING_ADMIN_APPROVAL = "PENDING_ADMIN_APPROVAL"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"


class WithdrawalStatus(str, enum.Enum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"


class TransferStatus(str, enum.Enum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"


# ── User ─────────────────────────────────────────────────────────────────────


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    telegram_id: Mapped[int] = mapped_column(BigInteger, unique=True, nullable=False, index=True)
    chat_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    username: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    first_name: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    last_name: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    full_name: Mapped[Optional[str]] = mapped_column(String(256), nullable=True)
    phone_number: Mapped[Optional[str]] = mapped_column(String(20), nullable=True, unique=True, index=True)

    main_wallet: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    play_wallet: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    coin: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    wins: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    is_registered: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    # ── Relationships
    deposits: Mapped[list[Deposit]] = relationship(
        "Deposit", back_populates="user", cascade="all, delete-orphan"
    )
    withdrawals: Mapped[list[Withdrawal]] = relationship(
        "Withdrawal", back_populates="user", cascade="all, delete-orphan"
    )
    sent_transfers: Mapped[list[Transfer]] = relationship(
        "Transfer", foreign_keys="Transfer.sender_id", back_populates="sender"
    )
    received_transfers: Mapped[list[Transfer]] = relationship(
        "Transfer", foreign_keys="Transfer.receiver_id", back_populates="receiver"
    )

    def __repr__(self) -> str:
        return f"<User id={self.id} telegram_id={self.telegram_id} username={self.username}>"


# ── Deposit ───────────────────────────────────────────────────────────────────


class Deposit(Base):
    __tablename__ = "deposits"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    amount: Mapped[float] = mapped_column(Float, nullable=False)
    sms_text: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    sender_phone: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    receiver_phone: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    reference: Mapped[Optional[str]] = mapped_column(String(128), nullable=True, index=True)
    transaction_date: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    status: Mapped[DepositStatus] = mapped_column(
        Enum(DepositStatus), default=DepositStatus.PENDING, nullable=False
    )
    admin_note: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    approved_by: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    user: Mapped[User] = relationship("User", back_populates="deposits")

    def __repr__(self) -> str:
        return f"<Deposit id={self.id} user_id={self.user_id} amount={self.amount} status={self.status}>"


# ── Withdrawal ────────────────────────────────────────────────────────────────


class Withdrawal(Base):
    __tablename__ = "withdrawals"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    telebirr_number: Mapped[str] = mapped_column(String(20), nullable=False)
    amount: Mapped[float] = mapped_column(Float, nullable=False)
    status: Mapped[WithdrawalStatus] = mapped_column(
        Enum(WithdrawalStatus), default=WithdrawalStatus.PENDING, nullable=False
    )
    admin_note: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    approved_by: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    user: Mapped[User] = relationship("User", back_populates="withdrawals")

    def __repr__(self) -> str:
        return f"<Withdrawal id={self.id} user_id={self.user_id} amount={self.amount} status={self.status}>"


# ── Transfer ──────────────────────────────────────────────────────────────────


class Transfer(Base):
    __tablename__ = "transfers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    sender_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    receiver_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    amount: Mapped[float] = mapped_column(Float, nullable=False)
    status: Mapped[TransferStatus] = mapped_column(
        Enum(TransferStatus), default=TransferStatus.PENDING, nullable=False
    )
    admin_note: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    approved_by: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    sender: Mapped[User] = relationship(
        "User", foreign_keys=[sender_id], back_populates="sent_transfers"
    )
    receiver: Mapped[User] = relationship(
        "User", foreign_keys=[receiver_id], back_populates="received_transfers"
    )

    def __repr__(self) -> str:
        return f"<Transfer id={self.id} from={self.sender_id} to={self.receiver_id} amount={self.amount}>"


# ── UsedSMS / Duplicate prevention ───────────────────────────────────────────


class UsedSMS(Base):
    """Permanent log of every Telebirr reference number ever used."""

    __tablename__ = "used_sms"
    __table_args__ = (UniqueConstraint("reference_number", name="uq_used_sms_reference"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    reference_number: Mapped[str] = mapped_column(String(128), nullable=False)
    sms_hash: Mapped[str] = mapped_column(String(64), nullable=False)  # SHA-256 of raw SMS text
    deposit_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("deposits.id", ondelete="SET NULL"), nullable=True, index=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    def __repr__(self) -> str:
        return f"<UsedSMS id={self.id} ref={self.reference_number}>"


# ── WalletTransaction / Complete ledger ──────────────────────────────────────


class TransactionType(str, enum.Enum):
    DEPOSIT = "DEPOSIT"
    WITHDRAWAL = "WITHDRAWAL"
    TRANSFER_OUT = "TRANSFER_OUT"
    TRANSFER_IN = "TRANSFER_IN"
    ADMIN_CREDIT = "ADMIN_CREDIT"
    ADMIN_DEBIT = "ADMIN_DEBIT"


class WalletTransaction(Base):
    """Complete ledger of all wallet movements for audit trail."""

    __tablename__ = "wallet_transactions"
    __table_args__ = (
        Index("idx_wallet_tx_user_created", "user_id", "created_at"),
        Index("idx_wallet_tx_type", "transaction_type"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    transaction_type: Mapped[TransactionType] = mapped_column(
        Enum(TransactionType), nullable=False
    )
    amount: Mapped[float] = mapped_column(Float, nullable=False)
    balance_before: Mapped[float] = mapped_column(Float, nullable=False)
    balance_after: Mapped[float] = mapped_column(Float, nullable=False)
    
    # Reference to related entity
    deposit_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    withdrawal_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    transfer_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    
    description: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    user: Mapped[User] = relationship("User")

    def __repr__(self) -> str:
        return f"<WalletTransaction id={self.id} user={self.user_id} type={self.transaction_type} amount={self.amount}>"


# ── AuditLog / System audit trail ────────────────────────────────────────────


class AuditAction(str, enum.Enum):
    USER_REGISTERED = "USER_REGISTERED"
    DEPOSIT_CREATED = "DEPOSIT_CREATED"
    DEPOSIT_APPROVED = "DEPOSIT_APPROVED"
    DEPOSIT_REJECTED = "DEPOSIT_REJECTED"
    WITHDRAWAL_CREATED = "WITHDRAWAL_CREATED"
    WITHDRAWAL_APPROVED = "WITHDRAWAL_APPROVED"
    WITHDRAWAL_REJECTED = "WITHDRAWAL_REJECTED"
    TRANSFER_CREATED = "TRANSFER_CREATED"
    TRANSFER_EXECUTED = "TRANSFER_EXECUTED"
    WALLET_CREDITED = "WALLET_CREDITED"
    WALLET_DEBITED = "WALLET_DEBITED"
    ADMIN_ACTION = "ADMIN_ACTION"


class AuditLog(Base):
    """Complete audit trail of all system actions."""

    __tablename__ = "audit_logs"
    __table_args__ = (
        Index("idx_audit_user_created", "user_id", "created_at"),
        Index("idx_audit_action", "action"),
        Index("idx_audit_admin", "admin_id"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    action: Mapped[AuditAction] = mapped_column(Enum(AuditAction), nullable=False)
    user_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True
    )
    admin_id: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True)
    
    # Related entity references
    deposit_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    withdrawal_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    transfer_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    
    # Details
    amount: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    extra_data: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # JSON string for additional data
    ip_address: Mapped[Optional[str]] = mapped_column(String(45), nullable=True)
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    user: Mapped[Optional[User]] = relationship("User")

    def __repr__(self) -> str:
        return f"<AuditLog id={self.id} action={self.action} user={self.user_id}>"
