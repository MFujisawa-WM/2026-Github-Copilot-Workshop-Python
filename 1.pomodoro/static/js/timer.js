/**
 * TimerUI - UI Control Layer for Pomodoro Timer
 * 
 * This class handles all UI interactions and DOM updates:
 * - Event listener setup
 * - Display updates
 * - User interactions (start, stop, reset)
 * - Session completion handling
 */

class TimerUI {
    /**
     * Initialize TimerUI with dependencies
     * @param {TimerCore} timerCore - Timer logic instance
     * @param {StorageAPI} storageAPI - Storage API instance
     */
    constructor(timerCore, storageAPI) {
        this.timer = timerCore;
        this.storage = storageAPI;

        // DOM Elements
        this.dom = {
            timeDisplay: document.querySelector('.time'),
            startBtn: document.querySelector('.btn-start'),
            resetBtn: document.querySelector('.btn-reset'),
            status: document.querySelector('.status'),
            completeCount: document.querySelector('.stat-complete'),
            totalMinutes: document.querySelector('.stat-minutes'),
            progressArc: document.querySelector('.progress-arc')
        };

        this.intervalId = null;
        this.setupListeners();
    }

    /**
     * Setup event listeners for buttons
     */
    setupListeners() {
        if (this.dom.startBtn) {
            this.dom.startBtn.addEventListener('click', () => this.onStartClick());
        }
        if (this.dom.resetBtn) {
            this.dom.resetBtn.addEventListener('click', () => this.onResetClick());
        }
    }

    /**
     * Handle start/pause button click
     */
    onStartClick() {
        if (this.intervalId) {
            // Pause
            clearInterval(this.intervalId);
            this.intervalId = null;
            this.dom.startBtn.textContent = '開始';
        } else {
            // Start
            this.dom.startBtn.textContent = '一時停止';
            this.intervalId = setInterval(() => {
                this.timer.tick();
                this.updateDisplay();

                if (this.timer.isComplete()) {
                    clearInterval(this.intervalId);
                    this.intervalId = null;
                    this.onSessionComplete();
                }
            }, 1000);
        }
    }

    /**
     * Handle reset button click
     */
    onResetClick() {
        if (this.intervalId) {
            clearInterval(this.intervalId);
            this.intervalId = null;
        }
        this.timer.reset();
        this.updateDisplay();
        this.dom.startBtn.textContent = '開始';
    }

    /**
     * Update display elements (time and progress)
     */
    updateDisplay() {
        // Update time display
        if (this.dom.timeDisplay) {
            this.dom.timeDisplay.textContent = this.timer.formatTime();
        }

        // Update circle progress
        this.updateCircleProgress();

        // Update title bar
        this.updateTitleBar();
    }

    /**
     * Update SVG circle progress
     */
    updateCircleProgress() {
        if (!this.dom.progressArc) return;

        const ratio = this.timer.getProgressRatio();
        const radius = 150;
        const circumference = 2 * Math.PI * radius;
        const offset = circumference * (1 - ratio);

        this.dom.progressArc.style.strokeDashoffset = offset;
    }

    /**
     * Update browser title bar with current time
     */
    updateTitleBar() {
        const formattedTime = this.timer.formatTime();
        document.title = `${formattedTime} - ポモドーロタイマー`;
    }

    /**
     * Handle session completion
     */
    onSessionComplete() {
        try {
            this.storage.updateStats(25);
            this.playCompleteSound();
            this.showToastNotification('セッション完了！お疲れさまでした。');
            this.loadStatsDisplay();
            this.timer.reset();
            this.updateDisplay();
            if (this.dom.startBtn) {
                this.dom.startBtn.textContent = '開始';
            }
        } catch (error) {
            console.error('Session completion error:', error);
            this.showErrorNotification('エラーが発生しました');
        }
    }

    /**
     * Load and display statistics from storage
     */
    loadStatsDisplay() {
        const stats = this.storage.loadStats();
        if (this.dom.completeCount) {
            this.dom.completeCount.textContent = stats.completed;
        }
        if (this.dom.totalMinutes) {
            this.dom.totalMinutes.textContent = this.formatMinutesToHM(stats.totalMinutes);
        }
    }

    /**
     * Convert minutes to hours and minutes format
     * @param {number} minutes - Total minutes
     * @returns {string} Formatted string (e.g., "1時間40分")
     */
    formatMinutesToHM(minutes) {
        const hours = Math.floor(minutes / 60);
        const mins = minutes % 60;
        if (hours === 0) {
            return `${mins}分`;
        }
        return `${hours}時間${mins}分`;
    }

    /**
     * Show toast notification
     * @param {string} message - Notification message
     */
    showToastNotification(message) {
        const toast = document.createElement('div');
        toast.className = 'toast';
        toast.textContent = message;
        document.body.appendChild(toast);

        setTimeout(() => {
            toast.style.opacity = '0';
            setTimeout(() => toast.remove(), 300);
        }, 3000);
    }

    /**
     * Show error notification
     * @param {string} message - Error message
     */
    showErrorNotification(message) {
        const toast = document.createElement('div');
        toast.className = 'toast';
        toast.style.background = '#ef4444';
        toast.textContent = message;
        document.body.appendChild(toast);

        setTimeout(() => {
            toast.style.opacity = '0';
            setTimeout(() => toast.remove(), 300);
        }, 3000);
    }

    /**
     * Play completion sound using Web Audio API
     */
    playCompleteSound() {
        try {
            const audioContext = new (window.AudioContext || window.webkitAudioContext)();
            const oscillator = audioContext.createOscillator();
            const gain = audioContext.createGain();

            oscillator.connect(gain);
            gain.connect(audioContext.destination);

            oscillator.frequency.value = 1000;
            oscillator.type = 'sine';

            gain.gain.setValueAtTime(0.3, audioContext.currentTime);
            gain.gain.exponentialRampToValueAtTime(0.01, audioContext.currentTime + 0.5);

            oscillator.start();
            oscillator.stop(audioContext.currentTime + 0.5);
        } catch (error) {
            console.warn('Failed to play sound:', error);
        }
    }
}

/**
 * Initialize application on page load
 */
document.addEventListener('DOMContentLoaded', () => {
    const timerCore = new TimerCore(25, 5);
    const storageAPI = new StorageAPI();
    const timerUI = new TimerUI(timerCore, storageAPI);

    // Initialize display
    timerUI.loadStatsDisplay();
    timerUI.updateDisplay();

    // Make globally accessible for debugging
    window.timerCore = timerCore;
    window.storageAPI = storageAPI;
    window.timerUI = timerUI;
});

// Export for testing (if using modules)
if (typeof module !== 'undefined' && module.exports) {
    module.exports = TimerUI;
}
