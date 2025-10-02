from aiogram.filters.callback_data import CallbackData


class ContinueCallback(CallbackData, prefix="continue"):
    pass


class BuyCreditsCallback(CallbackData, prefix="creds"):
    pass


class TryCallback(CallbackData, prefix="try"):
    pass


class BackCallback(CallbackData, prefix="back"):
    pass


class VideoBackCallback(CallbackData, prefix="ai_back"):
    pass


class TypeBackCallback(CallbackData, prefix="type_back"):
    pass


class VideoCallback(CallbackData, prefix="video"):
    pass


class MusicCallback(CallbackData, prefix="music"):
    pass


class PhotoCallback(CallbackData, prefix="photo"):
    pass


class GuideCallback(CallbackData, prefix="guide"):
    pass


class CreateLinkCallback(CallbackData, prefix="link"):
    pass
