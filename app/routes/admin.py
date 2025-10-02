import logging
import random
import string

from aiogram import Bot, F, Router
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message, InputMediaPhoto
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder
from sqlalchemy.ext.asyncio import AsyncSession

from app.callback import CreateLinkCallback
from app.db.database import DatabaseManager
from app.keyboard import (
    multix_keyboard,
    try_keyboard,
    vpn_keyboard,
    admin_link_keyboard,
)
from app.texts.base import admin_link_text

admin_router = Router()
admin_states = {}
logger = logging.getLogger(__name__)
db = DatabaseManager


class LinkCreation(StatesGroup):
    waiting_for_name = State()


@admin_router.message(Command("admin"))
async def start_admin_broadcast(
    message: Message, bot: Bot, session: AsyncSession, album: list[Message] = None
):
    content = {}
    user = await db.get_user(session, message.chat.id)
    if not user.is_admin:
        return

    if album:
        content["type"] = "media_group"
        content["media"] = [
            InputMediaPhoto(media=msg.photo[-1].file_id) for msg in album if msg.photo
        ]
        content["caption"] = album[0].caption[7:] if album[0].caption else ""
    elif message.photo:
        content["type"] = "photo"
        content["file_id"] = message.photo[-1].file_id
        content["caption"] = message.caption[7:] or ""

    elif message.video:
        content["type"] = "video"
        content["file_id"] = message.video.file_id
        content["caption"] = message.caption[7:] or ""
    else:
        args = message.text.split(maxsplit=1)
        if len(args) < 2:
            await message.reply(
                "Пришлите сообщение (или фото/видео с подписью) для рассылки.\n"
                "/admin ваш_текст_или_медиа"
            )
            return
        content["type"] = "text"
        content["text"] = args[1]

    admin_states[message.from_user.id] = content

    builder = InlineKeyboardBuilder()
    builder.button(
        text="✅ Подтвердить и отправить", callback_data="admin_broadcast:confirm"
    )
    builder.button(text="❌ Отмена", callback_data="admin_broadcast:cancel")
    if content["type"] == "media_group":
        await bot.send_media_group(chat_id=message.chat.id, media=content["media"])
    elif content["type"] == "photo":
        await bot.send_photo(
            chat_id=message.chat.id,
            photo=content["file_id"],
            caption=content["caption"],
            reply_markup=builder.as_markup(),
        )
    elif content["type"] == "video":
        await bot.send_video(
            chat_id=message.chat.id,
            video=content["file_id"],
            caption=content["caption"],
            reply_markup=builder.as_markup(),
        )
    else:
        await message.answer(content["text"], reply_markup=builder.as_markup())


@admin_router.callback_query(F.data.startswith("admin_broadcast:"))
async def confirm_broadcast(callback: CallbackQuery, bot: Bot, session: AsyncSession):
    action = callback.data.split(":")[1]
    admin_id = callback.from_user.id
    user = await db.get_user(session, callback.from_user.id)
    if not user.is_admin:
        return

    if action == "cancel":
        admin_states.pop(admin_id, None)
        await callback.bot.send_message(admin_id, "Рассылка отменена.")
        return

    content = admin_states.get(admin_id)
    if not content:
        await callback.answer("Нет данных для рассылки.", show_alert=True)
        return

    users = await db.get_users(session)

    sent, failed = 0, 0

    for user in users:
        user_id = user.user_id
        try:
            if content["type"] == "media_group":
                await bot.send_media_group(
                    chat_id=user_id,
                    media=content["media"],
                )
            elif content["type"] == "photo":
                message = await bot.send_photo(
                    chat_id=user_id,
                    photo=content["file_id"],
                    caption=content["caption"],
                    reply_markup=try_keyboard(),
                )
                await message.pin()
            elif content["type"] == "video":
                message = await bot.send_video(
                    chat_id=user_id,
                    video=content["file_id"],
                    caption=content["caption"],
                    reply_markup=try_keyboard(),
                )
                await message.pin()

            else:
                await bot.send_message(
                    chat_id=user_id, text=content["text"], reply_markup=try_keyboard()
                )
            sent += 1
        except Exception as e:
            failed += 1

    await callback.bot.send_message(
        admin_id, f"✅ Рассылка завершена!\nУспешно: {sent}\nОшибки: {failed}"
    )
    admin_states.pop(admin_id, None)


@admin_router.message(Command("links"))
async def link_admin_command(message: Message, bot: Bot, session: AsyncSession):
    user = await db.get_user(session, message.chat.id)
    if not user.is_admin:
        return

    links = await db.get_links(session)
    await bot.send_message(
        chat_id=user.user_id,
        text=await admin_link_text(bot, links),
        reply_markup=admin_link_keyboard(),
    )


@admin_router.callback_query(CreateLinkCallback.filter())
async def create_admin_handler(
    callback: CallbackQuery, bot: Bot, state: FSMContext, session: AsyncSession
):
    user = await db.get_user(session, callback.message.chat.id)
    if not user.is_admin:
        return

    links = await db.get_links(session)
    await state.set_state(LinkCreation.waiting_for_name)

    await bot.send_message(chat_id=user.user_id, text="Введите имя ссылки:")


@admin_router.message(LinkCreation.waiting_for_name)
async def process_prompt(
    message: Message, state: FSMContext, session: AsyncSession, bot: Bot
):
    link_name = message.text if message.text else (message.caption or "")

    if not link_name:
        await message.answer("❌ Ошибка: не ввели имя")
        await state.clear()
        return

    link = "".join(random.choices(string.ascii_letters + string.digits, k=15))

    link = await db.add_link(session, link_name, link)
    await session.commit()

    await link_admin_command(message, bot, session)

    await state.clear()
