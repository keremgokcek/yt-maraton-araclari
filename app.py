from quart import Quart, redirect
from quart_auth import Unauthorized
from streamlabs import Streamlabs
from os import getenv, listdir, path
from locale import setlocale, LC_TIME
from json import load, dump
from types import SimpleNamespace
from importlib import import_module
from connection import ConnectionHandler
from datetime import datetime
from aiosqlite import connect
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from aiosqlite import Connection


class CustomApp(Quart):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.streamlabs = Streamlabs(self, getenv('STREAMLABS_SOCKET_TOKEN'))
        self.app_config = load(open('config.json'))

        self.connections = SimpleNamespace()
        self.connections.donate_goal = ConnectionHandler()
        self.connections.membership_goal = ConnectionHandler()
        self.connections.countdown = ConnectionHandler()
        self.connections.leaderboard = ConnectionHandler()

        self.managers = SimpleNamespace()
        self.managers.countdown = ConnectionHandler()

        self.register_error_handler(Unauthorized, self.on_unauthorized)

        setlocale(LC_TIME, 'tr_TR.UTF-8')

    async def startup(self) -> None:
        self.db_conn = await self.setup_database_connection()
        await self.streamlabs.connect()
        return await super().startup()

    async def shutdown(self):
        print('Shutting down Quart server...')
        await self.streamlabs.shutdown()
        await self.db_conn.close()
        return await super().shutdown()

    def update_config(self) -> None:
        with open('config.json', 'w') as f:
            dump(self.app_config, f, indent=4)

    def log_event(self, data: dict) -> None:
        data['timestamp'] = datetime.now().astimezone().isoformat()

        logs = load(open('events.log'))
        logs.append(data)
        with open('events.log', 'w') as f:
            dump(logs, f, indent=2, default=str)

    def register_blueprint_folder(self, folder: str, **options) -> None:
        for file in listdir(folder):
            if file.endswith('.py'):
                module = import_module(f'{folder}.{file[:-3]}')
                blueprint = getattr(module, file[:-3])
                blueprint.register(self, options)

    async def on_unauthorized(self, _):
        return redirect("/login")

    async def setup_database_connection(
        self, database_file="maraton.db"
    ) -> "Connection":
        if path.isdir(database_file) or not path.exists(database_file):
            # Database setup here
            conn = await connect(database_file)
            await conn.execute(
                """
                CREATE TABLE IF NOT EXISTS leaderboard (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT UNIQUE,
                    username TEXT,
                    amount REAL,
                    minutes REAL
                )
                """
            )
            await conn.execute(
                """
                CREATE TABLE IF NOT EXISTS waiting_donations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT,
                    amount REAL,
                    minutes REAL,
                    source TEXT,
                    message TEXT
                )
                """
            )

            await conn.commit()
        else:
            conn = await connect(database_file)

        return conn
