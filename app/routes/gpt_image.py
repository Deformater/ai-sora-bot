import logging
import json
from contextlib import aclosing

import aio_pika
import aiohttp
from aiogram import Bot, Router, types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from sqlalchemy.ext.asyncio import AsyncSession

from app.callbacks.gpt_image import (
    GptImageCallback,
    GptImageEnhancePromptCallback,
    GptImageFormatCallback,
    GptImageGenerationCallback,
    GptImageNumberCallback,
)
from app.config.utils import get_settings
from app.db.connection.session import get_session
from app.db.database import DatabaseManager
from app.db.models import GenerationRequest
from app.keyboard import buy_credits_keyboard
from app.keyboards.gpt_image import (
    gpt_image_back_keyboard,
    gpt_image_format_keyboard,
    gpt_image_keyboard,
    gpt_image_number_keyboard,
)
from app.services.gpt_image import GptImageService
from app.texts.gpt_image import (
    gpt_image_format_text,
    gpt_image_number_text,
    gpt_image_prompt_text,
    gpt_image_text,
)
from app.utils.enum import GenerationModels, GenerationRequestStatus
from app.utils.utils import send_images

logger = logging.getLogger(__name__)
gpt_image_router = Router()
settings = get_settings()

db = DatabaseManager


class GptImageGeneration(StatesGroup):
    choosing_props = State()
    waiting_for_prompt = State()


@gpt_image_router.callback_query(GptImageCallback.filter())
async def gpt_image_callback(
    callback: types.CallbackQuery, state: FSMContext, session: AsyncSession
):
    await state.set_state(GptImageGeneration.choosing_props)

    user_id = callback.from_user.id
    user = await db.get_user(session, user_id)

    if not user:
        await callback.bot.send_message(
            user_id, "❌ Вы не зарегистрированы. Используйте /start"
        )
        return

    gpt_image_options = await state.get_data()

    cost = 6
    format = gpt_image_options.get("format")
    if format is None:
        await state.update_data(format="3_2")
        format = "3_2"

    number = gpt_image_options.get("number")
    if number is None:
        await state.update_data(number=1)
        number = 1

    enhance_prompt = gpt_image_options.get("enhance_prompt")
    if enhance_prompt is None:
        await state.update_data(enhance_prompt=False)
        enhance_prompt = False

    if number == 2:
        cost = 7
    elif number == 4:
        cost = 8

    await callback.message.edit_text(
        gpt_image_text(format.replace("_", ":"), number, enhance_prompt),
        reply_markup=gpt_image_keyboard(cost, enhance_prompt),
    )


@gpt_image_router.callback_query(GptImageEnhancePromptCallback.filter())
async def gpt_image_callback(
    callback: types.CallbackQuery,
    callback_data: GptImageEnhancePromptCallback,
    state: FSMContext,
    session: AsyncSession,
):
    user_id = callback.from_user.id
    user = await db.get_user(session, user_id)

    if not user:
        await callback.bot.send_message(
            user_id, "❌ Вы не зарегистрированы. Используйте /start"
        )
        return

    gpt_image_options = await state.get_data()

    cost = 6
    format = gpt_image_options.get("format")
    if format is None:
        await state.update_data(format="3_2")
        format = "3_2"

    number = gpt_image_options.get("number")
    if number is None:
        await state.update_data(number=1)
        number = 1

    enhance_prompt = callback_data.value

    if number == 2:
        cost = 7
    elif number == 4:
        cost = 8

    await callback.message.edit_text(
        gpt_image_text(format.replace("_", ":"), number, enhance_prompt),
        reply_markup=gpt_image_keyboard(cost, enhance_prompt),
    )
    await state.update_data(enhance_prompt=enhance_prompt)


@gpt_image_router.callback_query(GptImageFormatCallback.filter())
async def gpt_image_format_callback(
    callback: types.CallbackQuery,
    callback_data: GptImageFormatCallback,
    state: FSMContext,
):
    choosen_format = callback_data.value
    if choosen_format is None:
        state_data = await state.get_data()
        choosen_format = state_data.get("format", "3_2")

    await state.update_data(format=choosen_format)

    await callback.message.edit_text(
        gpt_image_format_text(), reply_markup=gpt_image_format_keyboard(choosen_format)
    )


@gpt_image_router.callback_query(GptImageNumberCallback.filter())
async def gpt_image_number_callback(
    callback: types.CallbackQuery,
    callback_data: GptImageNumberCallback,
    state: FSMContext,
):
    choosen_number = callback_data.value
    if choosen_number is None:
        state_data = await state.get_data()
        choosen_number = state_data.get("number", 1)

    await callback.message.edit_text(
        gpt_image_number_text(),
        reply_markup=gpt_image_number_keyboard(choosen_number),
    )

    await state.update_data(number=choosen_number)


@gpt_image_router.callback_query(GptImageGenerationCallback.filter())
async def gpt_image_generate_callback(
    callback: types.CallbackQuery,
    callback_data: GptImageGenerationCallback,
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
        gpt_image_prompt_text(), reply_markup=gpt_image_back_keyboard()
    )
    await state.set_state(GptImageGeneration.waiting_for_prompt)
    await session.commit()


@gpt_image_router.message(GptImageGeneration.waiting_for_prompt)
async def gpt_image_rocess_prompt(
    message: types.Message, state: FSMContext, session: AsyncSession, bot: Bot
):
    user_id = message.from_user.id
    chat_id = message.chat.id

    data = await state.get_data()
    format = data.get("format")
    number = data.get("number")
    enhance_prompt = data.get("enhance_prompt")
    cost = data.get("cost")

    if not format or not number or enhance_prompt is None or not cost:
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

    file_urls = []

    if message.photo:
        photo = message.photo[-1]
        file = await bot.get_file(photo.file_id)
        image_url = f"https://api.telegram.org/file/bot{settings.TELEGRAM_TOKEN}/{file.file_path}"
        file_urls = [image_url]

    user = await db.get_user(session, user_id)
    if not user or user.credits < cost:
        await message.answer("❌ Недостаточно кредитов для генерации видео")
        await state.clear()
        return

    msg = await message.answer("🔄 Отправляем запрос на генерацию...")

    format = format.replace("_", ":")

    request_params = {
        "aspectRatio": format,
        "number": number,
        "enhance_prompt": enhance_prompt,
        "file_urls": file_urls,
    }

    generation_request = GenerationRequest(
        user_id=user_id,
        chat_id=chat_id,
        prompt=prompt,
        status=GenerationRequestStatus.PENDING,
        model=GenerationModels.GPT_IMAGE,
        api=settings.API_SOURCE,
        cost=cost,
        request_params=request_params,
    )
    try:
        task_id = GptImageService.generate_image(prompt, **request_params)

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


async def gpt_image_rabbitmq_consumer(bot: Bot):
    """Асинхронный потребитель RabbitMQ"""
    connection = await aio_pika.connect_robust(settings.rabbitmq_uri)

    async with connection:
        channel = await connection.channel()
        queue = await channel.declare_queue(GenerationModels.GPT_IMAGE, durable=True)

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
                            "Результат генерации Gpt-4o Image:",
                            bot,
                        )
                    else:
                        await bot.send_message(
                            chat_id=generation_request.chat_id,
                            text="❌ Ошибка генерации Gpt-4o Image: попробуйте переделать промт или поменять картинку и отправить запрос ещё раз, кредиты возвращены",
                        )
                except Exception as e:
                    logger.error(f"Error processing RabbitMQ message: {e}")
