from quart import Blueprint, current_app, render_template, websocket
from donation import Donation, DonationType
from utils import reply_pings
from asyncio import gather

membership_goal = Blueprint(
    'membership_goal', __name__, template_folder='templates'
)


@membership_goal.route('/view/membership-goal')
async def view():
    membership_goal_cfg = current_app.app_config['membership-goal']
    return await render_template(
        'view/membership-goal.html',
        current=membership_goal_cfg['current'],
        goal=membership_goal_cfg['goal'],
        title=membership_goal_cfg['title'],
    )


@membership_goal.websocket('/view/membership-goal')
async def view_socket():
    membership_goal_cfg = current_app.app_config['membership-goal']

    await websocket.send_json(
        {
            'type': 'set_state',
            'state': {
                'title': membership_goal_cfg['title'],
                'goal': membership_goal_cfg['goal'],
                'current': membership_goal_cfg['current'],
            },
        }
    )

    async def sender() -> None:
        async for data in current_app.connections.membership_goal.subscribe():
            if isinstance(data, Donation):
                if data.kind not in (
                    DonationType.MEMBERSHIP,
                    DonationType.MEMBERSHIP_GIFT,
                ):
                    continue

                await websocket.send_json(
                    {
                        'type': 'add_donation',
                        'donation': data.to_dict(),
                    }
                )
            else:
                await websocket.send_json(data)

    await gather(sender(), reply_pings())
