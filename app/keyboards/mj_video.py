from aiogram.utils.keyboard import InlineKeyboardBuilder

from app.callback import VideoCallback
from app.callbacks.mj_video import (
    MjVideoCallback,
    MjVideoFormatCallback,
    MjVideoGenerationCallback,
    MjVideoSpeedCallback,
    MjVideoStylizationCallback,
    MjVideoWeirdnessCallback,
)


def mj_video_keyboard(cost: int):
    keyboard = InlineKeyboardBuilder()

    keyboard.button(text="Формат видео", callback_data=MjVideoFormatCallback().pack())
    keyboard.button(
        text="Стилизация", callback_data=MjVideoStylizationCallback().pack()
    )
    keyboard.button(text="Странность", callback_data=MjVideoWeirdnessCallback().pack())
    keyboard.button(
        text="Скорость генерации", callback_data=MjVideoSpeedCallback().pack()
    )
    keyboard.button(
        text="◀️ Назад",
        callback_data=VideoCallback().pack(),
    )
    keyboard.button(
        text=f"Начать генерацию - {cost}💎",
        callback_data=MjVideoGenerationCallback(price=cost).pack(),
    )

    keyboard.adjust(1, 2, 1, 1)
    return keyboard.as_markup()


def mj_video_back_keyboard():
    keyboard = InlineKeyboardBuilder()
    keyboard.button(
        text="◀️ Назад",
        callback_data=MjVideoCallback().pack(),
    )
    return keyboard.as_markup()


def mj_video_format_keyboard(chosen_format: str):
    formats = {
        "16_9": None,
        "9_16": None,
        "6_5": None,
        "5_6": None,
        "4_3": None,
        "3_4": None,
        "3_2": None,
        "2_3": None,
        "2_1": None,
        "1_2": None,
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
            callback_data=MjVideoFormatCallback(value=format_name).pack(),
        )

    keyboard.button(
        text="◀️ Назад",
        callback_data=MjVideoCallback().pack(),
    )
    keyboard.adjust(2, 2, 2, 2, 2, 1)
    return keyboard.as_markup()


def mj_video_speed_keyboard(chosen_speed: str):
    speeds = {"relaxed": None, "fast": None, "turbo": None}
    speeds[chosen_speed] = True

    keyboard = InlineKeyboardBuilder()
    for spped in speeds:
        callback_name = spped
        if speeds[spped]:
            callback_name = "✅" + callback_name
        keyboard.button(
            text=callback_name,
            callback_data=MjVideoSpeedCallback(value=spped).pack(),
        )

    keyboard.button(
        text="◀️ Назад",
        callback_data=MjVideoCallback().pack(),
    )
    keyboard.adjust(3, 1)
    return keyboard.as_markup()


def mj_video_stylization_keyboard(chosen_stylization: str):
    stylizations = {0: None, 1: None, 2: None, 3: None, 4: None, 5: None}
    stylizations[chosen_stylization] = True

    keyboard = InlineKeyboardBuilder()
    for stylization in stylizations:
        callback_name = str(stylization)
        if stylizations[stylization]:
            callback_name = "✅" + callback_name
        keyboard.button(
            text=callback_name,
            callback_data=MjVideoStylizationCallback(value=stylization).pack(),
        )

    keyboard.button(
        text="◀️ Назад",
        callback_data=MjVideoCallback().pack(),
    )
    keyboard.adjust(6, 1)
    return keyboard.as_markup()


def mj_video_weirdness_keyboard(chosen_weirdness: str):
    weirdnesses = {0: None, 1: None, 2: None, 3: None, 4: None, 5: None}
    weirdnesses[chosen_weirdness] = True

    keyboard = InlineKeyboardBuilder()
    for weirdness in weirdnesses:
        callback_name = str(weirdness)
        if weirdnesses[weirdness]:
            callback_name = "✅" + callback_name
        keyboard.button(
            text=callback_name,
            callback_data=MjVideoWeirdnessCallback(value=weirdness).pack(),
        )

    keyboard.button(
        text="◀️ Назад",
        callback_data=MjVideoCallback().pack(),
    )
    keyboard.adjust(6, 1)
    return keyboard.as_markup()
