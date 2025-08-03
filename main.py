from app import CustomApp
from quart import jsonify
from quart_auth import QuartAuth, login_required
from user import User
from dotenv import load_dotenv
from os import getenv

load_dotenv()

app = CustomApp(__name__)
app.secret_key = getenv('QUART_SECRET_KEY')
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

auth_manager = QuartAuth(cookie_secure=False, user_class=User)
auth_manager.init_app(app)

app.register_blueprint_folder('routes')


@app.after_request
def add_header(response):
    response.cache_control.no_cache = True
    response.cache_control.no_store = True
    response.cache_control.max_age = 0
    response.cache_control.must_revalidate = True
    return response


@app.route('/restart-clients')
async def restart_clients():
    await app.connections.donate_goal.publish('restart')
    await app.connections.countdown.publish('restart')
    await app.connections.leaderboard.publish('restart')
    return jsonify(True)


@app.route('/api/clients')
@login_required
async def api_clients():
    return {
        'donate-goal': len(app.connections.donate_goal.connections),
        'countdown': len(app.connections.countdown.connections),
        'leaderboard': len(app.connections.leaderboard.connections),
        'manage_countdown': len(app.managers.countdown.connections),
    }


if __name__ == '__main__':
    app.run(debug=True, use_reloader=True)
