import datetime
import logging
from uuid import UUID

from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session
from dateutil.relativedelta import relativedelta

from app.db.models import (
    Subscription,
    User,
    GenerationRequest,
    Transaction,
    Link,
    Price,
)
from app.utils.enum import TransactionStatus


logger = logging.getLogger(__name__)


class DatabaseManager:
    @classmethod
    async def add_user(
        cls, session: AsyncSession, user_id: int, username: str
    ) -> User | None:
        user = await session.scalar(select(User).where(User.user_id == user_id))
        if user is None:
            new_user = User(user_id=user_id, username=username)
            session.add(new_user)
            return new_user

        return user

    @classmethod
    async def add_link(cls, session: AsyncSession, name: str, link: str) -> User | None:
        user = await session.scalar(select(Link).where(Link.name == name))
        if user is None:
            session.add(Link(name=name, link=link))

        return user

    @classmethod
    async def add_credits_to_user(
        cls, session: AsyncSession, user_id: int, credits: int
    ) -> User | None:
        user = await session.scalar(select(User).where(User.user_id == user_id))
        user.credits += credits

        return user

    @classmethod
    async def get_links(cls, session: AsyncSession) -> list[Link] | None:
        links = await session.scalars(select(Link))
        return links

    @classmethod
    async def get_link_by_url(cls, session: AsyncSession, url: str) -> Link | None:
        link = await session.scalar(select(Link).where(Link.link == url))
        return link

    @classmethod
    async def get_user(cls, session: AsyncSession, user_id: int) -> User | None:
        user = await session.scalar(select(User).where(User.user_id == user_id))
        return user

    @classmethod
    async def get_users(cls, session: AsyncSession) -> list[User] | None:
        users = await session.scalars(select(User))
        return users

    @classmethod
    async def add_generation_request(
        cls, session: AsyncSession, request: GenerationRequest
    ):
        session.add(request)

    @classmethod
    async def get_generation_request(
        cls, session: AsyncSession, request_id: str
    ) -> GenerationRequest | None:
        request = await session.get(GenerationRequest, request_id)
        return request

    @classmethod
    async def get_request_by_task_id(
        cls, session: AsyncSession, task_id: str
    ) -> GenerationRequest | None:
        request = await session.scalar(
            select(GenerationRequest).where(GenerationRequest.task_id == task_id)
        )
        return request

    @classmethod
    def get_request_sync(
        cls, session: Session, request_id: str
    ) -> GenerationRequest | None:
        request = session.get(GenerationRequest, request_id)
        return request

    @classmethod
    async def update_generation_request(
        cls, session: AsyncSession, request_id: str, **kwargs
    ):
        request = await session.get(GenerationRequest, request_id)
        if request:
            for key, value in kwargs.items():
                setattr(request, key, value)

    @classmethod
    async def update_generation_request_status(
        cls, session: AsyncSession, request_id: str, status: str
    ):
        await cls.update_generation_request(session, request_id, status=status)

    @classmethod
    def update_generation_request_sync(
        cls, session: Session, request_id: str, **kwargs
    ):
        request = session.get(GenerationRequest, request_id)
        if request:
            for key, value in kwargs.items():
                setattr(request, key, value)

    @classmethod
    def update_generetion_request_status_sync(
        cls, session: Session, request_id: str, status: str
    ):
        cls.update_generation_request_sync(session, request_id, status=status)

    @classmethod
    async def add_transaction(
        cls,
        session: AsyncSession,
        user_id: int,
        price_id: UUID,
        status: TransactionStatus,
        payment_id: UUID,
        commit=True,
    ) -> Transaction:
        new_transaction = Transaction(
            user_id=user_id, price_id=price_id, status=status, payment_id=payment_id
        )
        session.add(new_transaction)
        if commit:
            await session.commit()

        return new_transaction

    @classmethod
    async def get_transaction_by_payment_id(
        cls, session: AsyncSession, payment_id: str
    ) -> Transaction | None:
        transaction = await session.scalar(
            select(Transaction).where(Transaction.payment_id == payment_id)
        )
        return transaction

    @classmethod
    async def add_subscription(
        cls,
        session: AsyncSession,
        user_id: int,
        transaction_id: UUID,
        duration: int,
        payment_method_id: str,
    ) -> bool:
        start_date = datetime.datetime.utcnow()
        end_date = start_date + relativedelta(months=duration)

        subscription = await cls.check_subscription(session, user_id)
        transaction = await cls.get_transaction_by_id(transaction_id)

        if subscription is not None:
            subscription.is_active = False
            if subscription.transaction.price.plan_id == transaction.price.plan_id:
                end_date = subscription.end_date + relativedelta(months=duration)
                

        new_subscription = Subscription(
            user_id=user_id,
            transaction_id=transaction_id,
            payment_method_id=payment_method_id,
            start_date=start_date,
            end_date=end_date,
        )

        await cls.add_credits_to_user(session, user_id, credits)

        session.add(new_subscription)
        return subscription

    @classmethod
    async def check_subscription(
        cls, session: AsyncSession, user_id: int
    ) -> Subscription:
        current_time = datetime.datetime.utcnow()

        result = await session.execute(
            select(Subscription)
            .where(
                (Subscription.user_id == user_id)
                & (Subscription.end_date >= current_time)
            )
            .join(Subscription.transaction)
            .join(Transaction.price)
            .order_by(desc(Subscription.end_date))
            .limit(1)
        )

        return result.scalar_one_or_none()

    @classmethod
    async def get_transaction_by_id(
        cls, session: AsyncSession, id: UUID
    ) -> Transaction | None:
        result = await session.execute(
            select(Transaction)
            .where((Transaction.id == id))
            .join(Transaction.price)
            .limit(1)
        )

        return result.scalar_one_or_none()

    @classmethod
    async def get_prices_by_type_and_currency(
        cls, session: AsyncSession, type: str, currency: str
    ) -> list[Price]:
        prices = await session.scalars(
            select(Price)
            .where(Price.type == type)
            .where(Price.currency == currency)
            .order_by(Price.price)
        )
        return prices

    @classmethod
    async def get_price_by_type_and_name_and_currency_and_duration(
        cls,
        session: AsyncSession,
        type: str,
        plan_id: str,
        currency: str,
        duration: int | None = None,
    ) -> Price | None:
        query = (
            select(Price)
            .where(Price.type == type)
            .where(Price.plan_id == plan_id)
            .where(Price.currency == currency)
        )
        if type == "PREMIUM":
            query = query.where(Price.duration == duration)

        price = await session.scalar(query)
        return price
