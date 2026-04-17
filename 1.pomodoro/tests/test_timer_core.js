/**
 * Unit Tests for timer-core.js using Jest
 * 
 * Test coverage for TimerCore class:
 * - Session initialization
 * - Time calculations
 * - Completion detection
 * - Progress tracking
 */

// Load the module under test
const TimerCore = require('../static/js/timer-core.js');

describe('TimerCore', () => {
    let timer;

    beforeEach(() => {
        timer = new TimerCore(25, 5); // 25 min work, 5 min break
    });

    describe('Initialization', () => {
        test('initializes with correct duration', () => {
            expect(timer.workSeconds).toBe(1500); // 25 * 60
            expect(timer.breakSeconds).toBe(300); // 5 * 60
            expect(timer.elapsedSeconds).toBe(0);
        });

        test('initializes with custom durations', () => {
            const customTimer = new TimerCore(10, 3);
            expect(customTimer.workSeconds).toBe(600);
            expect(customTimer.breakSeconds).toBe(180);
        });
    });

    describe('tick() method', () => {
        test('increments elapsed seconds', () => {
            expect(timer.elapsedSeconds).toBe(0);
            timer.tick();
            expect(timer.elapsedSeconds).toBe(1);
        });

        test('increments multiple times', () => {
            timer.tick();
            timer.tick();
            timer.tick();
            expect(timer.elapsedSeconds).toBe(3);
        });
    });

    describe('getRemaining() method', () => {
        test('returns full duration at start', () => {
            expect(timer.getRemaining()).toBe(1500);
        });

        test('decreases after ticks', () => {
            timer.elapsedSeconds = 300;
            expect(timer.getRemaining()).toBe(1200);
        });

        test('returns 0 when complete', () => {
            timer.elapsedSeconds = 1500;
            expect(timer.getRemaining()).toBe(0);
        });

        test('never returns negative', () => {
            timer.elapsedSeconds = 2000;
            expect(timer.getRemaining()).toBe(0);
        });
    });

    describe('isComplete() method', () => {
        test('returns false at start', () => {
            expect(timer.isComplete()).toBe(false);
        });

        test('returns false before end', () => {
            timer.elapsedSeconds = 1499;
            expect(timer.isComplete()).toBe(false);
        });

        test('returns true at end time', () => {
            timer.elapsedSeconds = 1500;
            expect(timer.isComplete()).toBe(true);
        });

        test('returns true after end time', () => {
            timer.elapsedSeconds = 2000;
            expect(timer.isComplete()).toBe(true);
        });
    });

    describe('getProgressRatio() method', () => {
        test('returns 0 at start', () => {
            expect(timer.getProgressRatio()).toBe(0);
        });

        test('returns 0.5 at midpoint', () => {
            timer.elapsedSeconds = 750; // 12.5 min
            expect(timer.getProgressRatio()).toBe(0.5);
        });

        test('returns 1 at completion', () => {
            timer.elapsedSeconds = 1500;
            expect(timer.getProgressRatio()).toBe(1);
        });

        test('never exceeds 1', () => {
            timer.elapsedSeconds = 2000;
            expect(timer.getProgressRatio()).toBe(1);
        });

        test('returns 0.75 at 75% progress', () => {
            timer.elapsedSeconds = 1125; // 18.75 min
            expect(timer.getProgressRatio()).toBe(0.75);
        });
    });

    describe('reset() method', () => {
        test('clears elapsed time', () => {
            timer.elapsedSeconds = 500;
            timer.reset();
            expect(timer.elapsedSeconds).toBe(0);
        });

        test('makes getRemaining() return full time', () => {
            timer.elapsedSeconds = 500;
            timer.reset();
            expect(timer.getRemaining()).toBe(1500);
        });

        test('makes isComplete() return false', () => {
            timer.elapsedSeconds = 1500;
            timer.reset();
            expect(timer.isComplete()).toBe(false);
        });
    });

    describe('formatTime() method', () => {
        test('returns MM:SS format at start', () => {
            expect(timer.formatTime()).toBe('25:00');
        });

        test('pads single-digit seconds with zero', () => {
            const minTimer = new TimerCore(1, 0); // 1 minute
            minTimer.elapsedSeconds = 54; // Remaining: 6 seconds
            expect(minTimer.formatTime()).toBe('00:06');
        });

        test('pads single-digit minutes with zero', () => {
            const minTimer = new TimerCore(1, 0);
            minTimer.elapsedSeconds = 30; // Remaining: 30 seconds
            expect(minTimer.formatTime()).toBe('00:30');
        });

        test('returns 00:00 at completion', () => {
            timer.elapsedSeconds = 1500;
            expect(timer.formatTime()).toBe('00:00');
        });

        test('returns 00:00 after completion', () => {
            timer.elapsedSeconds = 2000;
            expect(timer.formatTime()).toBe('00:00');
        });

        test('formats various intermediate times', () => {
            const minTimer = new TimerCore(1, 0);
            
            minTimer.elapsedSeconds = 0;
            expect(minTimer.formatTime()).toBe('01:00');
            
            minTimer.elapsedSeconds = 15;
            expect(minTimer.formatTime()).toBe('00:45');
            
            minTimer.elapsedSeconds = 35;
            expect(minTimer.formatTime()).toBe('00:25');
        });
    });

    describe('Comprehensive workflow tests', () => {
        test('full session simulation', () => {
            // Initial state
            expect(timer.formatTime()).toBe('25:00');
            expect(timer.isComplete()).toBe(false);
            expect(timer.getProgressRatio()).toBe(0);

            // 5 minutes elapsed
            for (let i = 0; i < 300; i++) {
                timer.tick();
            }
            expect(timer.formatTime()).toBe('20:00');
            expect(timer.getProgressRatio()).toBe(0.2);
            expect(timer.isComplete()).toBe(false);

            // 25 minutes total (completion)
            for (let i = 0; i < 1200; i++) {
                timer.tick();
            }
            expect(timer.formatTime()).toBe('00:00');
            expect(timer.getProgressRatio()).toBe(1);
            expect(timer.isComplete()).toBe(true);
        });

        test('reset after completion', () => {
            timer.elapsedSeconds = 1500;
            expect(timer.isComplete()).toBe(true);

            timer.reset();
            expect(timer.formatTime()).toBe('25:00');
            expect(timer.isComplete()).toBe(false);
            expect(timer.getProgressRatio()).toBe(0);
        });

        test('pause and resume simulation', () => {
            // Work for 5 minutes
            for (let i = 0; i < 300; i++) {
                timer.tick();
            }
            expect(timer.formatTime()).toBe('20:00');

            // Simulate UI state after pause
            const pausedState = {
                elapsed: timer.elapsedSeconds,
                remaining: timer.getRemaining(),
                progress: timer.getProgressRatio()
            };

            expect(pausedState.elapsed).toBe(300);
            expect(pausedState.remaining).toBe(1200);
            expect(pausedState.progress).toBeCloseTo(0.2);

            // Resume - continue working
            for (let i = 0; i < 300; i++) {
                timer.tick();
            }
            expect(timer.formatTime()).toBe('15:00');
        });
    });

    describe('Edge cases', () => {
        test('handles very short session', () => {
            const shortTimer = new TimerCore(0.5, 0); // 30 seconds
            expect(shortTimer.workSeconds).toBe(30);
            shortTimer.elapsedSeconds = 15;
            expect(shortTimer.getProgressRatio()).toBe(0.5);
        });

        test('handles very long session', () => {
            const longTimer = new TimerCore(120, 10); // 2 hours
            expect(longTimer.workSeconds).toBe(7200);
            longTimer.elapsedSeconds = 3600; // 1 hour
            expect(longTimer.getProgressRatio()).toBe(0.5);
        });

        test('formatTime handles large elapsed values', () => {
            const minTimer = new TimerCore(1, 0);
            minTimer.elapsedSeconds = 10000; // Way beyond work time
            expect(minTimer.formatTime()).toBe('00:00'); // Should still be 00:00
        });
    });
});

// Mock storage for testing (used in other test files)
class MockStorage {
    constructor() {
        this.data = {};
    }

    setItem(key, value) {
        this.data[key] = value;
    }

    getItem(key) {
        return this.data[key] || null;
    }

    removeItem(key) {
        delete this.data[key];
    }

    clear() {
        this.data = {};
    }
}
