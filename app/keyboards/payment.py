from aiogram import F, Bot, Router, types
from aiogram.utils.keyboard import InlineKeyboardBuilder

from app.callback import BuyCreditsCallback
from app.callbacks.payment import (
    PremiumCallback,
    PremiumContinueCallback,
    PremiumDurationCallback,
    PremiumPlanCallback,
)
from app.utils.enum import DURATION_NAME_MAP, PLAN_NAME_MAP


def get_premium_choose_keyboard(cost, chosen_plan, chosen_duration):
    keyboard = InlineKeyboardBuilder()

    plans = {"base": None, "pro": None, "ultra": None}

    plans[chosen_plan] = True

    for plan_name in plans:
        callback_name = PLAN_NAME_MAP[plan_name]
        if plans[plan_name]:
            callback_name = "✅" + callback_name
        keyboard.button(
            text=callback_name,
            callback_data=PremiumPlanCallback(value=plan_name).pack(),
        )

    durations = {1: None, 3: None, 12: None}
    durations[chosen_duration] = True

    for duration in durations:
        callback_name = DURATION_NAME_MAP[duration]
        if durations[duration]:
            callback_name = "✅" + callback_name
        keyboard.button(
            text=callback_name,
            callback_data=PremiumDurationCallback(value=duration).pack(),
        )

    keyboard.add(
        types.InlineKeyboardButton(
            text=f"Продолжить с подпиской за {cost} р/{DURATION_NAME_MAP[chosen_duration]}",
            callback_data=PremiumContinueCallback(
                cost=cost, plan=chosen_plan, duration=chosen_duration
            ).pack(),
        )
    )
    keyboard.adjust(3, 3, 1)
    return keyboard.as_markup()


def confirm_payment_keyboard(link: str):
    keyboard = InlineKeyboardBuilder()
    keyboard.button(
        text="Оплатить↗",
        url=link,
    )
    return keyboard.as_markup()


def choose_payment_keyboard():
    keyboard = InlineKeyboardBuilder()
    keyboard.add(
        types.InlineKeyboardButton(
            text="💎 Купить нейрокоины", callback_data=BuyCreditsCallback().pack()
        )
    )
    keyboard.add(
        types.InlineKeyboardButton(
            text="👑 Купить премиум", callback_data=PremiumCallback().pack()
        )
    )
    keyboard.adjust(1, 1)

    return keyboard.as_markup()
