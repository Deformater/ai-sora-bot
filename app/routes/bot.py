import base64
import json
import logging

from aiogram import F, Bot, Router, types
from aiogram.filters import CommandObject, CommandStart, or_f, Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import FSInputFile, LabeledPrice
from aiogram.utils.deep_linking import create_start_link
from aiogram.utils.keyboard import InlineKeyboardBuilder
from sqlalchemy.ext.asyncio import AsyncSession
from yookassa import Configuration

from app.callback import (
    BackCallback,
    BuyCreditsCallback,
    ContinueCallback,
    PhotoCallback,
    TryCallback,
    TypeBackCallback,
    VideoCallback,
)
from app.callbacks.payment import (
    PremiumCallback,
    PremiumContinueCallback,
    PremiumDurationCallback,
    PremiumPlanCallback,
)
from app.config.utils import get_settings
from app.db.database import DatabaseManager
from app.db.models.user import User
from app.keyboard import (
    buy_credits_keyboard,
    continue_keyboard,
    get_main_menu_keyboard,
    photo_keyboard,
    type_keyboard,
    video_keyboard,
)
from app.keyboards.payment import (
    choose_payment_keyboard,
    confirm_payment_keyboard,
    get_premium_choose_keyboard,
)
from app.services.payment import PaymentService
from app.texts.base import (
    ai_type_text,
    buy_credits_text,
    help_text,
    photo_text,
    profile_text,
    ref_text,
    start_text,
    video_text,
)
from app.texts.payment import buy_generation_text, confirm_premium_text, premium_text


logger = logging.getLogger(__name__)
main_router = Router()
settings = get_settings()


db = DatabaseManager

Configuration.account_id = settings.YOOKASSA_SHOP_ID
Configuration.secret_key = settings.YOOKASSA_SECRET_KEY


@main_router.message(Command("stop_subscription"))
async def delete_card_command(
    message: types.Message, state: FSMContext, session: AsyncSession
):
    await message.bot.send_message(
        chat_id=message.chat.id,
        text="Ваша карта отвязана",
    )

    await state.clear()


@main_router.message(CommandStart(deep_link=True))
async def start_command_deep_link(
    message: types.Message,
    command: CommandObject,
    state: FSMContext,
    session: AsyncSession,
):
    user_id = message.from_user.id
    username = message.from_user.username or ""

    refer = command.args

    user = await db.get_user(session, user_id)
    if not user:
        await db.add_user(session, user_id, username)
        await session.commit()
        user = await db.get_user(session, user_id)
        if refer:
            if refer == "veo":
                await message.bot.send_message(
                    chat_id=user_id,
                    text="Ты активировал промокод veo, тебе начислены 6💎",
                )
                user.credits += 6
            else:
                refer_user = await db.get_user(session, int(refer))
                refer_user.friends_invited += 1
                if refer_user.friends_invited <= 3:
                    refer_user.credits += 2
                    session.add(refer_user)
                    await message.bot.send_message(
                        chat_id=refer,
                        text="По твоей ссылке перешёл человек, тебе начислены 2💎",
                    )
                else:
                    await message.bot.send_message(
                        chat_id=refer,
                        text="По твоей ссылке перешёл человек, но лимит бесплатных кредитов исчерпан",
                    )

        session.add(user)
        await session.commit()

    await message.bot.send_photo(
        chat_id=user_id,
        photo=FSInputFile(path="start.png"),
        caption=start_text(),
        reply_markup=continue_keyboard(),
    )
    await state.clear()


@main_router.message(CommandStart())
async def start_command(
    message: types.Message, state: FSMContext, session: AsyncSession
):
    user_id = message.from_user.id
    username = message.from_user.username or ""

    user = await db.get_user(session, user_id)
    if not user:
        await db.add_user(session, user_id, username)
        await session.commit()
        user = await db.get_user(session, user_id)

    await message.bot.send_photo(
        chat_id=message.chat.id,
        photo=FSInputFile(path="start.png"),
        caption=start_text(),
        reply_markup=continue_keyboard(),
    )

    await session.commit()
    await state.clear()


@main_router.callback_query(ContinueCallback.filter())
async def continue_handler(query: types.CallbackQuery) -> None:
    await query.message.answer(
        text=help_text(),
        reply_markup=get_main_menu_keyboard(),
        parse_mode="Markdown",
    )


