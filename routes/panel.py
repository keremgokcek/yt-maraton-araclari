from datetime import datetime, timedelta
from quart_auth import login_required, current_user
from quart import Blueprint, render_template, current_app, redirect, websocket
from tools import EventType, get_display_time
from asyncio import create_task
from orjson import dumps, loads

panel = Blueprint('panel_page', __name__, template_folder='templates')

async def send_message(connection):
    async for message in current_app.connections.panel.subscribe(connection):
        await websocket.send(message)

@panel.route('/restart-clients')
@login_required
async def restart_clients():
    await current_app.connections.maraton.publish("restart")
    await current_app.connections.panel.publish(dumps({
        "type": "log",
        "message": "Sayaca bağlı olan sayfalar yeniden başlatıldı.",
        "username": await current_user.username,
        "timestamp": datetime.now().astimezone().isoformat()
    }).decode('utf-8'))
    current_app.log_event({
        "timestamp": datetime.now().astimezone().isoformat(),
        "type": EventType.RESTART_CLIENTS,
        "username": await current_user.username
    })
    return redirect('/panel')

@panel.route('/panel')
@login_required
async def panel_page():
    raw_logs = loads(open('events.log', 'rb').read())[-25:]
    logs = []

    for raw_log in raw_logs:
        temp_log = {
            "author": raw_log['username'],
            "full_date": datetime.fromisoformat(raw_log['timestamp']).strftime('%-d %B %Y %H.%M'),
            "date": get_display_time(raw_log['timestamp']),
            "timestamp": raw_log['timestamp']
        }
        match EventType[raw_log['type'].upper()]:
            case EventType.PAUSE_TIMER:
                temp_log["message"] = "Sayaç durduruldu."
            case EventType.RESUME_TIMER:
                temp_log["message"] = "Sayaç devam ettirildi."
            case EventType.ADD_TIME:
                if raw_log['donator']:
                    temp_log["message"] = f"{raw_log['donator']} tarafından {raw_log['minutes']} dakika uzatıldı."
                else:
                    temp_log["message"] = f"{raw_log['minutes']} dakika eklendi."
            case EventType.SET_DATE:
                temp_log["message"] = f"Sayaç {datetime.fromisoformat(raw_log['date']).strftime('%-d %B %Y %H.%M')} tarihine ayarlandı."
            case EventType.RESTART_CLIENTS:
                temp_log["message"] = "Sayaca bağlı olan sayfalar yeniden başlatıldı."
        logs.append(temp_log)

    logs.reverse()

    return await render_template('panel.html', username=await current_user.username, stopped=bool(current_app.app_config['pause-date']), logs=logs)

@panel.websocket('/socket/panel')
@login_required
async def panel_socket():
    connection = await current_app.connections.panel.new_connection(websocket.headers.get('User-Agent'))
    task = create_task(send_message(connection))
    try:
        while True:
            message = await websocket.receive()
            if message == "ping":
                await websocket.send("ping")
            elif message == "stop":
                if current_app.app_config['pause-date']:
                    return
                config = current_app.app_config
                with open('config.json', 'wb') as f:
                    config['pause-date'] = datetime.now().isoformat()
                    f.write(dumps(config))
                
                await current_app.connections.maraton.publish("stop")
                await current_app.connections.panel.publish(dumps({
                    "type": "log",
                    "message": "Sayaç durduruldu.",
                    "username": await current_user.username,
                    "timestamp": datetime.now().astimezone().isoformat()
                }).decode('utf-8'))
                
                current_app.log_event({
                    "timestamp": datetime.now().astimezone().isoformat(),
                    "type": EventType.PAUSE_TIMER,
                    "username": await current_user.username
                })
                    
            elif message == "start":
                if not current_app.app_config['pause-date']:
                    return
                config = current_app.app_config
                with open('config.json', 'wb') as f:
                    config['end-date'] = (datetime.fromisoformat(config['end-date']) + (datetime.now() - datetime.fromisoformat(config['pause-date']))).isoformat()
                    config['pause-date'] = None
                    f.write(dumps(config))
                    
                await current_app.connections.maraton.publish("start")
                await current_app.connections.panel.publish(dumps({
                    "type": "log",
                    "message": "Sayaç devam ettirildi.",
                    "username": await current_user.username,
                    "timestamp": datetime.now().astimezone().isoformat()
                }).decode('utf-8'))
                
                current_app.log_event({
                    "timestamp": datetime.now().astimezone().isoformat(),
                    "type": EventType.RESUME_TIMER,
                    "username": await current_user.username
                })
                
            else:
                json_data = loads(message)
                config = current_app.app_config
                
                if json_data['type'] == 'add':
                    current_app.set_date(datetime.fromisoformat(config['end-date']) + timedelta(minutes=float(json_data['time'])))
                    current_app.variables.days_hidden = not bool((datetime.fromisoformat(config['end-date']) - datetime.now()).days)
                    
                    await current_app.connections.maraton.publish(message)
                    await current_app.connections.panel.publish(dumps({
                        "type": "log",
                        "message": f"{json_data['name']} tarafından {json_data['time']} dakika uzatıldı." if json_data['name'] else f"{json_data['time']} dakika eklendi.",
                        "username": await current_user.username,
                        "timestamp": datetime.now().astimezone().isoformat()
                    }).decode('utf-8'))
                    
                    current_app.log_event({
                        "timestamp": datetime.now().astimezone().isoformat(),
                        "type": EventType.ADD_TIME,
                        "username": await current_user.username,
                        "donator": json_data['name'],
                        "donate_type": None,
                        "minutes": json_data['time'],
                    })
                elif json_data['type'] == 'set':
                    current_app.set_date(datetime.fromisoformat(json_data['date']))
                    current_app.app_config['pause-date'] = None
                    
                    with open('config.json', 'wb') as f:
                        f.write(dumps(current_app.app_config))
                    
                    current_app.variables.days_hidden = not bool((datetime.fromisoformat(config['end-date']) - datetime.now()).days)

                    await current_app.connections.maraton.publish(f'countdown {int(current_app.get_date().timestamp()*1000)}')
                    await current_app.connections.panel.publish(dumps({
                        "type": "log",
                        "message": f"Sayaç {datetime.fromisoformat(json_data['date']).strftime('%-d %B %Y %H.%M')} tarihine ayarlandı.",
                        "username": await current_user.username,
                        "timestamp": datetime.now().astimezone().isoformat()
                    }).decode('utf-8'))

                    current_app.log_event({
                        "timestamp": datetime.now().astimezone().isoformat(),
                        "type": EventType.SET_DATE,
                        "username": await current_user.username,
                        "date": json_data['date']
                    })
    finally:
        await current_app.connections.panel.close_connection(connection)
        task.cancel()
        await task
