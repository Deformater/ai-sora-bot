from aiogram.filters.callback_data import CallbackData


class NanoBananaCallback(CallbackData, prefix="nano-banana"):
    pass


class NanoBananaGenerationCallback(CallbackData, prefix="nano-banana_generation"):
    price: int
