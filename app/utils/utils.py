from aiogram.types import (
    InputMediaPhoto,
    InputMediaDocument,
    URLInputFile,
    InputMediaVideo,
)
from aiogram import Bot


async def send_images(
    chat_id: int, image_urls: list[str], caption: str = None, bot: Bot = None
):
    media = []
    for i, url in enumerate(image_urls):
        if i == 0:
            media.append(InputMediaPhoto(media=url, caption=caption))
        else:
            media.append(InputMediaPhoto(media=url))

    await bot.send_media_group(chat_id=chat_id, media=media)


async def send_videos(
    chat_id: int, videos_urls: list[str], caption: str = None, bot: Bot = None
):
    media = []
    for i, url in enumerate(videos_urls):
        if i == 0:
            media.append(InputMediaVideo(media=url, caption=caption))
        else:
            media.append(InputMediaVideo(media=url))

    await bot.send_media_group(chat_id=chat_id, media=media)


async def send_media(
    chat_id: int, image_urls: list[str], caption: str = None, bot: Bot = None
):
    media = []
    for i, url in enumerate(image_urls):
        file = URLInputFile(url)
        if i == 0:
            media.append(InputMediaDocument(media=file, caption=caption))
        else:
            media.append(InputMediaDocument(media=file))

    await bot.send_media_group(chat_id=chat_id, media=media)
