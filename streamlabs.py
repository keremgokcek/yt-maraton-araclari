from socketio import AsyncClient
from typing import TYPE_CHECKING
from donation import Donation, DonationType
from json import dump

if TYPE_CHECKING:
    from app import CustomApp

URL = "https://sockets.streamlabs.com?token={}"

USD_TO_TRY = 39.83
EUR_TO_TRY = 46.79


class Streamlabs(AsyncClient):
    def __init__(self, app: 'CustomApp', token: str) -> None:
        super().__init__(
            handle_sigint=False, reconnection_delay_max=60, request_timeout=60
        )
        self.app = app
        self.token = token
        self.on('event', self.event_handler)

    async def connect(self, *args, **kwargs) -> None:
        kwargs.pop('transports', None)
        await super().connect(
            URL.format(self.token), transports=['websocket'], **kwargs
        )

    async def _publish(self, data: Donation) -> None:
        # Donate Goal Update
        if data.kind == DonationType.DONATION:
            self.app.app_config['donate-goal']['current'] += data.amount
        else:
            self.app.app_config['donate-goal']['current'] += data.amount * 0.65

        with open('config.json', 'w') as f:
            dump(self.app.app_config, f)

        await self.app.connections.donate_goal.publish(data)

    async def event_handler(self, data) -> None:
        match data['type']:
            case 'donation':  # Bynogame and Oyunfor donations
                try:
                    amount = float(
                        data['message'][0]['formatted_amount']
                        .encode()
                        .decode('unicode_escape')
                        .replace(',', '')
                        .split()[1]
                    )
                except:
                    print('WARNING: Got basic donation with unknown currency!')
                    usd_amount = float(data['message'][0]['amount'])
                    amount = usd_amount * USD_TO_TRY

                donator = data['message'][0]['name']
                message = data['message'][0]['message']

                donation = Donation(
                    amount, DonationType.DONATION, donator, message
                )

                await self._publish(donation)

            case 'superchat':  # YouTube Superchats
                raw_amount = int(data['message'][0]['amount']) / 1000000
                if data['message'][0]['currency'] == 'TRY':
                    amount = raw_amount
                elif data['message'][0]['currency'] == 'USD':
                    amount = raw_amount * USD_TO_TRY
                elif data['message'][0]['currency'] == 'EUR':
                    amount = raw_amount * EUR_TO_TRY
                else:
                    print(
                        f"WARNING: Currency {data['message'][0]['currency']} is not supported!"
                    )
                    return

                donator = data['message'][0]['name']
                message = data['message'][0].get('comment')
                channel_id = data['message'][0]['channelId']

                donation = Donation(
                    amount,
                    DonationType.SUPERCHAT,
                    donator,
                    message,
                    channel_id,
                )

                await self._publish(donation)

            case 'subscription':  # YouTube Memberships
                """
                Membership Milestone (w/ message):  message with string value
                Membership Milestone (w/o message): no message attribute
                New membership:                     message with null value
                Upgrade membership:                 unknown
                """
                if 'message' not in data['message'][0]:
                    print(
                        'DEBUG: Skipping membership milestone event w/o message'
                    )
                    return  # Membership Milestone Message (w/o message)

                if data['message'][0]['message']:
                    print(
                        'DEBUG: Skipping membership milestone event w/ message'
                    )
                    return  # Membership Milestone Message (w/ message)

                else:  # New membership event
                    match data['message'][0]['membershipLevelName']:
                        case 'Destekçi':
                            amount = 10
                        case 'Sağlam Destekçi':
                            amount = 25
                        case 'Kral Destekçi':
                            amount = 50
                        case 'Kanalın Sahibi':
                            amount = 100
                        case 'Büyük Sponsor ':
                            amount = 650
                        case _:
                            print(
                                f"DEBUG: {data['message'][0]['membershipLevelName']} unsupported"
                            )
                            return

                    donator = data['message'][0]['name']
                    channel_id = data['message'][0]['id']

                    donation = Donation(
                        amount,
                        DonationType.MEMBERSHIP,
                        donator,
                        channel_id=channel_id,
                    )

                    await self._publish(donation)

            case 'membershipGift':  # YouTube Membership Gifts
                if 'giftMembershipsCount' not in data['message'][0]:
                    print('DEBUG: Skipping membership gift redemption message')
                    return  # Membership gift redemption announce

                amount = data['message'][0]['giftMembershipsCount'] * 10
                donator = data['message'][0]['name']
                channel_id = data['message'][0]['id']

                donation = Donation(
                    amount,
                    DonationType.MEMBERSHIP_GIFT,
                    donator,
                    channel_id=channel_id,
                )

                await self._publish(donation)

            case _:
                # Skip unnecessary events
                if data['type'] in [
                    'alertPlaying',
                    'follow',
                    'streamlabels',
                    'streamlabels.underlying',
                    'eventsPanelSettingsUpdate',
                ]:
                    return

                # Any other event
                print(f"TODO: Add support for {data['type']}")
