import { Donation, DonationType, DEF_MULT, YT_MULT } from "../common.js";

const protocol = window.location.protocol === "https:" ? "wss" : "ws";

enum CommandType {
    SET_STATE = "set_state",
    ADD_DONATION = "add_donation",
    RESTART = "restart",
}

interface BaseCommand {
    type: CommandType;
}

interface SetStateCommand {
    type: CommandType.SET_STATE;
    state: State;
}

interface AddDonationCommand extends BaseCommand {
    type: CommandType.ADD_DONATION;
    donation: Donation;
}

interface RestartCommand extends BaseCommand {
    type: CommandType.RESTART;
}

type Command = SetStateCommand | AddDonationCommand | RestartCommand;

interface State {
    title: string;
    goal: number;
    current: number;
}

let state: State;

window.onload = () => {
    const goal = document.getElementById("goal")!;
    const percent = document.getElementById("percent")!;
    const progress = document.getElementById("progress")!;
    const title = document.getElementById("title")!;

    state = {
        title: document.getElementById("title")?.textContent!,
        goal: parseInt(document.getElementById("goal")?.textContent?.split(" ")[0]!),
        current: parseFloat(document.getElementById("percent")?.textContent?.match(/^([0-9.]*) TL/)?.[1]!),
    };

    function connectWebsocket(): void {
        const ws = new WebSocket(`${protocol}://${window.location.host}/view/membership-goal`);
        var interval: number;

        ws.addEventListener("open", () => {
            console.log("Connected to WebSocket server");
            interval = window.setInterval(() => {
                ws.send("ping");
            }, 30000);
        });

        ws.addEventListener("error", (event: Event) => {
            console.error("WebSocket error observed:", event);
            ws.close();
        });

        ws.addEventListener("close", () => {
            console.log("WebSocket connection closed");
            window.clearInterval(interval);
            setTimeout(() => {
                connectWebsocket();
            }, 3000);
        });

        ws.addEventListener("message", async (event: MessageEvent) => {
            console.log("Message from server:", event.data);

            if (event.data === 'pong') {
                // Do nothing
            } else {
                const command: Command = JSON.parse(event.data);

                if (command.type == CommandType.ADD_DONATION) {
                    let data = command.donation;

                    console.log("Received donation:", data);

                    if (data.kind === DonationType.MEMBERSHIP) {
                        console.log(`Membership with ${data.amount} TRY`);
                        state.current += 1;
                    } else if (data.kind === DonationType.MEMBERSHIP_GIFT) {
                        console.log(`Membership gift for ${data.amount} TRY`);
                        state.current += data.amount / 25;
                    } else {
                        console.log(`Unsupported donation type: ${data.kind}`);
                        return;
                    }

                    let current_percent = (state.current / state.goal) * 100;

                    percent.textContent = `${parseInt(state.current.toFixed(0))} / ${parseInt(state.goal.toFixed(0))}`;
                    progress.style.width = `${Math.min(current_percent, 100)}%`;
                } else if (command.type == CommandType.SET_STATE) {
                    state = command.state;

                    goal.textContent = `${state.goal} KATIL`
                    title.textContent = `${state.title}`

                    let current_percent = (state.current / state.goal) * 100;
                    percent.textContent = `${parseInt(state.current.toFixed(0))} / ${parseInt(state.goal.toFixed(0))}`;
                    progress.style.width = `${Math.min(current_percent, 100)}%`;
                } else if (command.type == CommandType.RESTART) {
                    window.location.reload();
                }
            }
        });
    }

    connectWebsocket();
};
