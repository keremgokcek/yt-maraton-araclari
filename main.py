from app import CustomApp
from quart import render_template, websocket, jsonify
from donation import DonationType, Donation

app = CustomApp(__name__)


@app.route('/view/donate-goal')
async def view_donate_goal():
    donate_goal_cfg = app.app_config['donate-goal']
    return await render_template(
        'view/donate-goal.html',
        current=donate_goal_cfg['current'],
        goal=donate_goal_cfg['goal'],
        title=donate_goal_cfg['title'],
    )


@app.route('/manage/donate-goal')
async def manage_donate_goal():
    return 'manage_donate_goal'


@app.websocket('/ws/view/donate-goal')
async def view_donate_goal_ws():
    await websocket.accept()
    async for data in app.connections.donate_goal.subscribe():
        if isinstance(data, Donation):
            if data.kind != DonationType.DONATION:
                data.amount *= 0.65

            await websocket.send_json(data.to_dict())

        else:
            await websocket.send(data)


@app.route('/restart-clients')
async def restart_clients():
    await app.connections.donate_goal.publish('restart')
    return jsonify(True)


if __name__ == '__main__':
    app.run(debug=True, use_reloader=True)
