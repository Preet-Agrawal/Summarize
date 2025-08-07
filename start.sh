#!/bin/bash
# Start script for Render deployment

# Use gunicorn for production
exec gunicorn app:app --bind 0.0.0.0:${PORT:-5000} --workers 1 --threads 2 --timeout 120