def flux_text(format: str, model: str):
    text = (
        f"""Параметры генерации:

Формат: {format.replace("_", ":")}
Модель генерации: {model}"""
        + " " * 40
    )
    return text


def flux_format_text():
    text = f"""Выберите формат фото:""" + " " * 40
    return text


def flux_model_text():
    text = f"""Выберите модель для генерации:""" + " " * 40
    return text


def flux_prompt_text():
    text = """Введите описание для фото, пишите максимально подробно

🖼 Если хотите использовать фото для референса, просто отправьте его вместе с промптом (прикрепите фото как изображение, а не как файл).

Введите промпт:"""

    return text
