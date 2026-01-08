from datetime import datetime
from aiohttp import ClientSession
from os import getenv


class YouTubeUser:
    def __init__(self, display_name: str, username: str, creation_date: str):
        self.display_name = display_name
        self.username = username
        self.creation_date = datetime.fromisoformat(creation_date)


USER_CACHE: dict[str, YouTubeUser] = {}


async def get_display_name(channel_id: str) -> str | None:
    if cached_user := USER_CACHE.get(channel_id):
        return cached_user.display_name

    async with ClientSession() as session:
        async with session.get(
            f"https://www.googleapis.com/youtube/v3/channels?part=snippet&id={channel_id}&key={getenv('YOUTUBE_API_KEY')}"
        ) as resp:
            if resp.status != 200:
                return

            snippet = (await resp.json())['items'][0]['snippet']
            user = YouTubeUser(
                display_name=snippet['title'],
                username=snippet['customUrl'][1:],
                creation_date=snippet['publishedAt'],
            )

            USER_CACHE[channel_id] = user

            return user.display_name
