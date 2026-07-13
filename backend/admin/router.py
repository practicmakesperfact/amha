"""
Admin REST API router.
Provides full backend for the future admin dashboard.
All endpoints require admin authentication (Telegram ID header).
"""

from typing import Optional
from fastapi import APIRouter, Depends, Header, HTTPException, Query, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from backend.core.config import settings
from backend.core.logging import get_logger
from backend.database.session import get_db_session
from backend.models.models import DepositStatus, WithdrawalStatus, TransferStatus
from backend.repositories.deposit_repository import DepositRepository, UsedSMSRepository
from backend.repositories.transfer_repository import TransferRepository
from backend.repositories.user_repository import UserRepository
from backend.repositories.withdrawal_repository import WithdrawalRepository
from backend.services.deposit_service import DepositService
from backend.services.transfer_service import TransferService
from backend.services.withdrawal_service import WithdrawalService

logger = get_logger(__name__)
admin_router = APIRouter()


# ── Auth dependency ───────────────────────────────────────────────────────────


async def require_admin(
    x_admin_id: int = Header(..., description="Admin Telegram ID"),
) -> int:
    if x_admin_id not in settings.ADMIN_TELEGRAM_IDS:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized",
        )
    return x_admin_id


# ── Pydantic response schemas ─────────────────────────────────────────────────


class AdminActionRequest(BaseModel):
    note: Optional[str] = None


# ── Users ─────────────────────────────────────────────────────────────────────


@admin_router.get("/users")
async def list_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    search: Optional[str] = Query(None),
    admin_id: int = Depends(require_admin),
    session: AsyncSession = Depends(get_db_session),
):
    repo = UserRepository(session)
    if search:
        users = await repo.search(search)
    else:
        users = await repo.get_all(skip=skip, limit=limit)

    return [
        {
            "id": u.id,
            "telegram_id": u.telegram_id,
            "username": u.username,
            "full_name": u.full_name,
            "phone_number": u.phone_number,
            "main_wallet": u.main_wallet,
            "play_wallet": u.play_wallet,
            "coin": u.coin,
            "wins": u.wins,
            "is_registered": u.is_registered,
            "is_active": u.is_active,
            "created_at": u.created_at.isoformat(),
        }
        for u in users
    ]


@admin_router.get("/users/{user_id}")
async def get_user(
    user_id: int,
    admin_id: int = Depends(require_admin),
    session: AsyncSession = Depends(get_db_session),
):
    repo = UserRepository(session)
    user = await repo.get_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return {
        "id": user.id,
        "telegram_id": user.telegram_id,
        "username": user.username,
        "full_name": user.full_name,
        "phone_number": user.phone_number,
        "main_wallet": user.main_wallet,
        "play_wallet": user.play_wallet,
        "coin": user.coin,
        "wins": user.wins,
        "is_registered": user.is_registered,
        "is_active": user.is_active,
        "created_at": user.created_at.isoformat(),
    }


# ── Deposits ──────────────────────────────────────────────────────────────────


@admin_router.get("/deposits")
async def list_deposits(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    status_filter: Optional[str] = Query(None, alias="status"),
    admin_id: int = Depends(require_admin),
    session: AsyncSession = Depends(get_db_session),
):
    repo = DepositRepository(session)
    deposits = await repo.get_all(skip=skip, limit=limit)

    if status_filter:
        try:
            sf = DepositStatus(status_filter.upper())
            deposits = [d for d in deposits if d.status == sf]
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid status: {status_filter}")

    return [
        {
            "id": d.id,
            "user_id": d.user_id,
            "amount": d.amount,
            "reference": d.reference,
            "status": d.status.value,
            "sender_phone": d.sender_phone,
            "receiver_phone": d.receiver_phone,
            "transaction_date": d.transaction_date,
            "created_at": d.created_at.isoformat(),
        }
        for d in deposits
    ]


@admin_router.post("/deposits/{deposit_id}/approve")
async def approve_deposit(
    deposit_id: int,
    body: AdminActionRequest,
    admin_id: int = Depends(require_admin),
    session: AsyncSession = Depends(get_db_session),
):
    async with session.begin():
        service = DepositService(session)
        deposit = await service.admin_approve(deposit_id, admin_id)
    if not deposit:
        raise HTTPException(status_code=404, detail="Deposit not found")
    return {"ok": True, "deposit_id": deposit_id, "status": deposit.status.value}


@admin_router.post("/deposits/{deposit_id}/reject")
async def reject_deposit(
    deposit_id: int,
    body: AdminActionRequest,
    admin_id: int = Depends(require_admin),
    session: AsyncSession = Depends(get_db_session),
):
    async with session.begin():
        service = DepositService(session)
        deposit = await service.admin_reject(deposit_id, admin_id, note=body.note or "")
    if not deposit:
        raise HTTPException(status_code=404, detail="Deposit not found")
    return {"ok": True, "deposit_id": deposit_id, "status": deposit.status.value}


# ── Withdrawals ───────────────────────────────────────────────────────────────


