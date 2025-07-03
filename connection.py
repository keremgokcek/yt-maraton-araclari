from asyncio import Queue
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import AsyncIterator


class ConnectionHandler:
    def __init__(self):
        self.connections: set[Queue] = set()

    async def publish(self, message) -> None:
        for queue in self.connections:
            await queue.put(message)

    def subscribe(self) -> 'AsyncIterator':
        queue: Queue = Queue()
        self.connections.add(queue)

        async def generator():
            try:
                while True:
                    data = await queue.get()
                    yield data
            finally:
                self.connections.remove(queue)

        return generator()
