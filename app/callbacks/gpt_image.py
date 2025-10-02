from aiogram.filters.callback_data import CallbackData


class GptImageCallback(CallbackData, prefix="gpt"):
    pass


class GptImageFormatCallback(CallbackData, prefix="gpt_format"):
    value: str | None = None


class GptImageNumberCallback(CallbackData, prefix="gpt_number"):
    value: int | None = None


class GptImageEnhancePromptCallback(CallbackData, prefix="gpt_enhance"):
    value: bool | None = None


class GptImageGenerationCallback(CallbackData, prefix="gpt_generation"):
    price: int
