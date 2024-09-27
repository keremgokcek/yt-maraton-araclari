from quart import Quart, redirect
from quart_auth import Unauthorized
from types import SimpleNamespace
from connections import ConnectionHandler
from datetime import datetime
from streamlabs import Streamlabs
from dotenv import load_dotenv
from os import getenv, listdir
from importlib import import_module
from locale import setlocale, LC_TIME
from orjson import dumps, loads, OPT_INDENT_2

load_dotenv()


class CustomApp(Quart):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.variables = SimpleNamespace()
        self.connections = SimpleNamespace()
        
        self.connections.maraton = ConnectionHandler()
        self.connections.panel = ConnectionHandler()
        
        # self.app_config = load(open('config.json'))
        with open('config.json') as f:
            self.app_config = loads(f.read())
        
        self.variables.days_hidden = not bool((self.get_date() - datetime.now()).days)
        
        self.streamlabs = Streamlabs(self)
        
        self.register_error_handler(Unauthorized, self.unauthorized)
        
        setlocale(LC_TIME, 'tr_TR.UTF-8')

    def get_date(self) -> datetime:
        end_date = self.app_config['end-date']
        pause_date = self.app_config['pause-date']
        if pause_date:
            return datetime.fromisoformat(end_date) + (datetime.now() - datetime.fromisoformat(pause_date))
        else:
            return datetime.fromisoformat(end_date)
            
    def set_date(self, date: datetime) -> None:
        self.app_config['end-date'] = date.isoformat()
        with open('config.json', 'wb') as f:
            f.write(dumps(self.app_config))
            
    def log_event(self, data: dict) -> None:
        log = loads(open('events.log', 'rb').read())
        log.append(data)
        with open('events.log', 'wb') as f:
            f.write(dumps(log, option=OPT_INDENT_2))

    async def startup(self) -> None:
        await self.streamlabs.connect(getenv('STREAMLABS_SOCKET_TOKEN'))
        return await super().startup()
    
    async def shutdown(self) -> None:
        print('Shutting down')
        return await super().shutdown()
    
    async def unauthorized(self, *_):
        return redirect("/login")
    
    def register_blueprint_folder(self, folder: str, **options) -> None:
        for file in listdir(folder):
            if file.endswith('.py'):
                module = import_module(f'{folder}.{file[:-3]}')
                blueprint = getattr(module, file[:-3])
                blueprint.register(self, options)
        
