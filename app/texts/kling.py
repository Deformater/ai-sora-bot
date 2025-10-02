def kling_text(format: str, duration: str, model: str, version: str):
    text = f"""Параметры генерации:

Формат: {format}
Длительность: {duration}с
Модел: {model}
Версия: {version}"""
    return text


def kling_format_text():
    text = f"""Выберите формат видео:"""
    return text


def kling_version_text():
    text = f"""Выберите версия Kling:"""
    return text


def kling_model_text():
    text = f"""Выберите модель:"""
    return text


def kling_duration_text():
    text = f"""Выберите длительность видео:"""
    return text


def kling_prompt_text():
    text = """Введите описание для видео, пишите максимально подробно

Помните, что Kling это нейросеть, а не точный алгоритм, она может галлюцинировать или выдавать неверный результат, чтобы добиться качественного результата закладывайте несколько попыток.

🖼 Если хотите использовать фото для референса, просто отправьте его вместе с промптом (прикрепите фото как изображение, а не как файл).

Введите промпт:"""

    return text