@admin_router.get("/withdrawals")
async def list_withdrawals(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    status_filter: Optional[str] = Query(None, alias="status"),
    admin_id: int = Depends(require_admin),
    session: AsyncSession = Depends(get_db_session),
):
    repo = WithdrawalRepository(session)
    withdrawals = await repo.get_all(skip=skip, limit=limit)

    if status_filter:
        try:
            sf = WithdrawalStatus(status_filter.upper())
            withdrawals = [w for w in withdrawals if w.status == sf]
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid status: {status_filter}")

    return [
        {
            "id": w.id,
            "user_id": w.user_id,
            "telebirr_number": w.telebirr_number,
            "amount": w.amount,
            "status": w.status.value,
            "created_at": w.created_at.isoformat(),
        }
        for w in withdrawals
    ]


@admin_router.post("/withdrawals/{withdrawal_id}/approve")
async def approve_withdrawal(
    withdrawal_id: int,
    body: AdminActionRequest,
    admin_id: int = Depends(require_admin),
    session: AsyncSession = Depends(get_db_session),
):
    async with session.begin():
        service = WithdrawalService(session)
        w = await service.admin_approve(withdrawal_id, admin_id)
    if not w:
        raise HTTPException(status_code=404, detail="Withdrawal not found")
    return {"ok": True, "withdrawal_id": withdrawal_id, "status": w.status.value}


@admin_router.post("/withdrawals/{withdrawal_id}/reject")
async def reject_withdrawal(
    withdrawal_id: int,
    body: AdminActionRequest,
    admin_id: int = Depends(require_admin),
    session: AsyncSession = Depends(get_db_session),
):
    async with session.begin():
        service = WithdrawalService(session)
        w = await service.admin_reject(withdrawal_id, admin_id, note=body.note or "")
    if not w:
        raise HTTPException(status_code=404, detail="Withdrawal not found")
    return {"ok": True, "withdrawal_id": withdrawal_id, "status": w.status.value}


# ── Transfers ─────────────────────────────────────────────────────────────────


@admin_router.get("/transfers")
async def list_transfers(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    admin_id: int = Depends(require_admin),
    session: AsyncSession = Depends(get_db_session),
):
    repo = TransferRepository(session)
    transfers = await repo.get_all(skip=skip, limit=limit)
    return [
        {
            "id": t.id,
            "sender_id": t.sender_id,
            "receiver_id": t.receiver_id,
            "amount": t.amount,
            "status": t.status.value,
            "created_at": t.created_at.isoformat(),
        }
        for t in transfers
    ]


@admin_router.post("/transfers/{transfer_id}/approve")
async def approve_transfer(
    transfer_id: int,
    body: AdminActionRequest,
    admin_id: int = Depends(require_admin),
    session: AsyncSession = Depends(get_db_session),
):
    async with session.begin():
        service = TransferService(session)
        t = await service.admin_approve(transfer_id, admin_id)
    if not t:
        raise HTTPException(status_code=404, detail="Transfer not found")
    return {"ok": True, "transfer_id": transfer_id, "status": t.status.value}


@admin_router.post("/transfers/{transfer_id}/reject")
async def reject_transfer(
    transfer_id: int,
    body: AdminActionRequest,
    admin_id: int = Depends(require_admin),
    session: AsyncSession = Depends(get_db_session),
):
    async with session.begin():
        service = TransferService(session)
        t = await service.admin_reject(transfer_id, admin_id, note=body.note or "")
    if not t:
        raise HTTPException(status_code=404, detail="Transfer not found")
    return {"ok": True, "transfer_id": transfer_id, "status": t.status.value}


# ── Stats / Dashboard ─────────────────────────────────────────────────────────


@admin_router.get("/stats")
async def get_stats(
    admin_id: int = Depends(require_admin),
    session: AsyncSession = Depends(get_db_session),
):
    """Dashboard statistics."""
    from sqlalchemy import func, select
    from backend.models.models import User, Deposit, Withdrawal, Transfer

    total_users = (await session.execute(select(func.count(User.id)))).scalar_one()
    registered_users = (
        await session.execute(
            select(func.count(User.id)).where(User.is_registered == True)
        )
    ).scalar_one()
    total_deposits = (await session.execute(select(func.count(Deposit.id)))).scalar_one()
    approved_deposits_sum = (
        await session.execute(
            select(func.sum(Deposit.amount)).where(
                Deposit.status == DepositStatus.APPROVED
            )
        )
    ).scalar_one() or 0.0
    pending_withdrawals = (
        await session.execute(
            select(func.count(Withdrawal.id)).where(
                Withdrawal.status == WithdrawalStatus.PENDING
            )
        )
    ).scalar_one()
    pending_transfers = (
        await session.execute(
            select(func.count(Transfer.id)).where(
                Transfer.status == TransferStatus.PENDING
            )
        )
    ).scalar_one()

    return {
        "total_users": total_users,
        "registered_users": registered_users,
        "total_deposits": total_deposits,
        "total_deposited_etb": round(approved_deposits_sum, 2),
        "pending_withdrawals": pending_withdrawals,
        "pending_transfers": pending_transfers,
    }
