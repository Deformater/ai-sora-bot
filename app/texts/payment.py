from app.db.models.price import Price


def premium_text(price: Price):
    text = f"Тариф {price.name}:"

    if price.limits:
        for key, value in price.limits.items():
            text += f"\n{key}: {value}"

    return text


def confirm_premium_text():
    text = f"""Нажмите «Оплатить», затем вернитесь в бот — зачисление придёт автоматически."""
    return text


def buy_generation_text():
    text = f"""💎 Нейрокоины
— Внутренняя валюта для генерации нейросетей

👑 Премиум-подписка
— Премиум доступ ко всем нейросетям
— Скидка на покупку нейроикоинов 10%
— Расширенные функции"""
    return text
