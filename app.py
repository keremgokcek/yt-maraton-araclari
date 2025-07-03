from quart import Quart
from streamlabs import Streamlabs
from dotenv import load_dotenv
from os import getenv
from locale import setlocale, LC_TIME
from json import load
from types import SimpleNamespace
from connection import ConnectionHandler

load_dotenv()


class CustomApp(Quart):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.streamlabs = Streamlabs(self, getenv('STREAMLABS_SOCKET_TOKEN'))
        self.app_config = load(open('config.json'))

        self.connections = SimpleNamespace()
        self.connections.donate_goal = ConnectionHandler()

        setlocale(LC_TIME, 'tr_TR.UTF-8')

    async def startup(self) -> None:
        await self.streamlabs.connect()
        return await super().startup()

    async def shutdown(self):
        print('Shutting down Quart server...')
        await self.streamlabs.shutdown()
        return await super().shutdown()
