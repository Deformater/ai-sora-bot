import logging
import json
from contextlib import aclosing

import aio_pika
import aiohttp
from aiogram import Bot, Router, types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from sqlalchemy.ext.asyncio import AsyncSession

from app.callbacks.flux import (
    FluxCallback,
    FluxFormatCallback,
    FluxGenerationCallback,
    FluxModelCallback,
)
from app.config.utils import get_settings
from app.db.connection.session import get_session
from app.db.database import DatabaseManager
from app.db.models import GenerationRequest
from app.keyboard import buy_credits_keyboard
from app.keyboards.flux import (
    flux_back_keyboard,
    flux_format_keyboard,
    flux_keyboard,
    flux_model_keyboard,
)
from app.services.flux import FluxService
from app.texts.flux import (
    flux_format_text,
    flux_model_text,
    flux_prompt_text,
    flux_text,
)
from app.utils.enum import GenerationModels, GenerationRequestStatus
from app.utils.utils import send_images

logger = logging.getLogger(__name__)
flux_router = Router()
settings = get_settings()

db = DatabaseManager


class FluxGeneration(StatesGroup):
    choosing_props = State()
    waiting_for_prompt = State()


@flux_router.callback_query(FluxCallback.filter())
async def flux_image_callback(
    callback: types.CallbackQuery, state: FSMContext, session: AsyncSession
):
    await state.set_state(FluxGeneration.choosing_props)

    user_id = callback.from_user.id
    user = await db.get_user(session, user_id)

    if not user:
        await callback.bot.send_message(
            user_id, "❌ Вы не зарегистрированы. Используйте /start"
        )
        return

    flux_options = await state.get_data()

    cost = 5
    format = flux_options.get("format")
    if format is None:
        await state.update_data(format="16_9")
        format = "16_9"

    model = flux_options.get("model")
    if model is None:
        await state.update_data(model="PRO")
        model = "PRO"

    if model == "PRO":
        cost = 5
    elif model == "MAX":
        cost = 10

    await callback.message.edit_text(
        flux_text(format.replace("_", ":"), model),
        reply_markup=flux_keyboard(cost),
    )


@flux_router.callback_query(FluxFormatCallback.filter())
async def flux_format_callback(
    callback: types.CallbackQuery,
    callback_data: FluxFormatCallback,
    state: FSMContext,
):
    choosen_format = callback_data.value
    if choosen_format is None:
        state_data = await state.get_data()
        choosen_format = state_data.get("format", "16_9")

    await state.update_data(format=choosen_format)

    await callback.message.edit_text(
        flux_format_text(), reply_markup=flux_format_keyboard(choosen_format)
    )


@flux_router.callback_query(FluxModelCallback.filter())
async def flux_model_callback(
    callback: types.CallbackQuery,
    callback_data: FluxModelCallback,
    state: FSMContext,
):
    choosen_model = callback_data.value
    if choosen_model is None:
        state_data = await state.get_data()
        choosen_model = state_data.get("model", "PRO")

    await state.update_data(model=choosen_model)

    await callback.message.edit_text(
        flux_model_text(), reply_markup=flux_model_keyboard(choosen_model)
    )


@flux_router.callback_query(FluxGenerationCallback.filter())
async def flux_generate_callback(
    callback: types.CallbackQuery,
    callback_data: FluxGenerationCallback,
    state: FSMContext,
    session: AsyncSession,
):
    cost = callback_data.price

    if not cost:
        await callback.message.answer("❌ Неизвестная модель генерации")
        await state.clear()
        return

    user_id = callback.from_user.id
    user = await db.get_user(session, user_id)

    if user.credits < cost:
        await callback.message.edit_text(
            f"❌ Недостаточно кредитов!\n\n"
            f"Требуется: {cost}, доступно: {user.credits}",
            reply_markup=buy_credits_keyboard(),
        )
        await state.clear()
        return

    await state.update_data(cost=cost)

    await callback.message.edit_text(
        flux_prompt_text(), reply_markup=flux_back_keyboard()
    )
    await state.set_state(FluxGeneration.waiting_for_prompt)
    await session.commit()


