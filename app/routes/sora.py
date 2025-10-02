from contextlib import aclosing
import json
import logging

import aio_pika
from aiogram import F, Bot, Router, types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from sqlalchemy.ext.asyncio import AsyncSession

from app.callbacks.sora import (
    SoraCallback,
    SoraFormatCallback,
    SoraGenerationCallback,
    SoraQualityCallback,
)
from app.config.utils import get_settings
from app.db.connection.session import get_session
from app.db.database import DatabaseManager
from app.db.models import GenerationRequest
from app.keyboard import buy_credits_keyboard
from app.keyboards.sora import sora_back_keyboard, sora_keyboard
from app.services.sora import SoraService
from app.texts.sora import (
    sora_prompt_text,
    sora_text,
)
from app.utils.enum import GenerationModels, GenerationRequestStatus

logger = logging.getLogger(__name__)
sora_router = Router()
settings = get_settings()

db = DatabaseManager


class SoraGeneration(StatesGroup):
    choosing_props = State()
    waiting_for_prompt = State()


@sora_router.callback_query(SoraCallback.filter())
async def sora_callback(
    callback: types.CallbackQuery, state: FSMContext, session: AsyncSession
):
    await state.set_state(SoraGeneration.choosing_props)

    user_id = callback.from_user.id
    user = await db.get_user(session, user_id)

    if not user:
        await callback.bot.send_message(
            user_id, "❌ Вы не зарегистрированы. Используйте /start"
        )
        return

    sora_options = await state.get_data()

    format = sora_options.get("format")
    if format is None:
        await state.update_data(format="landscape")
        format = "landscape"

    quality = sora_options.get("quality")
    if quality is None:
        await state.update_data(quality="720p")
        quality = "720p"
    
    await callback.message.edit_text(
        sora_text(format, quality),
        reply_markup=sora_keyboard(quality, format),
    )


@sora_router.message(F.text == "🎬 Создать видео")
async def sora_callback(
    message: types.Message, state: FSMContext, session: AsyncSession
):
    await state.set_state(SoraGeneration.choosing_props)

    user_id = message.from_user.id
    user = await db.get_user(session, user_id)

    if not user:
        await message.bot.send_message(
            user_id, "❌ Вы не зарегистрированы. Используйте /start"
        )
        return

    sora_options = await state.get_data()

    format = sora_options.get("format")
    if format is None:
        await state.update_data(format="landscape")
        format = "landscape"

    quality = sora_options.get("quality")
    if quality is None:
        await state.update_data(quality="720p")
        quality = "720p"
    
    await message.bot.send_message(
        user_id,
        sora_text(format, quality),
        reply_markup=sora_keyboard(quality, format),
    )

@sora_router.callback_query(SoraFormatCallback.filter())
async def sora_format_callback(
    callback: types.CallbackQuery,
    callback_data: SoraFormatCallback,
    state: FSMContext,
):
    choosen_format = callback_data.value
    state_data = await state.get_data()

    if choosen_format is None:
        choosen_format = state_data.get("format", "landscape")

    quality = state_data.get("quality")
    if quality is None:
        await state.update_data(quality="720p")
        quality = "720p"

    await state.update_data(format=choosen_format)

    await callback.message.edit_text(
        sora_text(choosen_format, quality),
        reply_markup=sora_keyboard(quality, choosen_format),
    )


@sora_router.callback_query(SoraQualityCallback.filter())
async def sora_quality_callback(
    callback: types.CallbackQuery,
    callback_data: SoraQualityCallback,
    state: FSMContext,
):
    state_data = await state.get_data()

    choosen_quality = callback_data.value
    if choosen_quality is None:
        choosen_quality = state_data.get("quality", "720p")

    format = state_data.get("format")
    if format is None:
        await state.update_data(format="landscape")
        format = "landscape"

    await state.update_data(quality=choosen_quality)

    await callback.message.edit_text(
        sora_text(format, choosen_quality),
        reply_markup=sora_keyboard(choosen_quality, format),
    )


@sora_router.callback_query(SoraGenerationCallback.filter())
async def sora_generate_callback(
    callback: types.CallbackQuery,
    callback_data: SoraGenerationCallback,
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
            f"❌ Недостаточно генераций",
            reply_markup=buy_credits_keyboard(),
        )
        await state.clear()
        return

    await state.update_data(cost=cost)

    await callback.message.edit_text(
        sora_prompt_text(), reply_markup=sora_back_keyboard()
    )
    await state.set_state(SoraGeneration.waiting_for_prompt)
    await session.commit()


@sora_router.message(SoraGeneration.waiting_for_prompt)
async def process_prompt(
    message: types.Message, state: FSMContext, session: AsyncSession, bot: Bot
):
    user_id = message.from_user.id
    chat_id = message.chat.id

    data = await state.get_data()
    format = data.get("format")
    quality = data.get("quality")
    cost = 1

    if not format or not quality:
        await message.answer("❌ Ошибка: не выбрана модель генерации")
        await state.clear()
        return

    prompt = message.text if message.text else (message.caption or "")
    image_url = None

    if len(prompt) < 10:
        await message.answer("❌ Описание слишком короткое. Минимум 10 символов.")
        return

    if len(prompt) > 2500:
        await message.answer("❌ Описание слишком длинное. Максимум 2500 символов.")
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
        await message.answer("❌ У вас не хватает генераций!")
        await state.clear()
        return

    msg = await message.answer("🔄 Отправляем запрос на генерацию...")

    format = format.replace("_", ":")

    request_params = {
        "format": format,
        "quality": quality,
        "inputImage": image_url,
    }

    generation_request = GenerationRequest(
        user_id=user_id,
        chat_id=chat_id,
        prompt=prompt,
        status=GenerationRequestStatus.PENDING,
        model=GenerationModels.SORA,
        api=settings.API_SOURCE,
        cost=cost,
        request_params=request_params,
    )
    await db.add_generation_request(session, generation_request)
    try:
        task_id = SoraService.generate_video(prompt, **request_params)

        generation_request.task_id = task_id
        generation_request.status = GenerationRequestStatus.PROCESSING

        user.credits -= cost

        await msg.edit_text(
            "Видео начало создаваться. Это займет несколько минут.\n"
            f"Остаток: {user.credits} генераций"
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


async def sora_rabbitmq_consumer(bot: Bot):
    connection = await aio_pika.connect_robust(settings.rabbitmq_uri)

    async with connection:
        channel = await connection.channel()
        queue = await channel.declare_queue(GenerationModels.SORA, durable=True)

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
                            caption="Результат генерации Sora:",
                        )
                    else:
                        await bot.send_message(
                            chat_id=generation_request.chat_id,
                            text="❌ Ошибка генерации Sora: попробуйте переделать промт или поменять картинку и отправить запрос ещё раз, кредиты возвращены",
                        )
                except Exception as e:
                    logger.error(f"Error processing RabbitMQ message: {e}")
