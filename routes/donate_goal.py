from quart import Blueprint, current_app, render_template, websocket
from donation import Donation
from utils import reply_pings
from asyncio import gather

donate_goal = Blueprint('donate_goal', __name__, template_folder='templates')


@donate_goal.route('/view/donate-goal')
async def view():
    donate_goal_cfg = current_app.app_config['donate-goal']
    return await render_template(
        'view/donate-goal.html',
        current=donate_goal_cfg['current'],
        goal=donate_goal_cfg['goal'],
        title=donate_goal_cfg['title'],
    )


@donate_goal.websocket('/view/donate-goal')
async def view_socket():
    donate_goal_cfg = current_app.app_config['donate-goal']

    await websocket.send_json(
        {
            'type': 'set_state',
            'state': {
                'title': donate_goal_cfg['title'],
                'goal': donate_goal_cfg['goal'],
                'current': donate_goal_cfg['current'],
            },
        }
    )

    async def sender() -> None:
        async for data in current_app.connections.donate_goal.subscribe():
            if isinstance(data, Donation):
                await websocket.send_json(
                    {
                        'type': 'add_donation',
                        'donation': data.to_dict(),
                    }
                )
            else:
                await websocket.send_json(data)

    await gather(sender(), reply_pings())
