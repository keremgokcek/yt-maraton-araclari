import json
import datetime
from typing import Optional
from types import SimpleNamespace
from enum import Enum


class EventType(Enum):
    PAUSE_TIMER = 'pause_timer'
    RESUME_TIMER = 'resume_timer'
    ADD_TIME = 'add_time'
    SET_DATE = 'set_date'
    RESTART_CLIENTS = 'restart_clients'
    
    def __str__(self):
        return self.value
    
    
class DonationType(Enum):
    DONATION = 'donation'
    YOUTUBE_SUPERCHAT = 'youtube_superchat'
    YOUTUBE_SUBSCRIPTION = 'youtube_subscription'
    YOUTUBE_MEMBERSHIP_GIFT = 'youtube_membership_gift'
    
    def __str__(self):
        return self.value


async def get_user_data(username: str, password: str) -> Optional[int]:
    with open('logins.json') as f:
        logins = json.load(f)
    
    pair = logins.get(username)
    
    if pair and pair['password'] == password:
        return pair['id']
    else:
        return None
    
async def process_data(data: dict) -> Optional[dict]:
    usd_to_try = 33.61
    try:
        if len(data['message']) > 1 and isinstance(data['message'], list):
            print(data)
    except Exception as e:
        print(e)
    if data['type'] == 'donation':  # Bynogame/Oyunfor
        name = data['message'][0]['name']
        try:
            amount = float(data['message'][0]['formatted_amount'].encode().decode('unicode_escape').replace(',', '').split()[1])
        except:
            usd_amount = float(data['message'][0]['amount'])
            amount = usd_amount * usd_to_try
        return {
            'name': name,
            'time': str(amount * 0.3),
            'type': str(DonationType.DONATION)
        }
    elif data['type'] == 'superchat' and data['for'] == 'youtube_account':  # YouTube Superchat
        try:
            name = data['message'][0]['name']
            if data['message'][0]['currency'] == 'TRY':
                amount = int(data['message'][0]['amount']) / 1000000
                return {
                    'name': name,
                    'time': str(amount * 0.15),
                    'type': str(DonationType.YOUTUBE_SUPERCHAT)
                }
            else:
                print(f"Other currency {data}")
        except Exception as e:
            print(e)
    elif data['type'] == 'subscription' and data['for'] == 'youtube_account':  # YouTube katıl üyeliği
        # try:
        #     if data['message'][0]['months'] == 1:
        #         name = data['message'][0]['name']
        # except Exception as e:
        #     print(e)
        print(f"Subscription {data}")
    elif data['type'] == 'membershipGift' and data['for'] == 'youtube_account': # YouTube katil hediyesi
        try:
            if 'giftMembershipsCount' in data['message'][0]:
                name = data['message'][0]['name']
                amount = data['message'][0]['giftMembershipsCount'] * 10
                return {
                    'name': name,
                    'time': str(amount * 0.15),
                    'type': str(DonationType.YOUTUBE_MEMBERSHIP_GIFT)
                }
        except Exception as e:
            print(e)
    else:
        print(f"Else {data['type']}")

def get_time_metrics(date: datetime.datetime) -> SimpleNamespace:
    # Return time metrics between now and timestamp
    delta = date - datetime.datetime.now()
    return SimpleNamespace(
        days=str(delta.days).zfill(2),
        hours=str(delta.seconds // 3600).zfill(2),
        minutes=str(delta.seconds % 3600 // 60).zfill(2),
        seconds=str(delta.seconds % 60).zfill(2)
    )
