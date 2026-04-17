/**
 * Jest Setup File
 * This file runs before all tests
 */

// Simple localStorage mock for testing
global.localStorage = {
    data: {},
    getItem(key) {
        return this.data[key] || null;
    },
    setItem(key, value) {
        this.data[key] = String(value);
    },
    removeItem(key) {
        delete this.data[key];
    },
    clear() {
        this.data = {};
    },
};
