export const DEF_MULT = 1.0
export const YT_MULT = 0.65

export const DEF_TIME = 0.3;
export const YT_TIME = 0.15;

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