from yookassa import Payment


async def create_payment(
    price, description, metadata, subscription=False
) -> tuple[str, str]:
    resp = Payment.create(
        {
            "amount": {"value": price, "currency": "RUB"},
            "confirmation": {
                "type": "redirect",
                "return_url": f"https://t.me/multix_aibot",
            },
            "capture": True,
            "description": description,
            "save_payment_method": subscription,
            "metadata": metadata,
        }
    )

    return resp.id, resp.confirmation.confirmation_url
