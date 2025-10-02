from contextlib import aclosing
import json
import logging

import aio_pika
from aiogram import Bot, Router, types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from sqlalchemy.ext.asyncio import AsyncSession

from app.callbacks.runway import (
    RunwayCallback,
    RunwayDurationCallback,
    RunwayFormatCallback,
    RunwayGenerationCallback,
    RunwayQualityCallback,
)
from app.config.utils import get_settings
from app.db.connection.session import get_session
from app.db.database import DatabaseManager
from app.db.models import GenerationRequest
from app.keyboard import buy_credits_keyboard
from app.keyboards.runway import (
    runway_back_keyboard,
    runway_duration_keyboard,
    runway_format_keyboard,
    runway_keyboard,
    runway_quality_keyboard,
)
from app.services.runway import RunwayService
from app.texts.runway import (
    runway_duration_text,
    runway_format_text,
    runway_prompt_text,
    runway_quality_text,
    runway_text,
)
from app.utils.enum import GenerationModels, GenerationRequestStatus

logger = logging.getLogger(__name__)
runway_router = Router()
settings = get_settings()

db = DatabaseManager


class RunwayGeneration(StatesGroup):
    choosing_props = State()
    waiting_for_prompt = State()


@runway_router.callback_query(RunwayCallback.filter())
async def runway_callback(
    callback: types.CallbackQuery, state: FSMContext, session: AsyncSession
):
    await state.set_state(RunwayGeneration.choosing_props)

    user_id = callback.from_user.id
    user = await db.get_user(session, user_id)

    if not user:
        await callback.bot.send_message(
            user_id, "❌ Вы не зарегистрированы. Используйте /start"
        )
        return

    runway_options = await state.get_data()

    cost = 12
    format = runway_options.get("format")
    if format is None:
        await state.update_data(format="16_9")
        format = "16_9"

    quality = runway_options.get("quality")
    if quality is None:
        await state.update_data(quality="720p")
        quality = "720p"

    duration = runway_options.get("duration")
    if duration is None:
        await state.update_data(duration="5")
        duration = "5"

    if quality == "1080p" or duration == "8":
        cost = 30

    await callback.message.edit_text(
        runway_text(format.replace("_", ":"), quality, duration),
        reply_markup=runway_keyboard(cost),
    )


@runway_router.callback_query(RunwayFormatCallback.filter())
async def runway_format_callback(
    callback: types.CallbackQuery,
    callback_data: RunwayFormatCallback,
    state: FSMContext,
):
    choosen_format = callback_data.value
    if choosen_format is None:
        state_data = await state.get_data()
        choosen_format = state_data.get("format", "16_9")

    await state.update_data(format=choosen_format)

    await callback.message.edit_text(
        runway_format_text(), reply_markup=runway_format_keyboard(choosen_format)
    )


@runway_router.callback_query(RunwayQualityCallback.filter())
async def runway_quality_callback(
    callback: types.CallbackQuery,
    callback_data: RunwayQualityCallback,
    state: FSMContext,
):
    state_data = await state.get_data()
    duration = state_data.get("duration", "5")

    choosen_quality = callback_data.value
    if choosen_quality is None or duration == "8":
        choosen_quality = state_data.get("quality", "720p")

    await callback.message.edit_text(
        runway_quality_text(),
        reply_markup=runway_quality_keyboard(
            choosen_quality, block_1080p=duration == "8"
        ),
    )

    await state.update_data(quality=choosen_quality)


@runway_router.callback_query(RunwayDurationCallback.filter())
async def runway_duration_callback(
    callback: types.CallbackQuery,
    callback_data: RunwayDurationCallback,
    state: FSMContext,
):
    state_data = await state.get_data()
    quality = state_data.get("quality", "720p")

    choosen_duration = callback_data.value
    if choosen_duration is None or quality == "1080p":
        choosen_duration = state_data.get("duration", "5")

    await callback.message.edit_text(
        runway_duration_text(),
        reply_markup=runway_duration_keyboard(
            choosen_duration, block_8=quality == "1080p"
        ),
    )
    await state.update_data(duration=choosen_duration)


@runway_router.callback_query(RunwayGenerationCallback.filter())
async def runway_generate_callback(
    callback: types.CallbackQuery,
    callback_data: RunwayGenerationCallback,
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
        runway_prompt_text(), reply_markup=runway_back_keyboard()
    )
    await state.set_state(RunwayGeneration.waiting_for_prompt)
    await session.commit()


@runway_router.message(RunwayGeneration.waiting_for_prompt)
async def process_prompt(
    message: types.Message, state: FSMContext, session: AsyncSession, bot: Bot
):
    user_id = message.from_user.id
    chat_id = message.chat.id

    data = await state.get_data()
    format = data.get("format")
    quality = data.get("quality")
    duration = data.get("duration")
    cost = data.get("cost")

    if not format or not quality or not duration or not cost:
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
        "duration": duration,
        "quality": quality,
        "image_url": image_url,
    }

    generation_request = GenerationRequest(
        user_id=user_id,
        chat_id=chat_id,
        prompt=prompt,
        status=GenerationRequestStatus.PENDING,
        model=GenerationModels.RUNWAY,
        api=settings.API_SOURCE,
        cost=cost,
        request_params=request_params,
    )
    await db.add_generation_request(session, generation_request)
    try:
        task_id = RunwayService.generate_video(prompt, **request_params)

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


async def runway_rabbitmq_consumer(bot: Bot):
    connection = await aio_pika.connect_robust(settings.rabbitmq_uri)

    async with connection:
        channel = await connection.channel()
        queue = await channel.declare_queue(GenerationModels.RUNWAY, durable=True)

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
                            caption="Результат генерации Runway:",
                        )
                    else:
                        await bot.send_message(
                            chat_id=generation_request.chat_id,
                            text="❌ Ошибка генерации Runway: попробуйте переделать промт или поменять картинку и отправить запрос ещё раз, кредиты возвращены",
                        )
                except Exception as e:
                    logger.error(f"Error processing RabbitMQ message: {e}")
