from aiogram.filters.callback_data import CallbackData


class MjVideoCallback(CallbackData, prefix="mj_video"):
    pass


class MjVideoFormatCallback(CallbackData, prefix="mj_video_format"):
    value: str | None = None


class MjVideoSpeedCallback(CallbackData, prefix="mj_video_speed"):
    value: str | None = None


class MjVideoStylizationCallback(CallbackData, prefix="mj_video_stylization"):
    value: int | None = None


class MjVideoWeirdnessCallback(CallbackData, prefix="mj_video_weirdness"):
    value: int | None = None


class MjVideoGenerationCallback(CallbackData, prefix="mj_video_generation"):
    price: int
