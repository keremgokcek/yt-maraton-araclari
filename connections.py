from quart import websocket
from typing import AsyncGenerator
from asyncio import Queue, create_task

class Connection(Queue):
    def __init__(self, useragent: str):
        super().__init__()
        self.useragent = useragent


class ConnectionHandler:
    def __init__(self):
        self.connections = set()

    async def publish(self, message: str) -> None:
        for connection in self.connections:
            await connection.put(message)

    async def new_connection(self, useragent) -> Queue:
        connection = Connection(useragent)
        self.connections.add(connection)
        connection.task = create_task(self._receive(connection))
        return connection

    async def subscribe(self, connection: Queue) -> AsyncGenerator[str, None]:
        while True:
            message = await connection.get()
            yield message

    async def close_connection(self, connection: Queue) -> None:
        self.connections.remove(connection)
        connection.task.cancel()
        await connection.task

    async def _receive(self, connection) -> None:
        while True:
            message = await websocket.receive()
            await connection.put(message)
