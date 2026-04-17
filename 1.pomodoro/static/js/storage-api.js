/**
 * StorageAPI - LocalStorage Wrapper for Data Persistence
 * 
 * This class abstracts localStorage operations and handles:
 * - Session data persistence
 * - Statistics tracking
 * - Date-based statistics reset
 * - Dependency injection for testing
 */

class StorageAPI {
    /**
     * Initialize StorageAPI with optional DI for testing
     * @param {Storage} storageImpl - Storage implementation (default: window.localStorage)
     */
    constructor(storageImpl = null) {
        this.storage = storageImpl || window.localStorage;
    }

    /**
     * Save session data to storage
     * @param {Object} sessionData - Session data to save
     */
    saveSession(sessionData) {
        try {
            this.storage.setItem('pomodoro_session', JSON.stringify(sessionData));
        } catch (error) {
            console.error('Failed to save session:', error);
        }
    }

    /**
     * Load statistics from storage, with date-based reset
     * @returns {Object} Statistics object {completed, totalMinutes, date}
     */
    loadStats() {
        const today = new Date().toISOString().split('T')[0];
        const data = this.storage.getItem('pomodoro_stats');

        if (!data) {
            return { completed: 0, totalMinutes: 0, date: today };
        }

        try {
            const stats = JSON.parse(data);

            // Reset if date has changed
            if (stats.date !== today) {
                this.storage.removeItem('pomodoro_stats');
                return { completed: 0, totalMinutes: 0, date: today };
            }

            return stats;
        } catch (error) {
            console.error('Failed to parse stats:', error);
            return { completed: 0, totalMinutes: 0, date: today };
        }
    }

    /**
     * Update statistics after session completion
     * @param {number} minutes - Minutes completed
     */
    updateStats(minutes) {
        const today = new Date().toISOString().split('T')[0];
        const current = this.loadStats();

        current.completed += 1;
        current.totalMinutes += minutes;
        current.date = today;

        try {
            this.storage.setItem('pomodoro_stats', JSON.stringify(current));
        } catch (error) {
            console.error('Failed to update stats:', error);
        }
    }

    /**
     * Clear all stored data
     */
    clearAll() {
        try {
            this.storage.removeItem('pomodoro_session');
            this.storage.removeItem('pomodoro_stats');
        } catch (error) {
            console.error('Failed to clear data:', error);
        }
    }

    /**
     * Check if date has changed since last session
     * @returns {boolean} True if today is a new day
     */
    isNewDay() {
        const today = new Date().toISOString().split('T')[0];
        const stats = this.loadStats();
        return stats.date !== today;
    }
}

// Export for testing (if using modules)
if (typeof module !== 'undefined' && module.exports) {
    module.exports = StorageAPI;
}
