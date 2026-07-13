import os
os.environ["TELEGRAM_BOT_TOKEN"] = "dummy_token"
os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///:memory:"

import asyncio
import unittest
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from backend.database.base import Base
from backend.models.models import User, Deposit, DepositStatus, Withdrawal, WithdrawalStatus, Transfer, TransferStatus
from backend.services.user_service import UserService
from backend.services.deposit_service import DepositService
from backend.services.withdrawal_service import WithdrawalService
from backend.services.transfer_service import TransferService


class TestServices(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        # Create an in-memory SQLite database for testing
        self.engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
        self.session_factory = async_sessionmaker(
            bind=self.engine,
            class_=AsyncSession,
            expire_on_commit=False,
            autoflush=False,
            autocommit=False,
        )
        
        # Create tables
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
            
        self.session = self.session_factory()

    async def asyncTearDown(self):
        await self.session.close()
        await self.engine.dispose()

    async def test_user_creation_and_registration(self):
        user_service = UserService(self.session)
        
        # 1. Get or create user from Telegram
        user, created = await user_service.get_or_create_from_telegram(
            telegram_id=12345,
            chat_id=12345,
            username="test_user",
            first_name="Test",
            last_name="User"
        )
        self.assertTrue(created)
        self.assertEqual(user.telegram_id, 12345)
        self.assertFalse(user.is_registered)

        # Get the same user again, should not create a new one
        user2, created2 = await user_service.get_or_create_from_telegram(
            telegram_id=12345,
            chat_id=12345,
            username="test_user_updated",
            first_name="Test",
            last_name="User"
        )
        self.assertFalse(created2)
        self.assertEqual(user2.id, user.id)
        self.assertEqual(user2.username, "test_user_updated")

        # 2. Register user with phone number
        registered_user = await user_service.register_user(
            telegram_id=12345,
            phone_number="0909425014"
        )
        self.assertIsNotNone(registered_user)
        self.assertTrue(registered_user.is_registered)
        self.assertEqual(registered_user.phone_number, "0909425014")

    async def test_deposit_auto_approval(self):
        user_service = UserService(self.session)
        deposit_service = DepositService(self.session)

        # Create and register user
        user, _ = await user_service.get_or_create_from_telegram(
            telegram_id=22222, chat_id=22222, username="dep_user", first_name="Dep", last_name="User"
        )
        await user_service.register_user(telegram_id=22222, phone_number="0911223344")

        # Create a pending deposit request
        deposit = await deposit_service.create_pending_deposit(user_id=user.id, amount=150.00)
        self.assertEqual(deposit.status, DepositStatus.PENDING)
        self.assertEqual(deposit.amount, 150.00)

        # Process a valid SMS for the deposit
        from datetime import datetime, timezone, timedelta
        EAT = timezone(timedelta(hours=3))
        now_str = datetime.now(EAT).strftime("%d/%m/%Y %H:%M:%S")
        sms_text = f"Transaction of Birr 150.00 from 0911223344 to 0909425014 completed. Ref No. TXN100200 at {now_str}."
        result = await deposit_service.process_sms_deposit(
            user_id=user.id,
            expected_amount=150.00,
            sms_text=sms_text
        )
        self.assertTrue(result.success)
        self.assertEqual(result.deposit.status, DepositStatus.APPROVED)
        self.assertEqual(result.deposit.reference, "TXN100200")

        # Check that user's main wallet balance is updated
        updated_user = await user_service.get_by_id(user.id)
        self.assertEqual(updated_user.main_wallet, 150.00)

        # Try to process duplicate SMS
        dup_result = await deposit_service.process_sms_deposit(
            user_id=user.id,
            expected_amount=150.00,
            sms_text=sms_text
        )
        self.assertFalse(dup_result.success)
        self.assertIn("already been used", dup_result.message)

    async def test_withdrawal_flow(self):
        user_service = UserService(self.session)
        withdrawal_service = WithdrawalService(self.session)

        # Create and register user
        user, _ = await user_service.get_or_create_from_telegram(
            telegram_id=33333, chat_id=33333, username="withdraw_user", first_name="With", last_name="Draw"
        )
        await user_service.register_user(telegram_id=33333, phone_number="0911223345")

        # Credit user's wallet
        await user_service.repo.credit_wallet(user_id=user.id, amount=200.00)

        # Request withdrawal
        result = await withdrawal_service.request_withdrawal(
            user_id=user.id,
            telebirr_number="0911223345",
            amount=100.00
        )
        self.assertTrue(result.success)
        self.assertEqual(result.withdrawal.status, WithdrawalStatus.PENDING)

        # Balance should not be deducted yet
        user_db = await user_service.get_by_id(user.id)
        self.assertEqual(user_db.main_wallet, 200.00)

        # Admin approves the withdrawal
        approved_w = await withdrawal_service.admin_approve(
            withdrawal_id=result.withdrawal.id,
            admin_telegram_id=99999
        )
        self.assertIsNotNone(approved_w)
        self.assertEqual(approved_w.status, WithdrawalStatus.APPROVED)

        # Balance should now be deducted
        user_db = await user_service.get_by_id(user.id)
        self.assertEqual(user_db.main_wallet, 100.00)

    async def test_transfer_flow(self):
        user_service = UserService(self.session)
        transfer_service = TransferService(self.session)

        # Create and register Sender
        sender, _ = await user_service.get_or_create_from_telegram(
            telegram_id=44444, chat_id=44444, username="sender_user", first_name="Sen", last_name="Der"
        )
        await user_service.register_user(telegram_id=44444, phone_number="0911223346")
        await user_service.repo.credit_wallet(user_id=sender.id, amount=300.00)

        # Create and register Receiver
        receiver, _ = await user_service.get_or_create_from_telegram(
            telegram_id=55555, chat_id=55555, username="receiver_user", first_name="Rec", last_name="Eiver"
        )
        await user_service.register_user(telegram_id=55555, phone_number="0911223347")

        # Request transfer
        result = await transfer_service.request_transfer(
            sender_id=sender.id,
            recipient_identifier="@receiver_user",
            amount=50.00
        )
        self.assertTrue(result.success)
        self.assertEqual(result.transfer.status, TransferStatus.PENDING)

        # Check balances before approval (should be unchanged)
        sender_db = await user_service.get_by_id(sender.id)
        receiver_db = await user_service.get_by_id(receiver.id)
        self.assertEqual(sender_db.main_wallet, 300.00)
        self.assertEqual(receiver_db.main_wallet, 0.00)

        # Admin approves the transfer
        approved_t = await transfer_service.admin_approve(
            transfer_id=result.transfer.id,
            admin_telegram_id=99999
        )
        self.assertIsNotNone(approved_t)
        self.assertEqual(approved_t.status, TransferStatus.APPROVED)

        # Check balances after approval (sender deducted, receiver credited)
        sender_db = await user_service.get_by_id(sender.id)
        receiver_db = await user_service.get_by_id(receiver.id)
        self.assertEqual(sender_db.main_wallet, 250.00)
        self.assertEqual(receiver_db.main_wallet, 50.00)

    async def test_deposit_time_validation(self):
        user_service = UserService(self.session)
        deposit_service = DepositService(self.session)

        # Create and register user
        user, _ = await user_service.get_or_create_from_telegram(
            telegram_id=66666, chat_id=66666, username="time_user", first_name="Time", last_name="User"
        )
        await user_service.register_user(telegram_id=66666, phone_number="0911223348")

        from datetime import datetime, timezone, timedelta
        EAT = timezone(timedelta(hours=3))
        now_eat = datetime.now(EAT)

        # 1. SMS older than 30 minutes (e.g. 40 minutes old)
        old_time_str = (now_eat - timedelta(minutes=40)).strftime("%d/%m/%Y %H:%M:%S")
        sms_old = f"Transaction of Birr 100.00 from 0911223348 to 0909425014 completed. Ref No. TXNOLD at {old_time_str}."
        result_old = await deposit_service.process_sms_deposit(
            user_id=user.id,
            expected_amount=100.00,
            sms_text=sms_old
        )
        self.assertFalse(result_old.success)
        self.assertIn("too old", result_old.message)

        # 2. SMS in the future (e.g. 10 minutes in the future)
        future_time_str = (now_eat + timedelta(minutes=10)).strftime("%d/%m/%Y %H:%M:%S")
        sms_future = f"Transaction of Birr 100.00 from 0911223348 to 0909425014 completed. Ref No. TXNFUT at {future_time_str}."
        result_future = await deposit_service.process_sms_deposit(
            user_id=user.id,
            expected_amount=100.00,
            sms_text=sms_future
        )
        self.assertFalse(result_future.success)
        self.assertIn("in the future", result_future.message)


if __name__ == "__main__":
    unittest.main()
