import multiprocessing
import os

# Основні налаштування
bind = f"0.0.0.0:{os.getenv('PORT', '8080')}"
workers = 3
worker_class = 'gthread'
threads = 2
timeout = 120

# Налаштування логування
accesslog = '-'
errorlog = '-'
loglevel = 'info'
capture_output = True

# Налаштування для Railway
forwarded_allow_ips = '*'
secure_scheme_headers = {
    'X-FORWARDED-PROTO': 'https'
}

# Налаштування безпеки
proxy_allow_ips = '*'

# Додаткові налаштування
worker_tmp_dir = '/dev/shm'
preload_app = False

# Розширені налаштування логування
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s"'
enable_stdio_inheritance = True
logger_class = 'gunicorn.glogging.Logger'

# Налаштування для файлової системи
tmp_upload_dir = None

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
max_requests = 1000
max_requests_jitter = 50
graceful_timeout = 30
keepalive = 5
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

def worker_exit(server, worker):
    server.log.info(f"Worker {worker.pid} has finished serving")

def post_fork(server, worker):
    server.log.info(f"Worker {worker.pid} has been forked") 