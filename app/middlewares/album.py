import asyncio
from aiogram.utils.media_group import MediaGroupBuilder
from aiogram import BaseMiddleware


class AlbumMiddleware(BaseMiddleware):
    album_data = {}

    def __init__(self, latency: float = 0.1):
        self.latency = latency
        super().__init__()

    async def __call__(self, handler, event, data):
        if not event.media_group_id:
            return await handler(event, data)

        try:
            self.album_data[event.media_group_id].append(event)
        except KeyError:
            self.album_data[event.media_group_id] = [event]
            await asyncio.sleep(self.latency)

            album_messages = self.album_data.pop(event.media_group_id)
            data["album"] = album_messages
            return await handler(event, data)
