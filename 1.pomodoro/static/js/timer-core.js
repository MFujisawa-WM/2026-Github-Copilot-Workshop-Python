/**
 * TimerCore - Pure Business Logic for Pomodoro Timer
 * 
 * This class contains only the timer calculation logic without any side effects.
 * It is responsible for:
 * - Managing elapsed time
 * - Calculating remaining time
 * - Determining completion status
 * - Calculating progress ratio
 */

class TimerCore {
    /**
     * Initialize a new Pomodoro session
     * @param {number} workMinutes - Duration of work session (default: 25)
     * @param {number} breakMinutes - Duration of break session (default: 5)
     */
    constructor(workMinutes = 25, breakMinutes = 5) {
        this.workSeconds = workMinutes * 60;
        this.breakSeconds = breakMinutes * 60;
        this.elapsedSeconds = 0;
    }

    /**
     * Increment elapsed time by 1 second
     * Called once per second during active timer
     */
    tick() {
        this.elapsedSeconds++;
    }

    /**
     * Get remaining time in seconds (pure function, no side effects)
     * @returns {number} Remaining seconds
     */
    getRemaining() {
        return Math.max(0, this.workSeconds - this.elapsedSeconds);
    }

    /**
     * Check if session is complete
     * @returns {boolean} True if elapsed time >= work time
     */
    isComplete() {
        return this.elapsedSeconds >= this.workSeconds;
    }

    /**
     * Calculate progress ratio (0.0 to 1.0)
     * @returns {number} Progress ratio
     */
    getProgressRatio() {
        if (this.workSeconds === 0) {
            return 0;
        }
        return Math.min(1, this.elapsedSeconds / this.workSeconds);
    }

    /**
     * Reset timer to initial state
     */
    reset() {
        this.elapsedSeconds = 0;
    }

    /**
     * Format remaining time as MM:SS string
     * @returns {string} Formatted time (e.g., "24:59")
     */
    formatTime() {
        const seconds = this.getRemaining();
        const minutes = Math.floor(seconds / 60);
        const secs = seconds % 60;
        return `${String(minutes).padStart(2, '0')}:${String(secs).padStart(2, '0')}`;
    }
}

// Export for testing (if using modules)
if (typeof module !== 'undefined' && module.exports) {
    module.exports = TimerCore;
}
