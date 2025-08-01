from enum import Enum


class DonationType(Enum):
    DONATION = 'donation'
    MEMBERSHIP = 'membership'
    MEMBERSHIP_GIFT = 'membership_gift'
    SUPERCHAT = 'superchat'

    def __str__(self):
        return self.value


class Donation:
    def __init__(
        self,
        amount: int,
        kind: DonationType,
        donator: str,
        message: str = '',
        channel_id: str = '',
    ) -> None:
        self.amount = amount
        self.kind = kind
        self.donator = donator
        self.message = message
        self.channel_id = channel_id

    def to_dict(self) -> dict:
        return {
            'amount': self.amount,
            'kind': self.kind.value,
            'donator': self.donator,
            'message': self.message,
            'channel_id': self.channel_id,
        }
