const protocol = window.location.protocol === 'https:' ? 'wss' : 'ws';

enum CommandType {
    SET_STATE = 'set_state',
    RESTART = 'restart',
}

interface BaseCommand {
    type: CommandType;
}

interface SetStateCommand extends BaseCommand {
    type: CommandType.SET_STATE;
    state: State;
}

interface RestartCommand extends BaseCommand {
    type: CommandType.RESTART;
}

type Command = SetStateCommand | RestartCommand;

interface Entry {
    name: string;
    amount: number;
    minutes: number;
}

type State = Array<Entry>;

interface Change {
    entry: Entry;
    old_pos: number;
    new_pos: number;
}

function escapeHTML(unsafeText: string): string {
    let div = document.createElement('div');
    div.textContent = unsafeText;
    return div.innerHTML;
}

function animateChange(change: Change, tbody: HTMLTableSectionElement) {
    let rows = tbody.querySelectorAll('tr');
    let new_row = document.createElement('tr');
    new_row.classList.add('floating');
    new_row.innerHTML = `
        <td>${escapeHTML(change.entry.name)}</td>
        <td>${change.entry.amount} TL</td>
        <td>${change.entry.minutes} Dk</td>
    `;

    new_row.style.top = 40 * (change.old_pos + 1) + 'px';
    new_row.style.zIndex = `${20 - change.new_pos}`;

    if (change.old_pos >= 11) {
        new_row.style.opacity = '0%';
    } else {
        rows[change.old_pos].style.color = 'transparent';
        new_row.style.backgroundColor = window.getComputedStyle(rows[change.old_pos]).backgroundColor;
    }

    tbody.appendChild(new_row);

    if (change.new_pos < change.old_pos) setTimeout(() => {
        new_row.style.scale = '1.1';
        new_row.style.opacity = '100%';
    }, 200);

    setTimeout(() => {
        new_row.style.top = 40 * (change.new_pos + 1) + 'px';
        if (change.new_pos < 11) new_row.style.backgroundColor = window.getComputedStyle(rows[change.new_pos]).backgroundColor;
        if (change.new_pos >= 11) new_row.style.opacity = '0%';
    }, 800);

    setTimeout(() => {
        new_row.style.scale = '';
    }, 1800);

    setTimeout(() => {
        tbody.removeChild(new_row);
    }, 2800)

}

function renderState(tbody: HTMLTableSectionElement, state: State) {
    tbody.innerHTML = '';

    state.forEach((item) => {
        const tr = document.createElement('tr');
        tr.innerHTML = `
                    <td>${escapeHTML(item.name)}</td>
                    <td>${item.amount} TL</td>
                    <td>${item.minutes} Dk</td>
                `;
        tbody.appendChild(tr);
    });

    for (let i = 0; i < 10 - state.length; i++) {
        const tr = document.createElement('tr');
        tr.innerHTML = `
                    <td></td>
                    <td></td>
                    <td></td>
                `;
        tbody.appendChild(tr);
    }
}


window.onload = () => {
    const tbody = document.querySelector('tbody')!;

    let state: State = [];
    tbody.querySelectorAll('tr').forEach((row) => {
        let cells = row.cells;

        if (!cells[0].textContent) return;

        state.push({
            name: cells[0].textContent,
            amount: parseInt(cells[1].textContent.split(' ')[0]),
            minutes: parseInt(cells[2].textContent.split(' ')[0]),
        })
    })

    function connectWebsocket() {
        var ws = new WebSocket(`${protocol}://${window.location.host}/view/leaderboard`);
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

        ws.addEventListener('message', (event) => {
            console.log(`Message from server: ${event.data}`);
            if (event.data === 'pong') return;

            const command: Command = JSON.parse(event.data);

            if (command.type == CommandType.SET_STATE) {
                let new_state = command.state;

                let changes: Array<Change> = [];
                state.forEach((entry, index) => {
                    if (!entry.name) return;
                    if (entry.name == new_state[index]?.name) return;
                    let new_position = 11; // go out
                    let changed_entry = entry;
                    new_state.forEach((new_entry, new_index) => {
                        if (new_entry.name != entry.name) return;
                        new_position = new_index;
                        changed_entry = new_entry;
                    })
                    changes.push({ entry: changed_entry, old_pos: index, new_pos: new_position });
                })
                let new_entry_position = 11;
                new_state.forEach((new_entry, new_index) => {
                    if (state.some(entry => entry.name == new_entry.name)) return;
                    changes.push({ entry: new_entry, old_pos: new_entry_position, new_pos: new_index });
                    new_entry_position++;
                })
                changes.sort((a, b) => { return a.new_pos - b.new_pos });

                state = new_state;

                if (changes.length > 0) {
                    changes.forEach((change) => {
                        animateChange(change, tbody);
                    })
                    setTimeout(() => {
                        renderState(tbody, state)
                    }, 2800)
                } else renderState(tbody, state);

            } else if (command.type == CommandType.RESTART) {
                window.location.reload();
            }
        })
    }

    connectWebsocket();
}