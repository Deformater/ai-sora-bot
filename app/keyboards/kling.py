from aiogram.utils.keyboard import InlineKeyboardBuilder

from app.callback import VideoCallback
from app.callbacks.kling import (
    KlingCallback,
    KlingDurationCallback,
    KlingFormatCallback,
    KlingGenerationCallback,
    KlingModelCallback,
    KlingVersionCallback,
)


def kling_keyboard(cost: int):
    keyboard = InlineKeyboardBuilder()

    keyboard.button(text="Формат видео", callback_data=KlingFormatCallback().pack())
    keyboard.button(text="Длина", callback_data=KlingDurationCallback().pack())
    keyboard.button(text="Версия", callback_data=KlingVersionCallback().pack())
    keyboard.button(text="Модель", callback_data=KlingModelCallback().pack())
    keyboard.button(
        text="◀️ Назад",
        callback_data=VideoCallback().pack(),
    )
    keyboard.button(
        text=f"Начать генерацию - {cost}💎",
        callback_data=KlingGenerationCallback(price=cost).pack(),
    )

    keyboard.adjust(2, 2, 1, 1)
    return keyboard.as_markup()


def kling_back_keyboard():
    keyboard = InlineKeyboardBuilder()
    keyboard.button(
        text="◀️ Назад",
        callback_data=KlingCallback().pack(),
    )
    return keyboard.as_markup()


def kling_format_keyboard(chosen_format: str):
    formats = {
        "16_9": None,
        "9_16": None,
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
            callback_data=KlingFormatCallback(value=format_name).pack(),
        )

    keyboard.button(
        text="◀️ Назад",
        callback_data=KlingCallback().pack(),
    )
    keyboard.adjust(3, 2)
    return keyboard.as_markup()


def kling_duration_keyboard(chosen_duration: str):
    durations = {
        "5": None,
        "10": None,
    }
    durations[chosen_duration] = True

    keyboard = InlineKeyboardBuilder()
    for duration_name in durations:
        callback_name = f"{duration_name}c"
        if durations[duration_name]:
            callback_name = "✅" + callback_name
        if durations[duration_name] is False:
            callback_name = "🔒" + callback_name
        keyboard.button(
            text=callback_name,
            callback_data=KlingDurationCallback(value=duration_name).pack(),
        )

    keyboard.button(
        text="◀️ Назад",
        callback_data=KlingCallback().pack(),
    )
    keyboard.adjust(2, 1)
    return keyboard.as_markup()


def kling_model_keyboard(chosen_model: str):
    models = {
        "STD": None,
        "PRO": None,
    }
    models[chosen_model] = True

    keyboard = InlineKeyboardBuilder()
    for model_name in models:
        callback_name = model_name
        if models[model_name]:
            callback_name = "✅" + callback_name
        keyboard.button(
            text=callback_name,
            callback_data=KlingModelCallback(value=model_name).pack(),
        )

    keyboard.button(
        text="◀️ Назад",
        callback_data=KlingCallback().pack(),
    )
    keyboard.adjust(2, 1)
    return keyboard.as_markup()


def kling_version_keyboard(chosen_version: str):
    models = {
        "1.0": None,
        "1.5": None,
        "1.6": None,
        "2.1-master": None,
    }
    models[chosen_version] = True

    keyboard = InlineKeyboardBuilder()
    for model_name in models:
        callback_name = model_name
        if models[model_name]:
            callback_name = "✅" + callback_name
        keyboard.button(
            text=callback_name,
            callback_data=KlingVersionCallback(value=model_name).pack(),
        )

    keyboard.button(
        text="◀️ Назад",
        callback_data=KlingCallback().pack(),
    )
    keyboard.adjust(4, 1)
    return keyboard.as_markup()
