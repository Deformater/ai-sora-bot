def suno_text(format: str, quality: str, duration: str):
    text = f"""Параметры генерации:

Формат: {format.replace("_", ":")}
Качество: {quality}
Длительность: {duration}с"""
    return text


def runway_format_text():
    text = f"""Выберите формат видео:"""
    return text


def runway_quality_text():
    text = f"""Выберите качество видео:"""
    return text


def runway_duration_text():
    text = f"""Выберите длительность видео:"""
    return text


def runway_prompt_text():
    text = """Введите описание для видео, пишите максимально подробно

Помните, что Runway это нейросеть, а не точный алгоритм, она может галлюцинировать или выдавать неверный результат, чтобы добиться качественного результата закладывайте несколько попыток.

Введите промпт:"""

    return text
