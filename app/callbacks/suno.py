from aiogram.filters.callback_data import CallbackData


class SunoCallback(CallbackData, prefix="suno"):
    pass


class SunoModeCallback(CallbackData, prefix="suno_mode"):
    value: str | None = None


class SunoInstrumentalCallback(CallbackData, prefix="suno_instrumental"):
    value: str | None = None


class SunoStyleCallback(CallbackData, prefix="suno_style"):
    value: str | None = None


class RunwayDurationCallback(CallbackData, prefix="suno_"):
    value: str | None = None


class RunwayGenerationCallback(CallbackData, prefix="runway_generation"):
    price: int
