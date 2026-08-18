declare var stopped: boolean;

const protocol = window.location.protocol === 'https:' ? 'wss' : 'ws';
const element_ids = ['add-time', 'remove-time', 'adjust-time']
var circle: HTMLElement;
var log_body: HTMLElement;

var ws: WebSocket;
connectWebsocket();

interface Log {
    message: string;
    username: string;
    timestamp: string;
}

function connectWebsocket() {
    ws = new WebSocket(`${protocol}://${window.location.host}/manage/countdown`);
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
        console.log('Message from server:', event.data);
        if (event.data === 'pong') return;
        const data: Log = JSON.parse(event.data);
        const logCard = createLogCard(data.message, data.username, data.timestamp);
        log_body.insertBefore(logCard, log_body.firstChild);
    })
}

function add_submit() {
    const minutesInput = document.getElementById('minutes') as HTMLInputElement;
    const nameInput = document.getElementById('name') as HTMLInputElement;

    const minutes = minutesInput.value;
    const name = nameInput.value || '';

    if (isNaN(Number(minutes))) return;

    ws.send(JSON.stringify({ time: parseFloat(minutes), name: name, type: 'add_time' }));
}

function set_submit() {
    if (confirm('Bu işlem mevcut süreyi sıfırlayacaktır. Devam etmek istediğinize emin misiniz?')) {
        const dateInput = document.getElementById('date') as HTMLInputElement;
        ws.send(JSON.stringify({ date: dateInput.valueAsNumber, type: 'set_time' }));
    }
}

function stopTimer() {
    if (stopped) return;
    ws.send(JSON.stringify({ type: 'pause_timer' }))
    circle.style.background = 'red';
    stopped = true;
}

function startTimer() {
    if (!stopped) return
    ws.send(JSON.stringify({ type: 'resume_timer' }))
    circle.style.background = 'green';
    stopped = false;
}

function formatDisplayDate(timestamp: string) {
    const deltaMs = new Date().getTime() - new Date(timestamp).getTime();
    const deltaSeconds = Math.floor(deltaMs / 1000);
    const deltaMinutes = Math.floor(deltaSeconds / 60);
    const deltaHours = Math.floor(deltaMinutes / 60);
    const deltaDays = Math.floor(deltaHours / 24);

    if (deltaDays === 0) {
        if (deltaSeconds < 60) return 'Az önce';
        if (deltaSeconds < 3600) return `${deltaMinutes} dakika önce`;
        return `${deltaHours} saat önce`;
    }
    if (deltaDays === 1) return 'Dün';
    return `${deltaDays} gün önce`;
}

function formatFullDate(timestamp: string) {
    const date = new Date(timestamp);

    const day = date.getDate();
    const month = date.toLocaleString('tr-TR', { month: 'long' });
    const year = date.getFullYear();
    const hours = date.getHours();
    const minutes = String(date.getMinutes()).padStart(2, '0');

    return `${day} ${month} ${year} ${hours}.${minutes}`;
}

function createLogCard(message: string, username: string, timestamp: string) {
    const logCard = document.createElement('div');
    logCard.className = 'log-card';
    logCard.setAttribute('data-timestamp', timestamp.toString());

    const logCardContent = document.createElement('div');
    logCardContent.className = 'log-card-content';

    const logCardAuthor = document.createElement('div');
    logCardAuthor.className = 'log-card-author';
    logCardAuthor.textContent = username;

    const logCardDate = document.createElement('div');
    logCardDate.className = 'log-card-date';
    logCardDate.textContent = formatDisplayDate(timestamp);
    logCardDate.setAttribute('title', formatFullDate(timestamp));

    const logCardMessage = document.createElement('div');
    logCardMessage.className = 'log-card-message';
    logCardMessage.textContent = message;

    logCardContent.appendChild(logCardAuthor);
    logCardContent.appendChild(logCardDate);
    logCard.appendChild(logCardContent);
    logCard.appendChild(logCardMessage);

    return logCard;
}

window.onload = () => {
    const elements = document.querySelectorAll('.options ul li');
    elements.forEach(element => {
        element.addEventListener('click', () => {
            elements.forEach(element => {
                element.classList.remove('selected');
            });
            element.classList.add('selected');

            var index = Array.prototype.indexOf.call(elements, element);
            element_ids.forEach(id => {
                document.getElementById(id)!.style.display = 'none';
            });
            document.getElementById(element_ids[index])!.style.display = 'flex';
        });
    });

    circle = document.querySelector('.circle')!;
    circle.style.background = stopped ? 'red' : 'green';

    log_body = document.querySelector('.log-body')!;

    setInterval(() => {
        const cards = document.querySelectorAll('.log-card');
        cards.forEach(card => {
            const timestamp = card.getAttribute('data-timestamp')!;
            const displayDate = formatDisplayDate(timestamp);
            card.querySelector('.log-card-date')!.textContent = displayDate;
        });
    }, 1000);

    const add_time = document.getElementById('add-time-submit')!;
    const set_time = document.getElementById('set-time-submit')!;
    const start_timer = document.getElementById('start-timer')!;
    const stop_timer = document.getElementById('stop-timer')!;

    add_time.addEventListener('click', (e: Event) => add_submit());
    set_time.addEventListener('click', (e: Event) => set_submit());
    start_timer.addEventListener('click', (e: Event) => startTimer());
    stop_timer.addEventListener('click', (e: Event) => stopTimer());
}
