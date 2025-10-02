from aiogram.filters.callback_data import CallbackData


class SoraCallback(CallbackData, prefix="Sora"):
    pass


class SoraFormatCallback(CallbackData, prefix="sora_format"):
    value: str | None = None


class SoraQualityCallback(CallbackData, prefix="sora_quality"):
    value: str | None = None


class SoraGenerationCallback(CallbackData, prefix="sora_generation"):
    price: int