@main_router.message(F.text == "🎁 Бесплатные генерации")
async def invite_friend_callback(
    message: types.Message, state: FSMContext, session: AsyncSession
):
    user_id = message.from_user.id
    user = await db.get_user(session, user_id)

    if not user:
        await message.answer("❌ Вы не зарегистрированы. Используйте /start")
        return

    ref_link = await create_start_link(message.bot, user_id)
    await message.answer(ref_text(ref_link))
    await session.commit()
    await state.clear()


@main_router.message(F.text == "💎 Получить генерации")
async def buy_subscription_callback(message: types.Message, state: FSMContext):
    keyboard = InlineKeyboardBuilder()
    keyboard.add(
        types.InlineKeyboardButton(text="💳 Карта РФ(₽)", callback_data="pay_rub")
    )
    keyboard.add(types.InlineKeyboardButton(text="⭐️ Звёзды", callback_data="pay_star"))
    await message.answer(
        buy_credits_text(),
        reply_markup=keyboard.as_markup(),
        parse_mode="MarkdownV2",
        disable_web_page_preview=True,
    )
    await state.clear()

@main_router.callback_query(or_f(BuyCreditsCallback.filter(), BackCallback.filter()))
async def buy_credits_callback(callback: types.CallbackQuery, state: FSMContext):
    keyboard = InlineKeyboardBuilder()
    keyboard.add(
        types.InlineKeyboardButton(text="💳 Карта РФ(₽)", callback_data="pay_rub")
    )
    keyboard.add(types.InlineKeyboardButton(text="⭐️ Звёзды", callback_data="pay_star"))
    await callback.message.edit_text(
        buy_credits_text(),
        reply_markup=keyboard.as_markup(),
        parse_mode="MarkdownV2",
        disable_web_page_preview=True,
    )
    await state.clear()


@main_router.message(F.text == "👤 Профиль")
async def profile_callback(
    message: types.Message, state: FSMContext, session: AsyncSession
):
    user_id = message.from_user.id
    user = await db.get_user(session, user_id)

    if not user:
        await message.answer("❌ Вы не зарегистрированы. Используйте /start")
        return

    await message.answer(
        profile_text(user.credits),
        reply_markup=buy_credits_keyboard(),
    )
    await session.commit()
    await state.clear()


@main_router.callback_query(lambda c: c.data in ["pay_rub", "pay_star"])
async def show_plans_callback(callback: types.CallbackQuery, session: AsyncSession):
    pay_method = callback.data  # "pay_rub" или "pay_star"
    keyboard = InlineKeyboardBuilder()
    if pay_method == "pay_rub":
        plan = "RUB"
    else:
        plan = "STARS"
    prices = await db.get_prices_by_type_and_currency(session, "CREDITS", plan)
    for price in prices:
        keyboard.button(
            text=f"💎 {price.credits} генераций - {str(price.price) + '₽' if pay_method == 'pay_rub' else str(price.price) + '⭐️'}",
            callback_data=f"{pay_method}_{price.plan_id}",
        )
    keyboard.adjust(1)
    keyboard.add("◀️ Назад", callback_data=BuyCreditsCallback())
    await callback.message.edit(
        "Выберите план подписки:", reply_markup=keyboard.as_markup()
    )


@main_router.callback_query(lambda c: c.data.startswith("pay_rub_"))
async def pay_rub_callback(
    callback: types.CallbackQuery, bot: Bot, session: AsyncSession
):
    plan_id = callback.data.split("_")[2]
    link = await PaymentService.create_credits_payment(
        session, callback.from_user.id, plan_id
    )

    await callback.message.edit_text(
        confirm_premium_text(),
        reply_markup=confirm_payment_keyboard(link),
    )


# @main_router.callback_query(lambda c: c.data.startswith("pay_rub_"))
# async def pay_rub_callback(
#     callback: types.CallbackQuery, bot: Bot, session: AsyncSession
# ):
#     plan_id = callback.data.split("_")[2]
#     price = await db.get_price_by_type_and_name_and_currency_and_duration(
#         session, "CREDITS", plan_id, "RUB"
#     )
#     if not price:
#         await callback.message.answer("❌ Неизвестный план подписки")
#         return

