from socketio import AsyncClient
from typing import TYPE_CHECKING
from donation import Donation, DonationType
from datetime import datetime, timedelta

if TYPE_CHECKING:
    from app import CustomApp

URL = "https://sockets.streamlabs.com?token={}"

DEF_MULT = 1.0
YT_MULT = 0.65

DEF_TIME = 0.3
YT_TIME = 0.15

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
        mult = DEF_MULT if data.kind == DonationType.DONATION else YT_MULT
        self.app.app_config['donate-goal']['current'] += data.amount * mult

        # Countdown Update
        countdown_cfg = self.app.app_config['countdown']
        end_date = datetime.fromisoformat(countdown_cfg['end-date'])
        mult = DEF_TIME if data.kind == DonationType.DONATION else YT_TIME
        added_time = timedelta(minutes=data.amount * mult)
        countdown_cfg['end-date'] = (end_date + added_time).isoformat()

        # Leaderboard Update
        if data.kind == DonationType.DONATION:
            cursor = await self.app.db_conn.execute(
                'SELECT amount, minutes FROM leaderboard WHERE username = ?',
                (data.donator,),
            )
            user = await cursor.fetchone()

            if user:
                await self.app.db_conn.execute(
                    'UPDATE leaderboard SET amount = ?, minutes = ? WHERE username = ?',
                    (
                        user[0] + data.amount,
                        user[1] + data.amount * DEF_TIME,
                        data.donator,
                    ),
                )
            else:
                await self.app.db_conn.execute(
                    'INSERT INTO waiting_donations (username, amount, minutes, source, message) VALUES (?, ?, ?, ?, ?)',
                    (
                        data.donator,
                        data.amount,
                        data.amount * DEF_TIME,
                        data.kind.value,
                        data.message,
                    ),
                )
        else:
            cursor = await self.app.db_conn.execute(
                'SELECT amount, minutes FROM leaderboard WHERE user_id = ? OR username = ?',
                (data.channel_id, data.donator),
            )
            user = await cursor.fetchone()

            if user:
                await self.app.db_conn.execute(
                    'UPDATE leaderboard SET amount = ?, minutes = ? WHERE user_id = ?',
                    (
                        user[0] + data.amount,
                        user[1] + data.amount * YT_TIME,
                        data.channel_id,
                    ),
                )
            else:
                await self.app.db_conn.execute(
                    'INSERT INTO leaderboard (user_id, username, amount, minutes) VALUES (?, ?, ?, ?)',
                    (
                        data.channel_id,
                        data.donator,
                        data.amount,
                        data.amount * YT_TIME,
                    ),
                )

        # Save config
        self.app.update_config()
        await self.app.db_conn.commit()

        await self.app.connections.donate_goal.publish(data)
        await self.app.connections.countdown.publish(data)
        await self.app.connections.leaderboard.publish(data)
        await self.app.managers.countdown.publish(data)

    async def event_handler(self, data) -> None:
        # Skip unnecessary events
        if data['type'] in [
            'alertPlaying',
            'follow',
            'streamlabels',
            'streamlabels.underlying',
            'eventsPanelSettingsUpdate',
        ]:
            return

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
                # Any other event
                print(f"TODO: Add support for {data['type']}")
                return

        # Log
        self.app.log_event(
            {
                'type': 'add_time',
                'username': 'Sistem',
                'donator': donation.donator,
                'donate_type': donation.kind,
                'minutes': donation.amount
                * (
                    DEF_TIME
                    if donation.kind == DonationType.DONATION
                    else YT_TIME
                ),
            }
        )
