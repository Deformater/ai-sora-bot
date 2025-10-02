import asyncio
import logging
import sys
from contextlib import asynccontextmanager

from aiogram import Bot, Dispatcher, types
from aiohttp import web
from fastapi import Depends, FastAPI, HTTPException, Request

from app.config.utils import get_settings
from app.db.connection.session import get_session
from app.db.database import DatabaseManager
from app.middlewares import DbSessionMiddleware, AlbumMiddleware
from app.routes import (
    admin_router,
    main_router,
    sora_router,
)
from app.routes.sora import sora_rabbitmq_consumer
from app.services.payment import PaymentService
from app.utils.enum import DURATION_NAME_MAP, PLAN_NAME_MAP

logging.basicConfig(level=logging.INFO, stream=sys.stdout)
logger = logging.getLogger(__name__)

settings = get_settings()
bot = Bot(token=settings.TELEGRAM_TOKEN)
db = DatabaseManager
dp = Dispatcher()
dp.update.middleware(DbSessionMiddleware())
dp.message.middleware(AlbumMiddleware())


async def set_webhook():
    await bot.set_webhook(
        f"{settings.WEBHOOK_BASE_URL}/webhook", secret_token=settings.WEBHOOK_SECRET
    )


async def handle_webhook(request: Request):
    secret = request.headers.get("X-Telegram-Bot-Api-Secret-Token")

    if secret == settings.WEBHOOK_SECRET:
        try:
            update = types.Update(**await request.json())
            await dp.feed_webhook_update(bot, update)
            return web.Response()
        except Exception as e:
            logger.warning(e)
            return web.Response()

    else:
        raise HTTPException(status_code=403, detail="Forbidden")


@asynccontextmanager
async def lifespan(app: FastAPI):
    dp.include_router(admin_router)
    dp.include_router(main_router)

    dp.include_router(sora_router)

    asyncio.create_task(sora_rabbitmq_consumer(bot))

    await set_webhook()
    yield


app = FastAPI(lifespan=lifespan)


@app.post("/webhook")
async def webhook_endpoint(request: Request):
    return await handle_webhook(request)


@app.post("/yookassa/payment")
async def yookassa_webhook(request: Request, session=Depends(get_session)):
    data = await request.json()
    if data.get("event") == "payment.succeeded":
        logger.info(data)
        payment_type, data = await PaymentService.proceed_successful_payment(
            session, data["object"]
        )
        if payment_type == "CREDITS":
            await bot.send_message(
                data["user_id"],
                f"✅ Оплата прошла успешно! вам начисленно {data['credits']} генераций.",
            )
        else:
            await bot.send_message(
                data["user_id"],
                f"✅ Оплата прошла успешно! Вы оформили подписку тариф {PLAN_NAME_MAP[data['plan']]} на {DURATION_NAME_MAP[data['duration']]}.",
            )
        await session.commit()
    else:
        await bot.send_message(
            data["object"]["metadata"]["user_id"],
            f"❌ Ошибка оплаты.",
        )
    return {"status": "ok"}
