from aiogram.utils.keyboard import InlineKeyboardBuilder

from app.callback import VideoCallback
from app.callbacks.runway import (
    RunwayCallback,
    RunwayDurationCallback,
    RunwayFormatCallback,
    RunwayGenerationCallback,
    RunwayQualityCallback,
)


def runway_keyboard(cost: int):
    keyboard = InlineKeyboardBuilder()

    keyboard.button(text="Формат видео", callback_data=RunwayFormatCallback().pack())
    keyboard.button(text="Качество", callback_data=RunwayQualityCallback().pack())
    keyboard.button(text="Длина", callback_data=RunwayDurationCallback().pack())
    keyboard.button(
        text="◀️ Назад",
        callback_data=VideoCallback().pack(),
    )
    keyboard.button(
        text=f"Начать генерацию - {cost}💎",
        callback_data=RunwayGenerationCallback(price=cost).pack(),
    )

    keyboard.adjust(2, 1, 1, 1)
    return keyboard.as_markup()


def runway_back_keyboard():
    keyboard = InlineKeyboardBuilder()
    keyboard.button(
        text="◀️ Назад",
        callback_data=RunwayCallback().pack(),
    )
    return keyboard.as_markup()


def runway_format_keyboard(chosen_format: str):
    formats = {
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
            callback_data=RunwayFormatCallback(value=format_name).pack(),
        )

    keyboard.button(
        text="◀️ Назад",
        callback_data=RunwayCallback().pack(),
    )
    keyboard.adjust(2, 2, 1, 1)
    return keyboard.as_markup()


def runway_quality_keyboard(chosen_quality: str, block_1080p=False):
    qualities = {
        "720p": None,
        "1080p": None,
    }
    qualities[chosen_quality] = True
    if block_1080p:
        qualities["1080p"] = False

    keyboard = InlineKeyboardBuilder()
    for quality_name in qualities:
        callback_name = quality_name
        if qualities[quality_name]:
            callback_name = "✅" + callback_name
        if qualities[quality_name] is False:
            callback_name = "🔒" + callback_name
        keyboard.button(
            text=callback_name,
            callback_data=RunwayQualityCallback(value=quality_name).pack(),
        )

    keyboard.button(
        text="◀️ Назад",
        callback_data=RunwayCallback().pack(),
    )
    keyboard.adjust(2, 1)
    return keyboard.as_markup()


def runway_duration_keyboard(chosen_duration: str, block_8=False):
    durations = {
        "5": None,
        "8": None,
    }
    durations[chosen_duration] = True
    if block_8:
        durations["8"] = False

    keyboard = InlineKeyboardBuilder()
    for duration_name in durations:
        callback_name = f"{duration_name}c"
        if durations[duration_name]:
            callback_name = "✅" + callback_name
        if durations[duration_name] is False:
            callback_name = "🔒" + callback_name
        keyboard.button(
            text=callback_name,
            callback_data=RunwayDurationCallback(value=duration_name).pack(),
        )

    keyboard.button(
        text="◀️ Назад",
        callback_data=RunwayCallback().pack(),
    )
    keyboard.adjust(2, 1)
    return keyboard.as_markup()