@flux_router.message(FluxGeneration.waiting_for_prompt)
async def flux_rocess_prompt(
    message: types.Message, state: FSMContext, session: AsyncSession, bot: Bot
):
    user_id = message.from_user.id
    chat_id = message.chat.id

    data = await state.get_data()
    format = data.get("format")
    model = data.get("model")
    cost = data.get("cost")

    if not format or not model or not cost:
        await message.answer("❌ Ошибка: не выбрана модель генерации")
        await state.clear()
        return

    prompt = message.text if message.text else (message.caption or "")
    image_url = None

    if len(prompt) < 10:
        await message.answer("❌ Описание слишком короткое. Минимум 10 символов.")
        return

    if len(prompt) > 2000:
        await message.answer("❌ Описание слишком длинное. Максимум 2000 символов.")
        return

    if message.video:
        await message.answer("❌ Нельзя прикрепить видео, попробуйте ещё раз:")
        return

    if (
        message.document
        or message.audio
        or message.voice
        or message.sticker
        or message.animation
    ):
        await message.answer("❌ Нельзя прикреплять файлы, попробуйте ещё раз:")
        return

    if message.photo:
        photo = message.photo[-1]
        file = await bot.get_file(photo.file_id)
        image_url = f"https://api.telegram.org/file/bot{settings.TELEGRAM_TOKEN}/{file.file_path}"

    user = await db.get_user(session, user_id)
    if not user or user.credits < cost:
        await message.answer("❌ Недостаточно кредитов для генерации видео")
        await state.clear()
        return

    msg = await message.answer("🔄 Отправляем запрос на генерацию...")

    format = format.replace("_", ":")

    request_params = {
        "aspectRatio": format,
        "model": model,
        "inputImage": image_url,
    }

    generation_request = GenerationRequest(
        user_id=user_id,
        chat_id=chat_id,
        prompt=prompt,
        status=GenerationRequestStatus.PENDING,
        model=GenerationModels.FLUX,
        api=settings.API_SOURCE,
        cost=cost,
        request_params=request_params,
    )
    try:
        task_id = FluxService.generate_image(prompt, **request_params)

        generation_request.task_id = task_id
        generation_request.status = GenerationRequestStatus.PROCESSING

        user.credits -= cost

        await msg.edit_text(
            "Фото начало создаваться. Это займет несколько минут.\n"
            f"Списано кредитов: {cost}\n"
            f"Остаток: {user.credits}"
        )
        await state.clear()
    except Exception as e:
        generation_request.status = GenerationRequestStatus.FAILED
        generation_request.msg = str(e)
        logger.error(f"Ошибка при запуске генерации: {str(e)}")

        await msg.edit_text(
            "❌ Ошибка генерации видео: попробуйте переделать промт или поменять картинку и отправить запрос ещё раз:"
        )

    session.add(generation_request)
    await session.commit()


async def flux_rabbitmq_consumer(bot: Bot):
    """Асинхронный потребитель RabbitMQ"""
    connection = await aio_pika.connect_robust(settings.rabbitmq_uri)

    async with connection:
        channel = await connection.channel()
        queue = await channel.declare_queue(GenerationModels.FLUX, durable=True)

        async for message in queue:
            async with message.process():
                try:
                    data = json.loads(message.body.decode())
                    logger.info(f"Received RabbitMQ message: {data}")
                    async with aclosing(get_session()) as sessions:
                        async for session in sessions:
                            generation_request = await db.get_request_by_task_id(
                                session, data["task_id"]
                            )
                            if data["status"] != GenerationRequestStatus.COMPLETED:
                                user = await db.get_user(
                                    session, generation_request.chat_id
                                )
                                user.credits += generation_request.cost
                                generation_request.status = (
                                    GenerationRequestStatus.FAILED
                                )
                                generation_request.msg = data["msg"]

                                session.add(user)
                            else:
                                generation_request.status = (
                                    GenerationRequestStatus.COMPLETED
                                )
                                generation_request.result_urls = data["result_urls"]

                            session.add(generation_request)
                            await session.commit()

                            break

                    if data["status"] == GenerationRequestStatus.COMPLETED:
                        await send_images(
                            generation_request.chat_id,
                            data["result_urls"],
                            "Результат генерации Flux:",
                            bot,
                        )
                    else:
                        await bot.send_message(
                            chat_id=generation_request.chat_id,
                            text="❌ Ошибка генерации Flux: попробуйте переделать промт или поменять картинку и отправить запрос ещё раз, кредиты возвращены",
                        )
                except Exception as e:
                    logger.error(f"Error processing RabbitMQ message: {e}")
