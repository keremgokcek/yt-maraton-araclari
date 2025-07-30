from app import CustomApp
from quart import jsonify
from quart_auth import QuartAuth
from user import User
from dotenv import load_dotenv
from os import getenv

load_dotenv()

app = CustomApp(__name__)
app.secret_key = getenv('QUART_SECRET_KEY')


@app.route('/restart-clients')
async def restart_clients():
    await app.connections.donate_goal.publish('restart')
    return jsonify(True)


if __name__ == '__main__':
    auth_manager = QuartAuth(cookie_secure=False, user_class=User)
    auth_manager.init_app(app)

    app.register_blueprint_folder('routes')

    app.run(debug=True, use_reloader=True)
