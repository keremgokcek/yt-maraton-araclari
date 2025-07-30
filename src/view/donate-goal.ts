import { Donation, DonationType } from "../common";

const protocol = window.location.protocol === "https:" ? "wss" : "ws";

interface State {
    title: string;
    goal: number;
    percent: number;
    current: number;
}

let state: State;

window.onload = () => {
    const percent = document.getElementById("percent")!;
    const progress = document.getElementById("progress")!;

    state = {
        title: document.getElementById("title")?.textContent!,
        goal: parseInt(document.getElementById("goal")?.textContent?.split(" ")[0]!),
        percent: parseFloat(document.getElementById("percent")?.textContent?.match(/\(([0-9.]*)%\)/)?.[1]!),
        current: parseFloat(document.getElementById("percent")?.textContent?.match(/^([0-9.]*) TL/)?.[1]!),
    };

    function connectWebsocket(): void {
        const ws = new WebSocket(`${protocol}://${window.location.host}/view/donate-goal`);
        var interval: number;

        ws.addEventListener("open", () => {
            console.log("Connected to WebSocket server");
            interval = window.setInterval(() => {
                ws.send("ping");
            }, 60000);
        });

        ws.addEventListener("error", (event: Event) => {
            console.error("WebSocket error observed:", event);
            ws.close();
            window.clearInterval(interval);
        });

        ws.addEventListener("close", () => {
            console.log("WebSocket connection closed");
            setTimeout(() => {
                connectWebsocket();
            }, 3000);
        });

        ws.addEventListener("message", async (event: MessageEvent) => {
            console.log("Message from server:", event.data);

            if (event.data === "restart") {
                window.location.reload();
            } else {
                try {
                    const data: Donation = JSON.parse(event.data);
                    console.log("Received donation:", data);

                    state.current += data.amount;
                    state.percent = (state.current / state.goal) * 100;

                    percent.textContent = `${parseFloat(state.current.toFixed(2))} TL (${parseFloat(state.percent.toFixed(2))}%)`;
                    progress.style.width = `${Math.min(state.percent, 100)}%`;

                    if (data.kind === DonationType.DONATION) {
                        console.log(`Donation of ${data.amount} TRY`);
                    } else if (data.kind === DonationType.MEMBERSHIP) {
                        console.log(`Membership with ${data.amount} TRY`);
                    } else if (data.kind === DonationType.MEMBERSHIP_GIFT) {
                        console.log(`Membership gift for ${data.amount} TRY`);
                    } else if (data.kind === DonationType.SUPERCHAT) {
                        console.log(`Superchat for ${data.amount} TRY`);
                    } else {
                        console.log(`Unsupported donation type: ${data.kind}`);
                    }
                } catch (err) {
                    console.error("Failed to parse donation:", err);
                }
            }
        });
    }

    connectWebsocket();
};
