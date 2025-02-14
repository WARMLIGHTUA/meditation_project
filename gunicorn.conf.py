import multiprocessing
import os

# Основні налаштування
wsgi_app = 'meditation_app.wsgi:application'
bind = f"0.0.0.0:{os.getenv('PORT', '8080')}"
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = 'gthread'
threads = 4
timeout = 120
keepalive = 5

# Розширені налаштування логування
accesslog = '-'
errorlog = '-'
loglevel = os.getenv('GUNICORN_LOG_LEVEL', 'info')
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s"'
capture_output = True
enable_stdio_inheritance = True
logger_class = 'gunicorn.glogging.Logger'

# Налаштування для Railway
forwarded_allow_ips = '*'
secure_scheme_headers = {
    'X-FORWARDED-PROTOCOL': 'ssl',
    'X-FORWARDED-PROTO': 'https',
    'X-FORWARDED-SSL': 'on'
}

# Налаштування безпеки
limit_request_line = 4094
limit_request_fields = 100
limit_request_field_size = 8190
proxy_allow_ips = '127.0.0.1,*'
proxy_protocol = False

# Налаштування для файлової системи
worker_tmp_dir = '/dev/shm'
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
preload_app = True
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