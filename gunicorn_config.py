import os

# Debug: Check what PORT Render is providing
print(">>> Gunicorn binding to PORT:", os.environ.get("PORT"))
print(">>> Full bind address will be:", f"0.0.0.0:{os.environ.get('PORT', '8000')}")

# Bind to the port that Render provides via the PORT environment variable
bind = f"0.0.0.0:{os.environ.get('PORT', '8000')}"

# Worker configuration  
workers = 4
threads = 4
worker_class = 'gthread'
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