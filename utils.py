from quart import websocket
from typing import assert_never


async def reply_pings() -> None:
    while True:
        msg = await websocket.receive()

        if msg == 'ping':
            await websocket.send('pong')
        else:
            assert_never(msg)
