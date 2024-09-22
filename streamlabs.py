import socketio
from orjson import dumps
from tools import process_data
from datetime import datetime, timedelta
from tools import EventType

URL = "https://sockets.streamlabs.com?token={}"


class Streamlabs(socketio.AsyncClient):
    def __init__(self, app) -> None:
        super().__init__()
        self.app = app
        self.on('event', self.event_handler)
        
    async def connect(self, token: str) -> None:
        await super().connect(URL.format(token), transports=['websocket'])
        
    async def event_handler(self, data) -> None:
        if parsed_data := await process_data(data):
            self.app.log_event({
                "timestamp": datetime.now().astimezone().isoformat(),
                "type": EventType.ADD_TIME,
                "username": 'Sistem',
                "donator": parsed_data['name'],
                "donate_type": parsed_data['type'],
                "minutes": parsed_data['time'],
            })
            self.app.set_date(datetime.fromisoformat(self.app.app_config['end-date']) + timedelta(minutes=float(parsed_data['time'])))
            self.app.variables.days_hidden = not bool((self.app.get_date() - datetime.now()).days)
            await self.app.connections.maraton.publish(dumps(parsed_data).decode('utf-8'))
            await self.app.connections.panel.publish(dumps({
                "type": "log",
                "message": f"{parsed_data['name']} tarafından {parsed_data['time']} dakika uzatıldı.",
                "username": "Sistem",
                "timestamp": datetime.now().astimezone().isoformat()
            }).decode('utf-8'))
