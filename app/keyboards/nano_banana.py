from aiogram.utils.keyboard import InlineKeyboardBuilder

from app.callback import PhotoCallback
from app.callbacks.nano_banana import NanoBananaCallback, NanoBananaGenerationCallback


def nano_banana_keyboard(cost: int):
    keyboard = InlineKeyboardBuilder()

    keyboard.button(
        text="◀️ Назад",
        callback_data=PhotoCallback().pack(),
    )
    keyboard.button(
        text=f"Начать генерацию - {cost}💎",
        callback_data=NanoBananaGenerationCallback(price=cost).pack(),
    )

    keyboard.adjust(1, 1)
    return keyboard.as_markup()


def nano_banana_back_keyboard():
    keyboard = InlineKeyboardBuilder()
    keyboard.button(
        text="◀️ Назад",
        callback_data=NanoBananaCallback().pack(),
    )
    return keyboard.as_markup()
