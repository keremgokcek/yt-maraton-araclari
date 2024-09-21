const element_ids = ['add-time', 'remove-time', 'adjust-time']
var circle;

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
}

var ws;
connectWebsocket();

function connectWebsocket() {
    ws = new WebSocket(`ws://${window.location.host}/socket/panel`);

    ws.addEventListener('open', () => {
        console.log('Connected to WebSocket server');
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
