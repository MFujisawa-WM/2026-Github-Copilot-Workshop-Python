/**
 * Jest Configuration for Pomodoro Timer JavaScript Tests
 */

module.exports = {
    // Test environment
    testEnvironment: 'jsdom',

    // Test discovery patterns
    testMatch: [
        '**/tests/**/*.test.js',
        '**/tests/**/*.spec.js',
        '**/tests/**/test_*.js'
    ],

    // Coverage configuration
    collectCoverageFrom: [
        'static/js/**/*.js',
        '!static/js/**/*.test.js'
    ],

    coverageThreshold: {
        global: {
            branches: 80,
            functions: 80,
            lines: 80,
            statements: 80
        }
    },

    // Module name mapper for static files
    moduleNameMapper: {
        '\\.(css|less|scss|sass)$': 'identity-obj-proxy'
    },

    // Setup files
    setupFilesAfterEnv: ['<rootDir>/jest.setup.js'],

    // Verbose output
    verbose: true,

    // Coverage reporter
    reporters: ['default']
};
