from aiogram.utils.keyboard import InlineKeyboardBuilder

from app.callback import PhotoCallback
from app.callbacks.gpt_image import (
    GptImageCallback,
    GptImageEnhancePromptCallback,
    GptImageFormatCallback,
    GptImageGenerationCallback,
    GptImageNumberCallback,
)


def gpt_image_keyboard(cost: int, enhance_promt: bool):
    keyboard = InlineKeyboardBuilder()

    keyboard.button(text="Формат фото", callback_data=GptImageFormatCallback().pack())
    keyboard.button(
        text="Кол-во вариантов в ответе", callback_data=GptImageNumberCallback().pack()
    )
    enhance_btn_name = "Улучшить промпт"
    if enhance_promt:
        enhance_btn_name = "✅" + enhance_btn_name
    keyboard.button(
        text=enhance_btn_name,
        callback_data=GptImageEnhancePromptCallback(value=not enhance_promt).pack(),
    )
    keyboard.button(
        text="◀️ Назад",
        callback_data=PhotoCallback().pack(),
    )
    keyboard.button(
        text=f"Начать генерацию - {cost}💎",
        callback_data=GptImageGenerationCallback(price=cost).pack(),
    )

    keyboard.adjust(1, 1, 1, 1)
    return keyboard.as_markup()


def gpt_image_back_keyboard():
    keyboard = InlineKeyboardBuilder()
    keyboard.button(
        text="◀️ Назад",
        callback_data=GptImageCallback().pack(),
    )
    return keyboard.as_markup()


def gpt_image_format_keyboard(chosen_format: str):
    formats = {
        "3_2": None,
        "2_3": None,
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
            callback_data=GptImageFormatCallback(value=format_name).pack(),
        )

    keyboard.button(
        text="◀️ Назад",
        callback_data=GptImageCallback().pack(),
    )
    keyboard.adjust(2, 1, 1)
    return keyboard.as_markup()


def gpt_image_number_keyboard(chosen_number: int):
    numbers = {
        1: None,
        2: None,
        4: None,
    }
    numbers[chosen_number] = True

    keyboard = InlineKeyboardBuilder()
    for number in numbers:
        callback_name = str(number)
        if numbers[number]:
            callback_name = "✅" + callback_name
        keyboard.button(
            text=callback_name,
            callback_data=GptImageNumberCallback(value=number).pack(),
        )

    keyboard.button(
        text="◀️ Назад",
        callback_data=GptImageCallback().pack(),
    )
    keyboard.adjust(3, 1)
    return keyboard.as_markup()
