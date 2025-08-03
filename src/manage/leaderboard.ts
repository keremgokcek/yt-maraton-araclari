const protocol = window.location.protocol === 'https:' ? 'wss' : 'ws';
var ws: WebSocket;

window.onload = () => {
    const donations = document.querySelectorAll(".donation-card") as NodeListOf<HTMLElement>;
    const new_entry_area = document.querySelector(".new-entry-area") as HTMLElement;

    donations.forEach((donation) => {
        donation.addEventListener('mousedown', (e) => {
            // Show new table entry button
            new_entry_area.style.right = '-20px';

            const clonedDonation = donation.cloneNode(true) as HTMLElement;
            document.body.appendChild(clonedDonation);

            donation.style.opacity = "0";

            clonedDonation.classList.add("dragging");
            clonedDonation.style.width = clonedDonation.offsetWidth + "px";
            clonedDonation.style.maxWidth = "600px";
            clonedDonation.style.position = "absolute";
            clonedDonation.style.pointerEvents = "none";
            (clonedDonation.querySelector('.message') as HTMLElement)!.style.textWrap = 'wrap';

            if (!document.elementsFromPoint(e.pageX, e.pageY).includes(clonedDonation)) {
                clonedDonation.style.left = e.clientX - clonedDonation.offsetWidth / 2 + "px";
                clonedDonation.style.top = e.clientY - clonedDonation.offsetHeight / 2 + "px";
            } else {
                clonedDonation.style.left = clonedDonation.getBoundingClientRect().left + "px";
                clonedDonation.style.top = clonedDonation.getBoundingClientRect().top + "px";
            }

            const shiftX = e.clientX - clonedDonation.getBoundingClientRect().left;
            const shiftY = e.clientY - clonedDonation.getBoundingClientRect().top;

            let lastRow: HTMLTableRowElement | null = null;
            document.onmousemove = (e) => {
                clonedDonation.style.left = e.pageX - shiftX + "px";
                clonedDonation.style.top = e.pageY - shiftY + "px";

                if (!(e.target instanceof Element)) return;
                let target = e.target.closest('td');
                if (!target) {
                    if (lastRow) {
                        lastRow.style.height = '';
                        lastRow = null;
                    };
                    return;
                };
                if (lastRow == target.parentElement) return;
                if (lastRow) lastRow.style.height = '';
                target.parentElement!.style.height = "100px";
                lastRow = target.parentElement as HTMLTableRowElement;
            };

            document.onmouseup = function (e) {
                new_entry_area.style.right = '-1000px';

                document.body.removeChild(clonedDonation);

                document.onmousemove = null;
                document.onmouseup = null;

                // Create new entry
                if (new_entry_area.matches(':hover')) {
                    removeDonation(donation);
                    // TODO: Add new entry to table without refreshing the page
                    ws.send(JSON.stringify({
                        type: 'create',
                        source: donation.dataset.id
                    }));
                    setTimeout(() => document.location.reload(), 1000);
                    return;
                }

                if (!(e.target instanceof Element)) return;
                const target = e.target.closest('td');
                if (!target) {
                    donation.removeAttribute("style");
                    return;
                };

                // Dragged to a row
                target.parentElement!.style.height = '';
                const name = target.parentElement!.querySelector("td")!.textContent;
                console.log(name);

                removeDonation(donation);

                // TODO: Update table value without refreshing the page
                ws.send(JSON.stringify({
                    type: 'update',
                    target: target.parentElement!.dataset.id,
                    source: donation.dataset.id
                }));
                setTimeout(() => document.location.reload(), 1000);
            };
        });
    });
}



function removeDonation(donation: HTMLElement) {
    donation.onmousedown = null;
    donation.style.height = donation.offsetHeight + 'px';
    donation.style.border = '0';
    donation.textContent = '';
    setTimeout(() => {
        donation.style.transition = 'height 0.5s, padding 0.5s, margin 0.5s';
        donation.style.height = '0px';
        donation.style.padding = '0px';
        donation.style.margin = '0px';

        setTimeout(() => donation.parentElement!.removeChild(donation), 500)
    }, 100)
}

connectWebsocket();
function connectWebsocket() {
    ws = new WebSocket(`${protocol}://${window.location.host}/manage/leaderboard`);
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
        console.log('Message from server:', event.data);
        if (event.data === 'pong') return;
    })
}
