from aiogram.filters.callback_data import CallbackData


class FluxCallback(CallbackData, prefix="flux"):
    pass


class FluxFormatCallback(CallbackData, prefix="flux_format"):
    value: str | None = None


class FluxModelCallback(CallbackData, prefix="flux_model"):
    value: str | None = None


class FluxGenerationCallback(CallbackData, prefix="flux_generation"):
    price: int
