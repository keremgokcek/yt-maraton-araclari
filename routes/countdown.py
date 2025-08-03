from datetime import datetime, timezone, timedelta
from quart import Blueprint, render_template, current_app, websocket
from quart_auth import login_required, current_user
from types import SimpleNamespace
from json import loads, load
from donation import Donation, DonationType
from utils import reply_pings
from enum import Enum
from asyncio import gather

countdown = Blueprint('countdown', __name__, template_folder='templates')

DEF_TIME = 0.3
YT_TIME = 0.15


class EventType(Enum):
    PAUSE_TIMER = 'pause_timer'
    RESUME_TIMER = 'resume_timer'
    ADD_TIME = 'add_time'
    SET_DATE = 'set_date'
    RESTART_CLIENTS = 'restart_clients'

    def __str__(self):
        return self.value


def get_display_time(iso_time: str) -> str:
    time = datetime.fromisoformat(iso_time)
    delta = datetime.now(timezone.utc) - time
    if delta.days == 0:
        if delta.seconds < 60:
            return 'Az önce'
        elif delta.seconds < 3600:
            return f"{delta.seconds // 60} dakika önce"
        else:
            return f"{delta.seconds // 3600} saat önce"
    elif delta.days == 1:
        return 'Dün'
    else:
        return f"{delta.days} gün önce"