#     PRICES = [
#         LabeledPrice(
#             label=f"{price.name} ({price.credits} кредитов)",
#             amount=price.price,
#         )
#     ]
#     provider_data = {
#         "receipt": {
#             "items": [
#                 {
#                     "description": f"Тариф {price.name} ({price.credits} кредитов)",
#                     "quantity": "1.00",
#                     "amount": {
#                         "value": f"{price.price / 100:.2f}",
#                         "currency": "RUB",
#                     },
#                     "vat_code": 1,
#                 }
#             ]
#         }
#     }
#     await bot.send_invoice(
#         chat_id=callback.message.chat.id,
#         title=f"Тариф {price.name}",
#         description=f"{price.credits} кредитов для генерации видео",
#         provider_token=settings.YOOKASSA_KEY,
#         currency="RUB",
#         prices=PRICES,
#         need_phone_number=True,
#         send_phone_number_to_provider=True,
#         payload=f"subscription_rubs_{price.plan_id}",
#         provider_data=json.dumps(provider_data),
#     )


@main_router.callback_query(lambda c: c.data.startswith("pay_star_"))
async def pay_star_callback(
    callback: types.CallbackQuery, bot: Bot, session: AsyncSession
):
    plan_id = callback.data.split("_")[2]
    price = await db.get_price_by_type_and_name_and_currency_and_duration(
        session, "CREDITS", plan_id, "STARS"
    )

    if not price:
        await callback.message.answer("❌ Неизвестный план подписки")
        return

    PRICES = [
        LabeledPrice(
            label=f"{price.name} ({price.credits} генераций)",
            amount=price.price,
        )
    ]
    await bot.send_invoice(
        chat_id=callback.message.chat.id,
        title=f"Тариф {price.name}",
        description=f"{price.credits} генерации видео",
        provider_token="",
        currency="XTR",
        prices=PRICES,
        payload=f"subscription_stars_{plan_id}",
        need_shipping_address=False,
    )


@main_router.pre_checkout_query()
async def precheckout_handler(precheckout_query: types.PreCheckoutQuery, bot: Bot):
    await bot.answer_pre_checkout_query(precheckout_query.id, ok=True)


@main_router.message(lambda m: m.successful_payment is not None)
async def successful_payment_handler(message: types.Message, session: AsyncSession):
    user_id = message.from_user.id
    payment = message.successful_payment
    payload = payment.invoice_payload
    user = await db.get_user(session, user_id)
    if not user:
        user = await db.add_user(session, user_id, message.from_user.username)

    if payload == "pay_content_factory":
        await message.answer(
            f"✅ Платеж принят! Вы получили доступ к контент заводу!\n\n"
            "В ближайшее время с вами свяжется наш представитель!"
        )
        admin_users = await db.get_admin_users()
        for admin_user in admin_users:
            await message.bot.send_message(
                admin_user.user_id,
                f"Пользователь @{user.username}, {user.user_id} купил доступ к контент-заводу",
            )

    if not payload.startswith("subscription_"):
        await message.answer("❌ Неизвестный тип платежа")
        return

    payment_method, plan_id = payload.split("_")[1:]
    if payment_method == "rubs":
        price = await db.get_price_by_type_and_name(session, "RUB", plan_id)
    else:
        price = await db.get_price_by_type_and_name(session, "STARS", plan_id)

    if not price:
        await message.answer("❌ Неизвестный план подписки")
        return

    user.credits += price.credits
    await session.commit()

    await message.answer(
        f"✅ Платеж принят! Вам начислено {price.credits} кредитов.\n\n"
        f"💰 Текущий баланс: {user.credits} кредитов\n\n"
        'Теперь вы можете создавать видео с помощью кнопки "🎬 Создать видео"'
    )


@main_router.callback_query(lambda c: c.data == "buy_content_factory")
async def buy_guide_callback(
    callback: types.CallbackQuery, bot: Bot, session: AsyncSession
):
    price = await db.get_price_by_type_and_name(session, "CONTENT_FACTORY", "basic")

    PRICES = [
        LabeledPrice(
            label=price.name,
            amount=price.price,
        )
    ]
    provider_data = {
        "receipt": {
            "items": [
                {
                    "description": price.name,
                    "quantity": "1.00",
                    "amount": {
                        "value": f"{price.price / 100:.2f}",
                        "currency": "RUB",
                    },
                    "vat_code": 1,
                }
            ]
        }
    }
    await bot.send_invoice(
        chat_id=callback.message.chat.id,
        title=price.name,
        description=price.name,
        provider_token=settings.YOOKASSA_KEY,
        currency="RUB",
        prices=PRICES,
        need_phone_number=True,
        send_phone_number_to_provider=True,
        payload="pay_content_factory",
        provider_data=json.dumps(provider_data),
    )
