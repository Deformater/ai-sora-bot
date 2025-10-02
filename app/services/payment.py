import json
import logging

from app.config.utils import get_settings
from app.db.database import DatabaseManager
from app.utils.enum import DURATION_NAME_MAP, PLAN_NAME_MAP, TransactionStatus
from app.utils.payment import create_payment

logger = logging.getLogger(__name__)

settings = get_settings()


db = DatabaseManager


class PaymentService:
    @classmethod
    async def create_subuscription_payment(
        cls,
        session,
        user_id,
        duration,
        plan_id,
    ) -> str:
        price = await db.get_price_by_type_and_name_and_currency_and_duration(
            session, "PREMIUM", plan_id, "RUB", duration
        )

        description = f"Подписка уровень {PLAN_NAME_MAP[plan_id]} на {DURATION_NAME_MAP[duration]}"
        metadata = {
            "type": "PREMIUM",
            "user_id": user_id,
            "duration": duration,
            "plan": plan_id,
            "credits": price.credits,
        }
        payment_id, link = await create_payment(
            price.price, description, metadata, subscription=True
        )
        await db.add_transaction(
            session, user_id, price.id, TransactionStatus.PROCESSING, payment_id
        )

        return link

    @classmethod
    async def create_credits_payment(
        cls,
        session,
        user_id,
        plan_id,
    ) -> str:
        price = await db.get_price_by_type_and_name_and_currency_and_duration(
            session, "CREDITS", plan_id, "RUB"
        )

        description = f"Покупка {price.credits} нейрокоинов"
        metadata = {
            "type": "CREDITS",
            "user_id": user_id,
            "plan": plan_id,
            "credits": price.credits,
        }
        payment_id, link = await create_payment(
            price.price, description, metadata, subscription=False
        )
        await db.add_transaction(
            session, user_id, price.id, TransactionStatus.PROCESSING, payment_id
        )

        return link

    @classmethod
    async def proceed_successful_payment(
        cls,
        session,
        payment: dict,
    ):
        payment_type = payment["metadata"]["type"]
        if payment_type == "CREDITS":
            user_id = int(payment["metadata"]["user_id"])
            credits = int(payment["metadata"]["credits"])

            transaction = await db.get_transaction_by_payment_id(session, payment["id"])
            transaction.status = TransactionStatus.SUCCESSFULL

            await db.add_credits_to_user(session, user_id, credits)
            return "CREDITS", {
                "user_id": user_id,
                "credits": credits,
            }
