def gpt_image_text(format: str, number: int, enhance_promt: bool):
    text = (
        f"""Параметры генерации:

Формат: {format.replace("_", ":")}
Кол-во фото в ответе: {number}
Улучшение промпта: {'да' if enhance_promt else 'нет'}"""
        + " " * 40
    )
    return text


def gpt_image_format_text():
    text = f"""Выберите формат фото:""" + " " * 40
    return text


def gpt_image_number_text():
    text = f"""Выберите кол-во вариантов:""" + " " * 40
    return text


def gpt_image_prompt_text():
    text = """Введите описание для фото, пишите максимально подробно

🖼 Если хотите использовать фото для референса, просто отправьте его вместе с промптом (прикрепите фото как изображение, а не как файл).

Введите промпт:"""

    return text
