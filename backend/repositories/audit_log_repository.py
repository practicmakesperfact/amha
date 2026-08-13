"""
AuditLog repository.
"""
from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.models.models import AuditLog, AuditAction
from backend.repositories.base import BaseRepository


class AuditLogRepository(BaseRepository[AuditLog]):
    model = AuditLog

    async def log_action(
        self,
        action: AuditAction,
        user_id: Optional[int] = None,
        admin_id: Optional[int] = None,
        deposit_id: Optional[int] = None,
        withdrawal_id: Optional[int] = None,
        transfer_id: Optional[int] = None,
        amount: Optional[float] = None,
        description: Optional[str] = None,
        extra_data: Optional[str] = None,
        ip_address: Optional[str] = None,
    ) -> AuditLog:
        """Log an audit action."""
        log = AuditLog(
            action=action,
            user_id=user_id,
            admin_id=admin_id,
            deposit_id=deposit_id,
            withdrawal_id=withdrawal_id,
            transfer_id=transfer_id,
            amount=amount,
            description=description,
            extra_data=extra_data,
            ip_address=ip_address,
        )
        self.session.add(log)
        await self.session.flush()
        await self.session.refresh(log)
        return log

    async def get_user_logs(
        self, user_id: int, skip: int = 0, limit: int = 50
    ) -> list[AuditLog]:
        """Get audit logs for a user."""
        result = await self.session.execute(
            select(AuditLog)
            .where(AuditLog.user_id == user_id)
            .order_by(AuditLog.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())

    async def get_admin_logs(
        self, admin_id: int, skip: int = 0, limit: int = 50
    ) -> list[AuditLog]:
        """Get audit logs for admin actions."""
        result = await self.session.execute(
            select(AuditLog)
            .where(AuditLog.admin_id == admin_id)
            .order_by(AuditLog.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())
