#!/bin/bash
# Start script for Render deployment

# Debug: Print the PORT value
echo "PORT environment variable is: $PORT"

# Use gunicorn for production - bind to the PORT that Render provides
exec gunicorn app:app --bind 0.0.0.0:${PORT} --workers 1 --threads 2 --timeout 120