def get_time_metrics(date: datetime) -> SimpleNamespace:
    # Return time metrics between now and timestamp
    delta = date - datetime.now()
    return SimpleNamespace(
        days=str(delta.days).zfill(2),
        hours=str(delta.seconds // 3600).zfill(2),
        minutes=str(delta.seconds % 3600 // 60).zfill(2),
        seconds=str(delta.seconds % 60).zfill(2),
    )


def get_date() -> datetime:
    countdown_cfg = current_app.app_config['countdown']

    end_date = countdown_cfg['end-date']
    pause_date = countdown_cfg['pause-date']

    if pause_date:
        return datetime.fromisoformat(end_date) + (
            datetime.now() - datetime.fromisoformat(pause_date)
        )
    else:
        return datetime.fromisoformat(end_date)


@countdown.route('/view/countdown')
async def view():
    countdown_cfg = current_app.app_config['countdown']
    end_date = get_date()

    return await render_template(
        'view/countdown.html',
        timestamp=int(end_date.timestamp() * 1000),
        days_hidden=not bool((end_date - datetime.now()).days),
        time_metrics=get_time_metrics(end_date),
        stopped=bool(countdown_cfg['pause-date']),
    )


@countdown.websocket('/view/countdown')
async def view_socket():
    await websocket.send(f'countdown {int(get_date().timestamp()*1000)}')

    async def sender() -> None:
        async for data in current_app.connections.countdown.subscribe():
            if isinstance(data, Donation):
                await websocket.send_json(
                    {
                        'type': 'add_donation',
                        'donation': data.to_dict(),
                    }
                )
            else:
                await websocket.send(data)

    await gather(sender(), reply_pings())


@countdown.route('/manage/countdown')
@login_required
async def manage():
    raw_logs = load(open('events.log'))[-25:]

    message_map = {
        EventType.PAUSE_TIMER: "Sayaç durduruldu.",
        EventType.RESUME_TIMER: "Sayaç devam ettirildi.",
        EventType.RESTART_CLIENTS: "Sayaca bağlı olan sayfalar yeniden başlatıldı.",
    }

    logs = []
    for entry in raw_logs:
        event_type = EventType[entry['type'].upper()]
        timestamp = entry['timestamp']

        log = {
            "author": entry['username'],
            "full_date": datetime.fromisoformat(timestamp).strftime(
                '%-d %B %Y %H.%M'
            ),
            "date": get_display_time(entry['timestamp']),
            "timestamp": timestamp,
        }

        if event_type in message_map:
            log['message'] = message_map[event_type]
        elif event_type == EventType.ADD_TIME:
            minutes = entry['minutes']
            donator = entry['donator']
            log['message'] = (
                f'{donator} tarafından {minutes} dakika uzatıldı.'
                if donator
                else f'{minutes} dakika eklendi.'
            )
        elif event_type == EventType.SET_DATE:
            date = datetime.fromisoformat(entry['date']).strftime(
                '%-d %B %Y %H.%M'
            )
            log["message"] = f'Sayaç {date} tarihine ayarlandı.'

        logs.append(log)

    return await render_template(
        'manage/countdown.html',
        username=current_user.username,
        stopped=bool(current_app.app_config['countdown']['pause-date']),
        logs=reversed(logs),
    )


@countdown.websocket('/manage/countdown')
@login_required
async def manage_socket():
    async def send():
        async for data in current_app.managers.countdown.subscribe():
            if isinstance(data, Donation):
                m = DEF_TIME if data.kind == DonationType.DONATION else YT_TIME
                log = {
                    'username': 'Sistem',
                    'timestamp': datetime.now().astimezone().isoformat(),
                    'message': f'{data.donator} tarafından {data.amount * m} dakika uzatıldı.',
                }
                await websocket.send_json(log)
            elif isinstance(data, dict):
                await websocket.send_json(data)
            else:
                await websocket.send(data)

    async def receive():
        while True:
            message = await websocket.receive()
            if message == "ping":
                await websocket.send('pong')
                continue

            now = datetime.now()
            config = current_app.app_config['countdown']

            log = {
                "type": "log",
                "username": current_user.username,
                "timestamp": now.astimezone().isoformat(),
            }

            json_data = loads(message)
            if json_data['type'] == "pause_timer":
                if config['pause-date']:
                    continue
                config['pause-date'] = now.isoformat()
                current_app.update_config()

                log['message'] = 'Sayaç durduruldu.'

                await current_app.connections.countdown.publish(message)
                await current_app.managers.countdown.publish(log)

                current_app.log_event(
                    {
                        "type": EventType.PAUSE_TIMER,
                        "username": current_user.username,
                    }
                )

            elif json_data['type'] == "resume_timer":
                if not config['pause-date']:
                    continue
                config['end-date'] = (
                    datetime.fromisoformat(config['end-date'])
                    + (now - datetime.fromisoformat(config['pause-date']))
                ).isoformat()
                config['pause-date'] = None
                current_app.update_config()

                log['message'] = 'Sayaç devam ettirildi.'

                await current_app.connections.countdown.publish(message)
                await current_app.managers.countdown.publish(log)

                current_app.log_event(
                    {
                        "type": EventType.RESUME_TIMER,
                        "username": current_user.username,
                    }
                )

            elif json_data['type'] == 'add_time':
                config['end-date'] = (
                    datetime.fromisoformat(config['end-date'])
                    + timedelta(minutes=float(json_data['time']))
                ).isoformat()
                current_app.update_config()

                log['message'] = (
                    f"{json_data['name']} tarafından {json_data['time']} dakika uzatıldı."
                    if json_data['name']
                    else f"{json_data['time']} dakika eklendi."
                )

                await current_app.connections.countdown.publish(message)
                await current_app.managers.countdown.publish(log)

                current_app.log_event(
                    {
                        "type": EventType.ADD_TIME,
                        "username": current_user.username,
                        "donator": json_data['name'],
                        "donate_type": None,
                        "minutes": json_data['time'],
                    }
                )
            elif json_data['type'] == 'set_time':
                print(json_data)
                new_date = datetime.fromtimestamp(json_data['date'] / 1000)
                config['end-date'] = new_date.isoformat()
                config['pause-date'] = None
                current_app.update_config()

                log['message'] = (
                    f"Sayaç {new_date.strftime('%-d %B %Y %H.%M')} tarihine ayarlandı."
                )

                await current_app.connections.countdown.publish(message)
                await current_app.managers.countdown.publish(log)

                current_app.log_event(
                    {
                        "type": EventType.SET_DATE,
                        "username": current_user.username,
                        "date": config['end-date'],
                    }
                )

    await gather(send(), receive())
