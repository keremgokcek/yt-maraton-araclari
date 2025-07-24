export enum DonationType {
    DONATION = "donation",
    MEMBERSHIP = "membership",
    MEMBERSHIP_GIFT = "membership_gift",
    SUPERCHAT = "superchat",
}

export interface Donation {
    amount: number;
    kind: DonationType;
    donator: string;
    message?: string;
    channel_id?: string;
}