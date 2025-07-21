from app import CustomApp
from quart import jsonify

app = CustomApp(__name__)


@app.route('/restart-clients')
async def restart_clients():
    await app.connections.donate_goal.publish('restart')
    return jsonify(True)


if __name__ == '__main__':
    app.register_blueprint_folder('routes')

    app.run(debug=True, use_reloader=True)
