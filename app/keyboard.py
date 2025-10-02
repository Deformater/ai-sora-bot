from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder

from app.callback import (
    BuyCreditsCallback,
    ContinueCallback,
    CreateLinkCallback,
    MusicCallback,
    PhotoCallback,
    TryCallback,
    TypeBackCallback,
    VideoCallback,
)
from app.callbacks.flux import FluxCallback
from app.callbacks.gpt_image import GptImageCallback
from app.callbacks.kling import KlingCallback
from app.callbacks.mj_image import MjImageCallback
from app.callbacks.mj_video import MjVideoCallback
from app.callbacks.nano_banana import NanoBananaCallback
from app.callbacks.runway import RunwayCallback


def get_main_menu_keyboard():
    kb = ReplyKeyboardBuilder()
    kb.button(text="🎬 Создать видео")
    kb.button(text="💎 Получить генерации")
    kb.button(text="👤 Профиль")
    # kb.button(text="🎁 Бесплатные генерации")

    kb.adjust(1, 1, 1)
    return kb.as_markup(resize_keyboard=True)


def continue_keyboard():
    builder = InlineKeyboardBuilder()

    builder.button(text="Продолжить", callback_data=ContinueCallback())

    return builder.as_markup()


def buy_credits_keyboard():
    builder = InlineKeyboardBuilder()

    builder.button(text="💎 Получить генерации", callback_data=BuyCreditsCallback())

    return builder.as_markup()


def try_keyboard():
    builder = InlineKeyboardBuilder()

    builder.button(text="Выбрать модель", callback_data=TryCallback())

    return builder.as_markup()


def type_keyboard():
    keyboard = InlineKeyboardBuilder()

    keyboard.button(text="🖼 Работа с фото", callback_data=PhotoCallback())
    keyboard.button(text="📹 Видео будущего", callback_data=VideoCallback())
    # keyboard.button(text="🎵 ИИ Музыка", callback_data=MusicCallback())
    keyboard.adjust(1)
    return keyboard.as_markup()


def video_keyboard():
    keyboard = InlineKeyboardBuilder()

    keyboard.button(text="Veo3", url="https://t.me/ai_veo_bot")
    keyboard.button(text="Kling", callback_data=KlingCallback())
    keyboard.button(text="Midjourney Video", callback_data=MjVideoCallback().pack())
    keyboard.button(text="Runway", callback_data=RunwayCallback())
    keyboard.button(
        text="◀️ Назад",
        callback_data=TypeBackCallback(),
    )
    keyboard.adjust(1)
    return keyboard.as_markup()


def photo_keyboard():
    keyboard = InlineKeyboardBuilder()

    keyboard.button(text="GPT-4o Image", callback_data=GptImageCallback().pack())
    keyboard.button(text="Nano Banana", callback_data=NanoBananaCallback().pack())
    keyboard.button(text="Midjourney", callback_data=MjImageCallback().pack())
    keyboard.button(text="Flux", callback_data=FluxCallback().pack())
    keyboard.button(
        text="◀️ Назад",
        callback_data=TypeBackCallback(),
    )
    keyboard.adjust(1)
    return keyboard.as_markup()


def multix_keyboard():
    keyboard = InlineKeyboardBuilder()

    keyboard.button(text="Попробовать сейчас", url="https://t.me/multix_aibot")
    return keyboard.as_markup()


def vpn_keyboard():
    keyboard = InlineKeyboardBuilder()

    keyboard.button(text="Получить скидку", url="https://t.me/shrimpvpn_bot?start=veo")
    return keyboard.as_markup()


def admin_link_keyboard():
    builder = InlineKeyboardBuilder()

    builder.button(text="Создать ссылку", callback_data=CreateLinkCallback())

    return builder.as_markup()
