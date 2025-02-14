import multiprocessing
import os

# Основні налаштування
bind = f"0.0.0.0:{os.getenv('PORT', '8080')}"
workers = 2
worker_class = 'gthread'
threads = 2
timeout = 120
max_requests = 1000
max_requests_jitter = 50
graceful_timeout = 30
keepalive = 5

# Налаштування логування
accesslog = '-'
errorlog = '-'
loglevel = 'info'
capture_output = True
enable_stdio_inheritance = True
logger_class = 'gunicorn.glogging.Logger'

# Налаштування для проксі
forwarded_allow_ips = '*'
proxy_allow_ips = '*'
proxy_protocol = False
secure_scheme_headers = {
    'X-FORWARDED-PROTO': 'https'
}

# Налаштування для файлової системи
worker_tmp_dir = '/dev/shm'
tmp_upload_dir = None

# Налаштування процесу
proc_name = 'meditation_app'
default_proc_name = 'meditation_app.wsgi:application'

# Налаштування користувача
user = None
group = None
umask = 0
initgroups = False

# SSL налаштування
keyfile = None
certfile = None
ssl_version = 2
cert_reqs = 0
ca_certs = None
suppress_ragged_eofs = True
do_handshake_on_connect = False
ciphers = None

# Додаткові налаштування продуктивності
reload = False

# Налаштування для статистики
statsd_host = os.getenv('STATSD_HOST', None)
statsd_prefix = 'meditation_app'

# Обробники подій
def when_ready(server):
    server.log.info("Server is ready. Meditation app is starting...")

def on_starting(server):
    server.log.info("Initializing meditation app server...")

def worker_int(worker):
    worker.log.info("Worker gracefully shutting down...")

def post_fork(server, worker):
    server.log.info(f"Worker {worker.pid} has been forked")

def worker_exit(server, worker):
    from django.db import connections
    for conn in connections.all():
        conn.close()
    server.log.info(f"Worker {worker.pid} has finished serving") 