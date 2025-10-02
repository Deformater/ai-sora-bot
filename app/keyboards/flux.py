from aiogram.utils.keyboard import InlineKeyboardBuilder

from app.callback import PhotoCallback
from app.callbacks.flux import (
    FluxCallback,
    FluxFormatCallback,
    FluxGenerationCallback,
    FluxModelCallback,
)


def flux_keyboard(cost: int):
    keyboard = InlineKeyboardBuilder()

    keyboard.button(text="Формат фото", callback_data=FluxFormatCallback().pack())
    keyboard.button(text="Выбрать модель", callback_data=FluxModelCallback().pack())
    keyboard.button(
        text="◀️ Назад",
        callback_data=PhotoCallback().pack(),
    )
    keyboard.button(
        text=f"Начать генерацию - {cost}💎",
        callback_data=FluxGenerationCallback(price=cost).pack(),
    )

    keyboard.adjust(2, 1, 1, 1)
    return keyboard.as_markup()


def flux_back_keyboard():
    keyboard = InlineKeyboardBuilder()
    keyboard.button(
        text="◀️ Назад",
        callback_data=FluxCallback().pack(),
    )
    return keyboard.as_markup()


def flux_format_keyboard(chosen_format: str):
    formats = {
        "21_9": None,
        "9_21": None,
        "16_9": None,
        "9_16": None,
        "4_3": None,
        "3_4": None,
        "1_1": None,
    }
    formats[chosen_format] = True

    keyboard = InlineKeyboardBuilder()
    for format_name in formats:
        callback_name = format_name.replace("_", ":")
        if formats[format_name]:
            callback_name = "✅" + callback_name
        keyboard.button(
            text=callback_name,
            callback_data=FluxFormatCallback(value=format_name).pack(),
        )

    keyboard.button(
        text="◀️ Назад",
        callback_data=FluxCallback().pack(),
    )
    keyboard.adjust(2, 2, 2, 1)
    return keyboard.as_markup()


def flux_model_keyboard(chosen_model: str):
    models = {
        "PRO": None,
        "MAX": None,
    }
    models[chosen_model] = True

    keyboard = InlineKeyboardBuilder()
    for model_name in models:
        callback_name = model_name
        if models[model_name]:
            callback_name = "✅" + callback_name
        keyboard.button(
            text=callback_name,
            callback_data=FluxModelCallback(value=model_name).pack(),
        )

    keyboard.button(
        text="◀️ Назад",
        callback_data=FluxCallback().pack(),
    )
    keyboard.adjust(2, 1)
    return keyboard.as_markup()
