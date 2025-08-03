const protocol = window.location.protocol === 'https:' ? 'wss' : 'ws';

function escapeHTML(unsafeText: string): string {
    let div = document.createElement('div');
    div.textContent = unsafeText;
    return div.innerHTML;
}

window.onload = () => {
    const tbody = document.querySelector('tbody')!;

    function connectWebsocket() {
        var ws = new WebSocket(`${protocol}://${window.location.host}/view/leaderboard`);
        var interval: number;

        ws.addEventListener('open', () => {
            console.log('Connected to WebSocket server');
            interval = setInterval(() => {
                ws.send('ping');
            }, 60000);
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

        ws.addEventListener('message', (event) => {
            console.log(`Message from server: ${event.data}`);
            if (event.data === 'pong') return;
            if (event.data === 'restart') window.location.reload();

            const data: string[][] = JSON.parse(event.data);

            tbody.innerHTML = '';

            data.forEach((item) => {
                const tr = document.createElement('tr');
                tr.innerHTML = `
                    <td>${escapeHTML(item[0])}</td>
                    <td>${parseInt(item[1])} TL</td>
                    <td>${parseInt(item[2])} Dk</td>
                `;
                tbody.appendChild(tr);
            });

            for (let i = 0; i < 10 - data.length; i++) {
                const tr = document.createElement('tr');
                tr.innerHTML = `
                    <td></td>
                    <td></td>
                    <td></td>
                `;
                tbody.appendChild(tr);
            }
        })
    }

    connectWebsocket();
}