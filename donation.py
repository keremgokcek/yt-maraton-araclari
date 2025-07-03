from enum import Enum


class DonationType(Enum):
    DONATION = 'donation'
    MEMBERSHIP = 'membership'
    MEMBERSHIP_GIFT = 'membership_gift'
    SUPERCHAT = 'superchat'


class Donation:
    def __init__(self, amount: int, kind: DonationType) -> None:
        self.amount: int = amount
        self.kind: DonationType = kind

    def to_dict(self) -> dict:
        return {'amount': self.amount, 'kind': self.kind.value}
