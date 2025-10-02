from aiogram.filters.callback_data import CallbackData


class KlingCallback(CallbackData, prefix="kling"):
    pass


class KlingFormatCallback(CallbackData, prefix="kling_format"):
    value: str | None = None


class KlingDurationCallback(CallbackData, prefix="kling_duration"):
    value: str | None = None


class KlingModelCallback(CallbackData, prefix="kling_model"):
    value: str | None = None


class KlingVersionCallback(CallbackData, prefix="kling_version"):
    value: str | None = None


class KlingGenerationCallback(CallbackData, prefix="kling_generation"):
    price: int
