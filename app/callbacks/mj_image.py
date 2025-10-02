from aiogram.filters.callback_data import CallbackData


class MjImageCallback(CallbackData, prefix="mj_image"):
    pass


class MjImageFormatCallback(CallbackData, prefix="mj_image_format"):
    value: str | None = None


class MjImageSpeedCallback(CallbackData, prefix="mj_image_speed"):
    value: str | None = None


class MjImageStylizationCallback(CallbackData, prefix="mj_image_stylization"):
    value: int | None = None


class MjImageWeirdnessCallback(CallbackData, prefix="mj_image_weirdness"):
    value: int | None = None


class MjImageGenerationCallback(CallbackData, prefix="mj_image_generation"):
    price: int
