const protocol = window.location.protocol === 'https:' ? 'wss' : 'ws';
const element_ids = ['add-time', 'remove-time', 'adjust-time']
var circle, log_body;

window.onload = () => {
    const elements = document.querySelectorAll('.options ul li');
    elements.forEach(element => {
        element.addEventListener('click', function() {
            elements.forEach(element => {
                element.classList.remove('selected');
            });
            element.classList.add('selected');
            
            var index = Array.prototype.indexOf.call(elements, element);
            element_ids.forEach(id => {
                document.getElementById(id).style.display = 'none';
            });
            document.getElementById(element_ids[index]).style.display = 'flex';
        });
    });
    
    circle = document.querySelector('.circle');
    circle.style.background = stopped ? 'red' : 'green';

    log_body = document.querySelector('.log-body');
}

var ws;
connectWebsocket();

function connectWebsocket() {
    ws = new WebSocket(`${protocol}://${window.location.host}/socket/panel`);

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
        setTimeout(() => {
            connectWebsocket();
        }, 3000);
    });

    ws.addEventListener('message', (event) => {
        console.log('Message from server:', event.data);
        if (event.data === 'ping') return;
        const data = JSON.parse(event.data);
        if (data.type === 'log') {
            const logCard = createLogCard(data.message, data.username, data.timestamp);
            log_body.insertBefore(logCard, log_body.firstChild);
        }
    })
}

function add_submit() {
    const minutes = document.getElementById('minutes').value;
    const name = document.getElementById('name').value ? document.getElementById('name').value : '';
    if (isNaN(minutes)) return;
    ws.send(JSON.stringify({time: minutes, name: name, type: 'add'}));
}

function set_submit() {
    if (confirm('Bu işlem mevcut süreyi sıfırlayacaktır. Devam etmek istediğinize emin misiniz?')) {
        const date = document.getElementById('date').value;
        if (!date) return;
        ws.send(JSON.stringify({date: date, type: 'set'}));
    }
}

function stopTimer() {
    if (stopped) return
    ws.send('stop');
    circle.style.background = 'red';
    stopped = true;
}

function startTimer() {
    if (!stopped) return
    ws.send('start');
    circle.style.background = 'green';
    stopped = false;
}

function formatDisplayDate(timestamp) {
    const deltaMs = new Date() - new Date(timestamp);
    const deltaSeconds = Math.floor(deltaMs / 1000);
    const deltaMinutes = Math.floor(deltaSeconds / 60);
    const deltaHours = Math.floor(deltaMinutes / 60);
    const deltaDays = Math.floor(deltaHours / 24);
    
    if (deltaDays === 0) {
        if (deltaSeconds < 60) {
            return 'Az önce';
        } else if (deltaSeconds < 3600) {
            return `${deltaMinutes} dakika önce`;
        } else {
            return `${deltaHours} saat önce`;
        }
    } else if (deltaDays === 1) {
        return 'Dün';
    } else {
        return `${deltaDays} gün önce`;
    }
}

function formatFullDate(timestamp) {
    const date = new Date(timestamp);

    const day = date.getDate(); // Day of the month without leading zero
    const month = date.toLocaleString('tr-TR', { month: 'long' }); // Full month name in Turkish
    const year = date.getFullYear(); // Full year
    const hours = date.getHours(); // Hours (24-hour format)
    const minutes = String(date.getMinutes()).padStart(2, '0'); // Minutes with leading zero

    return `${day} ${month} ${year} ${hours}.${minutes}`;
}

function createLogCard(message, username, timestamp) {
    const logCard = document.createElement('div');
    logCard.className = 'log-card';

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
