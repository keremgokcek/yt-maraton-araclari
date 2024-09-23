class Timer {
    constructor(timestamp) {
        this.seconds = document.getElementById("seconds");
        this.minutes = document.getElementById("minutes");
        this.hours = document.getElementById("hours");
        this.days = document.getElementById("days");
        this.boxes = document.querySelectorAll('.box');
        this.donations = document.getElementById("donations");

        this.end = new Date(timestamp);
        this.animMinutes = 0;
        this.days_hidden = days_hidden;
        this.stopped_seconds = 0;

        this.step = 0;
        this.wait_time = 0;
    }

    createDonationString(minutes) {
        if (minutes < 1) {
            return `+${Math.floor(minutes*60)} SANİYE`
        } else if (minutes < 20) {
            return `+${parseFloat(minutes.toFixed(2))} DAKİKA`
        } else {
            return `+${Math.floor(minutes)} DAKİKA`
        }
    }

    getSeconds() {
        if (this.stopped_seconds) {
            return this.stopped_seconds;
        } else {
            return Math.max(0, Math.floor((this.end - new Date()) / 1000));
        }
    }

    parseCountdown(total_seconds) {
        var days = Math.floor(total_seconds / (60 * 60 * 24));
        var hours = Math.floor((total_seconds % (60 * 60 * 24)) / (60 * 60));
        var minutes = Math.floor((total_seconds % (60 * 60)) / 60);
        var seconds = Math.floor(total_seconds % 60);
        return {days: days, hours: hours, minutes: minutes, seconds: seconds};
    }

    async addTime(minutes) {
        if (this.animMinutes) {
            this.animMinutes += minutes;
            this.setIntervals(this.animMinutes + minutes);
        } else {
            if (minutes < 0) {
                if (this.stopped_seconds) this.stopped_seconds += minutes * 60;
                this.addWithoutAnimation(minutes);
            } else {
                await this.addWithAnimation(minutes);
            }
        }
    }

    setIntervals(minutes) {
        if (minutes < 5) {  // YT 25 TRY / BYNO-OYUNFOR 12.5 TRY
            this.wait_time = 30;
            this.step = minutes;
        } else if (minutes < 180) {  // YT 600 TRY / BYNO-OYUNFOR 300 TRY
            this.wait_time = 20;
            this.step = minutes / 4;
        } else {
            this.wait_time = 10;
            this.step = minutes / 5;
        }
    }

    addWithoutAnimation(minutes) {
        this.end = new Date(this.end.getTime() + minutes * 60000);
        this.updateCountdown();
    }

    async addWithAnimation(minutes) {
        console.log(minutes);
        var countdown = this.parseCountdown(this.getSeconds());
        this.animMinutes = minutes;
        this.checkForDays(countdown);
        this.setIntervals(minutes);
        var current_seconds = this.getSeconds();
        while (true) {
            var countdown = this.parseCountdown(current_seconds);
            this.checkForDays(countdown);
            this.days.innerHTML = String(countdown.days).padStart(2, "0");
            this.hours.innerHTML = String(countdown.hours).padStart(2, "0");
            this.minutes.innerHTML = String(countdown.minutes).padStart(2, "0");
            this.seconds.innerHTML = String(countdown.seconds).padStart(2, "0");
            var target_seconds = this.getSeconds() + this.animMinutes * 60;
            if (current_seconds == target_seconds) break; 
            current_seconds += this.step;
            if (current_seconds > target_seconds) current_seconds = target_seconds;
            await new Promise(res => setTimeout(res, this.wait_time));
        }
        if (this.stopped_seconds) {
            this.stopped_seconds += this.animMinutes * 60;
        } else {
            this.end = new Date(this.end.getTime() + this.animMinutes * 60000);
        }
        this.animMinutes = 0;
    }

    updateCountdown() {
        var countdown = this.parseCountdown(this.getSeconds());
        this.checkForDays(countdown);
        this.days.innerHTML = String(countdown.days).padStart(2, "0");
        this.hours.innerHTML = String(countdown.hours).padStart(2, "0");
        this.minutes.innerHTML = String(countdown.minutes).padStart(2, "0");
        this.seconds.innerHTML = String(countdown.seconds).padStart(2, "0");
        if (this.getSeconds() == 0 || this.stopped_seconds) {
            setTimeout(() => {
                this.days.innerHTML = '';
                this.hours.innerHTML = '';
                this.minutes.innerHTML = '';
                this.seconds.innerHTML = '';
            }, 600);
        }
    }

    checkForDays(countdown) {
        if (countdown.days == 0 && !this.days_hidden) {
            this.days_hidden = true;
            this.hideDays();
        } else if (countdown.days > 0 && this.days_hidden) {
            this.days_hidden = false;
            this.showDays();
        }
    }

    hideDays() {
        document.getElementById("day-box").style.opacity = 0;
        this.boxes.forEach((box, _index) => {
            box.style.animation = `disappear 1s ease-in-out forwards`;
        });
        setTimeout(() => {
            this.boxes.forEach((box, _index) => {
                box.style.animation = `none`;
            });
            document.getElementById("day-box").style.display = "none";
        }, 1000)
    }
    
    showDays() {
        document.getElementById("day-box").style.display = "inline";
        setTimeout(() => {document.getElementById("day-box").style.opacity = 1;}, 10);
        this.boxes.forEach((box, _index) => {
            box.style.transform = `translateX(-71px)`;
            box.style.animation = `reappear 1s ease-in-out forwards`;
        });
        setTimeout(() => {
            this.boxes.forEach((box, _index) => {
                box.style.transform = `translateX(0px)`;
                box.style.animation = `none`;
            });
        }, 1000)
    }

    createDonation(time, name) {
        var donation = document.createElement('div');
        donation.classList.add('new-donation');

        var donateAmount = document.createElement('div');
        donateAmount.id = 'donate-time';
        donateAmount.innerHTML = this.createDonationString(time);

        var donatorName = document.createElement('div');
        donatorName.id = 'donator-name';
        donatorName.innerHTML = name;

        donation.appendChild(donatorName);
        donation.appendChild(donateAmount);
        this.donations.appendChild(donation);
        
        setTimeout(() => {
            donation.classList.add('remove-donation');
            setTimeout(() => {
                donation.remove();
            }, 2000);
        }, 4000);
    }

    startCountdown() {
        this.updateCountdown();
        setInterval(() => {
            if (!this.animMinutes) this.updateCountdown();
        }, 1000);
    }

    setNewTime(timestamp) {
        this.end = new Date(timestamp);
    }

    stopCountdown() {
        if (!this.stopped_seconds)
            this.stopped_seconds = this.getSeconds();
    }

    continueCountdown() {
        if (this.stopped_seconds) {
            this.end = new Date(new Date().getTime() + this.stopped_seconds * 1000);
            this.stopped_seconds = 0;
        }
    }
}

export default Timer;
