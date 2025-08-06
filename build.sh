#!/usr/bin/env bash
# Exit on error
set -o errexit

echo "🔨 Starting build process for Story Quiz..."

# Upgrade pip
echo "📦 Upgrading pip..."
pip install --upgrade pip

# Install Python dependencies
echo "🐍 Installing Python dependencies..."
pip install -r requirements.txt

# Install gunicorn for production
echo "🚀 Installing Gunicorn for production..."
pip install gunicorn

# Verify installations
echo "✅ Verifying installations..."
python -c "import flask; import pymongo; print('✅ Core dependencies installed')"

# Create necessary directories if they don't exist
mkdir -p static/images
mkdir -p templates

echo "🎉 Build completed successfully!"