from quart import Blueprint, current_app
from quart_auth import login_required


clients = Blueprint('clients_page', __name__)

@clients.route('/api/clients')
@login_required
async def clients_page():
    return {
        'maraton': [connection.useragent for connection in current_app.connections.maraton.connections],
        'panel': [connection.useragent for connection in current_app.connections.panel.connections]
    }
