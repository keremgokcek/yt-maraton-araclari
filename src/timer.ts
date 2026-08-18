declare const days_hidden: boolean;

interface Countdown {
    days: number;
    hours: number;
    minutes: number;
    seconds: number;
}

export class Timer {
    private seconds: HTMLElement;
    private minutes: HTMLElement;
    private hours: HTMLElement;
    private days: HTMLElement;
    private boxes: NodeListOf<HTMLElement>;
    private donations: HTMLElement;

    private banner: HTMLElement;
    private banner_text: HTMLElement;

    private end: Date;
    private animMinutes: number;
    private days_hidden: boolean;
    private stopped_seconds: number;
    private banner_running: boolean;

    private step: number;
    private wait_time: number;

    constructor(timestamp: number) {

        this.seconds = document.getElementById("seconds")!;
        this.minutes = document.getElementById("minutes")!;
        this.hours = document.getElementById("hours")!;
        this.days = document.getElementById("days")!;
        this.boxes = document.querySelectorAll('.box');
        this.donations = document.getElementById("donations")!;

        this.banner = document.getElementById("banner")!;
        this.banner_text = document.getElementById("banner-text")!;

        this.end = new Date(timestamp);
        this.animMinutes = 0;
        this.days_hidden = days_hidden;
        this.stopped_seconds = 0;
        this.banner_running = false;

        this.step = 0;
        this.wait_time = 0;
    }

    private createDonationString(minutes: number) {
        if (minutes < 1) {
            return `+${Math.floor(minutes * 60)} SANİYE`
        } else if (minutes < 20) {
            return `+${parseFloat(minutes.toFixed(2))} DAKİKA`
        } else {
            return `+${Math.floor(minutes)} DAKİKA`
        }
    }

    private getSeconds() {
        return this.stopped_seconds || Math.max(0, Math.floor((this.end.getTime() - new Date().getTime()) / 1000));
    }

    private parseCountdown(total_seconds: number) {
        var days = Math.floor(total_seconds / (60 * 60 * 24));
        var hours = Math.floor((total_seconds % (60 * 60 * 24)) / (60 * 60));
        var minutes = Math.floor((total_seconds % (60 * 60)) / 60);
        var seconds = Math.floor(total_seconds % 60);
        return { days: days, hours: hours, minutes: minutes, seconds: seconds };
    }

    async addTime(minutes: number) {
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

    private setIntervals(minutes: number) {
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

    private addWithoutAnimation(minutes: number) {
        this.end = new Date(this.end.getTime() + minutes * 60000);
        this.updateCountdown();
    }

    private async addWithAnimation(minutes: number) {
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

    private updateCountdown() {
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

    private checkForDays(countdown: Countdown) {
        if (countdown.days == 0 && !this.days_hidden) {
            this.days_hidden = true;
            this.hideDays();
        } else if (countdown.days > 0 && this.days_hidden) {
            this.days_hidden = false;
            this.showDays();
        }
    }

    private hideDays() {
        const dayBox = document.getElementById("day-box")!;
        dayBox.style.opacity = "0";

        this.boxes.forEach((box, _index) => {
            box.style.animation = `disappear 1s ease-in-out forwards`;
        });
        setTimeout(() => {
            this.boxes.forEach((box, _index) => {
                box.style.animation = `none`;
            });
            dayBox.style.display = "none";
        }, 1000)
    }

    private showDays() {
        const dayBox = document.getElementById("day-box")!;
        dayBox.style.display = "inline";
        setTimeout(() => { dayBox.style.opacity = "1"; }, 10);
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

    private showBanner(text: string) {
        if (this.banner_running) return;

        this.banner_running = true;

        this.banner.classList.add("active");
        this.banner_text.textContent = text;
        setTimeout(() => {
            this.banner_text.classList.add("sliding");
            setTimeout(() => {
                this.banner_text.classList.remove("sliding");
                setTimeout(() => {
                    this.banner_text.classList.add("sliding");
                    setTimeout(() => {
                        this.banner_text.classList.remove("sliding");
                        this.banner.classList.remove("active");
                        this.banner_running = false;
                    }, 11000);
                }, 100);
            }, 10000);
        }, 1500);
    }

    showReminder() {
        this.showBanner(`SAYAÇ ${this.end.getHours()}.${this.end.getMinutes()}'DE BİTİYOR               DESTEKLERİ UNUTMAYALIM`);
    }

    createDonation(time: number, name: string) {
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

    setNewTime(timestamp: number) {
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