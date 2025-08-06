#!/usr/bin/env bash
# Render.com build script
set -o errexit

echo "🚀 Starting Render build for Story Quiz..."
echo "📍 Python version: $(python --version)"
echo "📍 Node version: $(node --version 2>/dev/null || echo 'Node not installed')"

# Install Python dependencies
echo "📦 Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Install production server
echo "🔧 Installing Gunicorn..."
pip install gunicorn

# Verify critical dependencies
echo "✅ Verifying dependencies..."
python -c "
import sys
print(f'Python: {sys.version}')
try:
    import flask
    print('✅ Flask installed')
except ImportError:
    print('❌ Flask not found')
    sys.exit(1)
    
try:
    import pymongo
    print('✅ PyMongo installed')
except ImportError:
    print('❌ PyMongo not found')
    sys.exit(1)
    
try:
    import gunicorn
    print('✅ Gunicorn installed')
except ImportError:
    print('❌ Gunicorn not found')
    sys.exit(1)

try:
    import groq
    print('✅ Groq API client installed')
except ImportError:
    print('❌ Groq not found')
    sys.exit(1)

print('✅ All critical dependencies verified')
"

# Create required directories
echo "📁 Creating directories..."
mkdir -p static/images
mkdir -p templates

echo "✨ Build completed successfully!"
echo "🌐 Ready for deployment on Render"