from contextlib import aclosing
import json
import logging

import aio_pika
from aiogram import Bot, Router, types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from sqlalchemy.ext.asyncio import AsyncSession

from app.callbacks.kling import (
    KlingCallback,
    KlingDurationCallback,
    KlingFormatCallback,
    KlingGenerationCallback,
    KlingModelCallback,
    KlingVersionCallback,
)
from app.config.utils import get_settings
from app.db.connection.session import get_session
from app.db.database import DatabaseManager
from app.db.models import GenerationRequest
from app.keyboard import buy_credits_keyboard
from app.keyboards.kling import (
    kling_back_keyboard,
    kling_duration_keyboard,
    kling_format_keyboard,
    kling_keyboard,
    kling_model_keyboard,
    kling_version_keyboard,
)
from app.services.kling import KlingService
from app.texts.kling import (
    kling_duration_text,
    kling_format_text,
    kling_prompt_text,
    kling_version_text,
    kling_model_text,
    kling_text,
)
from app.utils.enum import GenerationModels, GenerationRequestStatus

logger = logging.getLogger(__name__)
kling_router = Router()
settings = get_settings()

db = DatabaseManager


class KlingGeneration(StatesGroup):
    choosing_props = State()
    waiting_for_prompt = State()


@kling_router.callback_query(KlingCallback.filter())
async def kling_callback(
    callback: types.CallbackQuery, state: FSMContext, session: AsyncSession
):
    await state.set_state(KlingGeneration.choosing_props)

    user_id = callback.from_user.id
    user = await db.get_user(session, user_id)

    if not user:
        await callback.bot.send_message(
            user_id, "❌ Вы не зарегистрированы. Используйте /start"
        )
        return

    kling_options = await state.get_data()

    cost = 184

    model = kling_options.get("model")
    if model is None:
        await state.update_data(model="STD")
        model = "STD"

    version = kling_options.get("version")
    if version is None:
        await state.update_data(version="1.6")
        version = "1.6"

    format = kling_options.get("format")
    if format is None:
        await state.update_data(format="16_9")
        format = "16_9"

    duration = kling_options.get("duration")
    if duration is None:
        await state.update_data(duration="5")
        duration = "5"

    if version == "1.0":
        if model == "STD":
            cost = 26
        else:
            cost = 92
    elif version in ["1.5", "1.6"]:
        if model == "STD":
            cost = 52
        else:
            cost = 92

    if duration == "10":
        cost *= 2

    await callback.message.edit_text(
        kling_text(format.replace("_", ":"), duration, model, version),
        reply_markup=kling_keyboard(cost),
    )


@kling_router.callback_query(KlingFormatCallback.filter())
async def kling_format_callback(
    callback: types.CallbackQuery,
    callback_data: KlingFormatCallback,
    state: FSMContext,
):
    choosen_format = callback_data.value
    if choosen_format is None:
        state_data = await state.get_data()
        choosen_format = state_data.get("format", "16_9")

    await state.update_data(format=choosen_format)

    await callback.message.edit_text(
        kling_format_text(), reply_markup=kling_format_keyboard(choosen_format)
    )


@kling_router.callback_query(KlingModelCallback.filter())
async def kling_model_callback(
    callback: types.CallbackQuery,
    callback_data: KlingFormatCallback,
    state: FSMContext,
):
    choosen_model = callback_data.value
    if choosen_model is None:
        state_data = await state.get_data()
        choosen_model = state_data.get("model", "STD")

    await state.update_data(model=choosen_model)

    await callback.message.edit_text(
        kling_model_text(), reply_markup=kling_model_keyboard(choosen_model)
    )


@kling_router.callback_query(KlingVersionCallback.filter())
async def kling_version_callback(
    callback: types.CallbackQuery,
    callback_data: KlingFormatCallback,
    state: FSMContext,
):
    choosen_version = callback_data.value
    if choosen_version is None:
        state_data = await state.get_data()
        choosen_version = state_data.get("version", "1.6")

    await state.update_data(version=choosen_version)

    await callback.message.edit_text(
        kling_version_text(), reply_markup=kling_version_keyboard(choosen_version)
    )


@kling_router.callback_query(KlingDurationCallback.filter())
async def kling_duration_callback(
    callback: types.CallbackQuery,
    callback_data: KlingDurationCallback,
    state: FSMContext,
):
    choosen_duration = callback_data.value
    if choosen_duration is None:
        state_data = await state.get_data()
        choosen_duration = state_data.get("duration", "5")

    await callback.message.edit_text(
        kling_duration_text(),
        reply_markup=kling_duration_keyboard(choosen_duration),
    )
    await state.update_data(duration=choosen_duration)


@kling_router.callback_query(KlingGenerationCallback.filter())
async def kling_generate_callback(
    callback: types.CallbackQuery,
    callback_data: KlingGenerationCallback,
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
        kling_prompt_text(), reply_markup=kling_back_keyboard()
    )
    await state.set_state(KlingGeneration.waiting_for_prompt)
    await session.commit()


@kling_router.message(KlingGeneration.waiting_for_prompt)
async def process_prompt(
    message: types.Message, state: FSMContext, session: AsyncSession, bot: Bot
):
    user_id = message.from_user.id
    chat_id = message.chat.id

    data = await state.get_data()
    format = data.get("format")
    duration = data.get("duration")
    version = data.get("version")
    model = data.get("model")
    cost = data.get("cost")

    if not format or not duration or not cost or not version or not model:
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
        "version": version,
        "model": model,
        "duration": duration,
        "image_url": image_url,
    }

    generation_request = GenerationRequest(
        user_id=user_id,
        chat_id=chat_id,
        prompt=prompt,
        status=GenerationRequestStatus.PENDING,
        model=GenerationModels.KLING,
        api=settings.API_SOURCE,
        cost=cost,
        request_params=request_params,
    )
    await db.add_generation_request(session, generation_request)
    try:
        task_id = KlingService.generate_video(prompt, **request_params)

        generation_request.task_id = task_id
        generation_request.status = GenerationRequestStatus.PROCESSING

        user.credits -= cost

        await msg.edit_text(
            "Видео начало создаваться. Это займет несколько минут.\n"
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


async def kling_rabbitmq_consumer(bot: Bot):
    connection = await aio_pika.connect_robust(settings.rabbitmq_uri)

    async with connection:
        channel = await connection.channel()
        queue = await channel.declare_queue(GenerationModels.KLING, durable=True)

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
                        await bot.send_video(
                            generation_request.chat_id,
                            data["result_urls"][0],
                            caption="Результат генерации Kling:",
                        )
                    else:
                        await bot.send_message(
                            chat_id=generation_request.chat_id,
                            text="❌ Ошибка генерации Kling: попробуйте переделать промт или поменять картинку и отправить запрос ещё раз, кредиты возвращены",
                        )
                except Exception as e:
                    logger.error(f"Error processing RabbitMQ message: {e}")
