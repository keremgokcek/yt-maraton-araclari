from typing import AsyncGenerator
from asyncio import Queue

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
        return connection

    async def subscribe(self, connection: Queue) -> AsyncGenerator[str, None]:
        while True:
            message = await connection.get()
            yield message

    async def close_connection(self, connection: Queue) -> None:
        self.connections.remove(connection)
