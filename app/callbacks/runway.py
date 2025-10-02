from aiogram.filters.callback_data import CallbackData


class RunwayCallback(CallbackData, prefix="runway"):
    pass


class RunwayFormatCallback(CallbackData, prefix="runway_format"):
    value: str | None = None


class RunwayQualityCallback(CallbackData, prefix="runway_quality"):
    value: str | None = None


class RunwayDurationCallback(CallbackData, prefix="runway_duration"):
    value: str | None = None


class RunwayGenerationCallback(CallbackData, prefix="runway_generation"):
    price: int
