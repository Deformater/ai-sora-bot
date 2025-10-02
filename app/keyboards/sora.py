from aiogram.utils.keyboard import InlineKeyboardBuilder

from app.callbacks.sora import (
    SoraCallback,
    SoraFormatCallback,
    SoraGenerationCallback,
    SoraQualityCallback,
)
from app.utils.enum import FORMAT_NAME_MAP

def sora_keyboard(chosen_quality: str, chosen_format: str):
    keyboard = InlineKeyboardBuilder()

    qualities = {
        "720p": None,
        "1080p": None,
    }
    qualities[chosen_quality] = True

    keyboard = InlineKeyboardBuilder()
    for quality_name in qualities:
        callback_name = quality_name
        if qualities[quality_name]:
            callback_name = "✅" + callback_name
        keyboard.button(
            text=callback_name,
            callback_data=SoraQualityCallback(value=quality_name).pack(),
        )
    
    formats = {
        "landscape": None,
        "portrait": None,
    }
    formats[chosen_format] = True

    for format_name in formats:
        callback_name = FORMAT_NAME_MAP[format_name]
        if formats[format_name]:
            callback_name = "✅" + callback_name
        keyboard.button(
            text=callback_name,
            callback_data=SoraFormatCallback(value=format_name).pack(),
        )

    keyboard.button(
        text=f"Продолжить",
        callback_data=SoraGenerationCallback(price=1).pack(),
    )

    keyboard.adjust(2, 2, 1)
    return keyboard.as_markup()


def sora_back_keyboard():
    keyboard = InlineKeyboardBuilder()
    keyboard.button(
        text="◀️ Назад",
        callback_data=SoraCallback().pack(),
    )
    return keyboard.as_markup()
