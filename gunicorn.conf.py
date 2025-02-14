import os

port = os.getenv("PORT", "8000")
bind = f"0.0.0.0:{port}"
workers = 2
threads = 2
timeout = 120
keepalive = 2
worker_class = "gthread"
worker_connections = 1000
max_requests = 1000
max_requests_jitter = 50
graceful_timeout = 30
log_level = "debug"
accesslog = "-"
errorlog = "-"
capture_output = True
enable_stdio_inheritance = True 