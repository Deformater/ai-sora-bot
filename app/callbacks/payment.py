from aiogram.filters.callback_data import CallbackData


class PremiumCallback(CallbackData, prefix="premium"):
    pass


class PremiumPlanCallback(CallbackData, prefix="premium_plan"):
    value: str | None = None


class PremiumDurationCallback(CallbackData, prefix="premium_duration"):
    value: int | None = None


class PremiumContinueCallback(CallbackData, prefix="premium_continue"):
    cost: int | None = None
    plan: str | None = None
    duration: int | None = None
