import os

# Bind to the port that Render provides via the PORT environment variable
bind = f"0.0.0.0:{os.environ.get('PORT', 8000)}"

# Worker configuration
workers = 2
threads = 2
worker_class = 'sync'
worker_connections = 1000
max_requests = 1000
max_requests_jitter = 50

# Timeout configuration
timeout = 300
graceful_timeout = 60
keepalive = 2

# Logging
accesslog = '-'
errorlog = '-'
loglevel = 'info'

# Preload app for better performance
preload_app = True

print(f"Gunicorn starting on {bind}")