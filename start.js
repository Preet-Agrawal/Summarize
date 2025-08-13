#!/usr/bin/env node

/**
 * Cross-platform starter script for Story Quiz Flask application
 */

const { spawn } = require('child_process');
const os = require('os');
const path = require('path');
require('dotenv').config();

// Determine Python command based on OS
const isWindows = os.platform() === 'win32';
const pythonCmd = isWindows ? 'python' : 'python3';

// Set environment variables
const env = { ...process.env };
if (!env.FLASK_ENV) {
    env.FLASK_ENV = 'development';
}
if (!env.HOST) {
    env.HOST = process.env.HOST || '0.0.0.0';
}
if (!env.PORT) {
    env.PORT = process.env.PORT || '5000';
}

console.log('🚀 Starting Story Quiz Application...');
console.log(`📍 Environment: ${env.FLASK_ENV}`);
console.log(`🌐 URL: http://${env.HOST}:${env.PORT}`);
console.log('');

// Start the Flask application
const flask = spawn(pythonCmd, ['app.py'], {
    env: env,
    stdio: 'inherit',
    shell: isWindows
});

// Handle process termination
flask.on('error', (err) => {
    console.error('❌ Failed to start application:', err.message);
    console.error('Make sure Python and all dependencies are installed.');
    console.error('Run: npm run setup');
    process.exit(1);
});

flask.on('close', (code) => {
    if (code !== 0) {
        console.error(`❌ Application exited with code ${code}`);
    } else {
        console.log('✅ Application stopped successfully');
    }
    process.exit(code);
});

// Handle Ctrl+C gracefully
process.on('SIGINT', () => {
    console.log('\n⏹️  Stopping application...');
    flask.kill('SIGINT');
});