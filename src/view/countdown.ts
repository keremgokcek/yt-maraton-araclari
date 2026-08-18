declare const timestamp: string;
declare const stopped: boolean;

import { Timer } from "../timer.js";
import { Donation, DonationType, DEF_TIME, YT_TIME } from "../common.js";

enum CommandType {
    ADD_TIME = 'add_time',
    SET_TIME = 'set_time',
    ADD_DONATION = 'add_donation',
    PAUSE_TIMER = 'pause_timer',
    RESUME_TIMER = 'resume_timer',
    RESTART = 'restart',
    SHOW_REMINDER = 'show_reminder',
}

interface BaseCommand {
    type: CommandType;
}

interface AddTimeCommand extends BaseCommand {
    type: CommandType.ADD_TIME;
    time: number;
    name: string;
}

interface SetTimeCommand extends BaseCommand {
    type: CommandType.SET_TIME;
    date: number;
}

interface AddDonationCommand extends BaseCommand {
    type: CommandType.ADD_DONATION;
    donation: Donation;
}

interface OtherCommand extends BaseCommand {
    type: CommandType.PAUSE_TIMER | CommandType.RESUME_TIMER | CommandType.RESTART;
}

type Command = AddTimeCommand | SetTimeCommand | AddDonationCommand | OtherCommand;

const protocol = window.location.protocol === 'https:' ? 'wss' : 'ws';

window.onload = () => {
    const timer = new Timer(parseInt(timestamp));
    timer.startCountdown();

    function connectWebsocket() {
        const ws = new WebSocket(`${protocol}://${window.location.host}/view/countdown`);
        var interval: number;

        ws.addEventListener('open', () => {
            console.log('Connected to WebSocket server');
            interval = setInterval(() => {
                ws.send('ping');
            }, 30000);
        });

        ws.addEventListener('error', (event) => {
            console.error('WebSocket error observed:', event);
            ws.close();
        });

        ws.addEventListener('close', () => {
            console.log('WebSocket connection closed');
            clearInterval(interval);
            setTimeout(() => {
                connectWebsocket();
            }, 3000);
        });

        ws.addEventListener('message', async (event) => {
            console.log('Message from server:', event.data);

            if (event.data == 'pong') {
                // Do nothing
            } else {
                const data: Command = JSON.parse(event.data);

                if (data.type == CommandType.ADD_DONATION) {
                    const multiplier = data.donation.kind === DonationType.DONATION ? DEF_TIME : YT_TIME;
                    const minutes = data.donation.amount * multiplier;
                    timer.createDonation(minutes, data.donation.donator);
                    await timer.addTime(minutes);
                } else if (data.type == CommandType.ADD_TIME) {
                    timer.createDonation(data.time, data.name);
                    await timer.addTime(data.time);
                } else if (data.type == CommandType.SET_TIME) {
                    timer.setNewTime(data.date);
                } else if (data.type == CommandType.PAUSE_TIMER) {
                    timer.stopCountdown();
                } else if (data.type == CommandType.RESUME_TIMER) {
                    timer.continueCountdown();
                } else if (data.type == CommandType.RESTART) {
                    window.location.reload();
                } else if (data.type == CommandType.SHOW_REMINDER) {
                    timer.showReminder();
                }
            }
        });
    }

    if (stopped) timer.stopCountdown();

    connectWebsocket();
}
