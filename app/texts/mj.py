def mj_text(format: str, speed: str, stylization: int, weirdness: int):
    text = (
        f"""Параметры генерации:

Формат: {format.replace("_", ":")}
Скорость генерации: {speed}
Уровень стилизации: {stylization}
Уровень странности: {weirdness}"""
        + " " * 40
    )
    return text


def mj_format_text():
    text = f"""Выберите формат:""" + " " * 40
    return text


def mj_speed_text():
    text = f"""Выберите скорость генерации:""" + " " * 40
    return text


def mj_stylization_text():
    text = f"""Выберите уровень стилизации:""" + " " * 40
    return text


def mj_weirdness_text():
    text = f"""Выберите уровень странности:""" + " " * 40
    return text


def mj_prompt_text():
    text = """Отправьте фото с дополнительным описанием, пишите максимально подробно

🖼 Обязательно прикрепите фото для референса, просто отправьте его вместе с промптом (прикрепите фото как изображение, а не как файл).

Введите промпт:"""

    return text
