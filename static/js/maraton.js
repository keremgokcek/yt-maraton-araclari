import Timer from './timer.js';

function hideDays() {
    document.getElementById("day-box").style.opacity = 0;
    var visibleBoxes = document.querySelectorAll('.box');
    visibleBoxes.forEach((box, index) => {
        box.style.animation = `disappear 1s ease-in-out forwards`;
    });
    setTimeout(() => {
        visibleBoxes.forEach((box, index) => {
            box.style.animation = `none`;
        });
        document.getElementById("day-box").style.display = "none";
    }, 1000)
}

function showDays() {
    document.getElementById("day-box").style.display = "inline";
    setTimeout(() => {document.getElementById("day-box").style.opacity = 1;}, 10);
    var visibleBoxes = document.querySelectorAll('.box');
    visibleBoxes.forEach((box, index) => {
        box.style.transform = `translateX(-71px)`;
        box.style.animation = `reappear 1s ease-in-out forwards`;
    });
    setTimeout(() => {
        visibleBoxes.forEach((box, index) => {
            box.style.transform = `translateX(0px)`;
            box.style.animation = `none`;
        });
    }, 1000)
}

function checkForDays(countdown) {
    if (countdown.days == 0 && !days_hidden) {
        days_hidden = true;
        hideDays();
    } else if (countdown.days > 0 && days_hidden) {
        days_hidden = false;
        showDays();
    }
}

window.onload = () => {
    const timer = new Timer(parseInt(timestamp));
    timer.startCountdown();

    function connectWebsocket() {
        const ws = new WebSocket(`ws://${window.location.host}/socket/maraton`);
        var interval;
        
        ws.addEventListener('open', () => {
            console.log('Connected to WebSocket server');
            interval = setInterval(() => {
                ws.send('ping');
            }, 60000);
        });
        
        ws.addEventListener('error', (event) => {
            console.error('WebSocket error observed:', event);
            ws.close();
            clearInterval(interval);
        });
        
        ws.addEventListener('close', () => {
            console.log('WebSocket connection closed');
            setTimeout(() => {
                connectWebsocket();
            }, 3000);
        });
        
        ws.addEventListener('message', async (event) => {
            console.log('Message from server:', event.data);
        
            if (event.data.startsWith('countdown')) {
                timer.setNewTime(parseInt(event.data.split(' ')[1]));
            } else if (event.data == 'stop') {
                timer.stopCountdown();
            } else if (event.data == 'start') {
                timer.continueCountdown();
            } else if (event.data == 'restart') {
                window.location.reload()
            } else if (event.data == 'ping') {
                // Do nothing
            } else {
                var json_data = JSON.parse(event.data);
                var minutes = parseFloat(json_data['time']);
                timer.createDonation(parseInt(minutes), json_data['name']);
                await timer.addTime(minutes);
            }
        });
    }

    if (stopped) timer.stopCountdown();

    connectWebsocket();
}
