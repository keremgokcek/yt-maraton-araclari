from datetime import datetime
from tools import get_time_metrics
from quart import Blueprint, render_template, current_app, websocket

maraton = Blueprint('maraton_page', __name__, template_folder='templates')

@maraton.route('/maraton')
async def maraton_page():
    current_app.variables.days_hidden = not bool((current_app.get_date() - datetime.now()).days)
    return await render_template('maraton.html', timestamp=int(current_app.get_date().timestamp()*1000),
                                 days_hidden=current_app.variables.days_hidden,
                                 time_metrics=get_time_metrics(current_app.get_date()),
                                 stopped=bool(current_app.app_config['pause-date']))
    
@maraton.websocket('/socket/maraton')
async def maraton_socket():
    await websocket.send(f'countdown {int(current_app.get_date().timestamp()*1000)}')
    connection = await current_app.connections.maraton.new_connection(websocket.headers.get('User-Agent'))
    try:
        async for message in current_app.connections.maraton.subscribe(connection):
            await websocket.send(message)
    finally:
        await current_app.connections.maraton.close_connection(connection)
