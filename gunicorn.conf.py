import os

# Базові налаштування
bind = f"0.0.0.0:{os.getenv('PORT', '8080')}"
backlog = 2048
workers = 2
worker_class = 'gthread'
threads = 2
worker_connections = 1000
worker_tmp_dir = '/dev/shm'
chdir = '/app'

# Таймаути та ліміти
timeout = 120
graceful_timeout = 60
keepalive = 5
limit_request_line = 4094
limit_request_fields = 100
limit_request_field_size = 8190

# Налаштування для кращої обробки сигналів
worker_abort_on_error = False
worker_shutdown_timeout = 60

# Функції для обробки сигналів
def worker_int(worker):
    worker.log.info(f"Воркер {worker.pid} отримав сигнал INT/QUIT")
    return True

def worker_term(worker):
    worker.log.info(f"Воркер {worker.pid} отримав сигнал TERM")
    return True

def worker_abort(worker):
    worker.log.warning(f"Воркер {worker.pid} отримав сигнал ABORT")

def worker_exit(server, worker):
    from django.db import connections
    server.log.info(f"Воркер {worker.pid} завершує роботу")
    for conn in connections.all():
        try:
            conn.close()
            server.log.info(f"З'єднання {conn} закрито")
        except Exception as e:
            server.log.error(f"Помилка при закритті з'єднання {conn}: {e}")

def on_starting(server):
    server.log.info(f"Запуск Gunicorn сервера в середовищі {os.getenv('RAILWAY_ENVIRONMENT', 'development')}")
    server.log.info(f"Версія Python: {os.getenv('PYTHON_VERSION', 'unknown')}")
    server.log.info(f"Домен: {os.getenv('RAILWAY_PUBLIC_DOMAIN', 'unknown')}")

# Системні налаштування
umask = 0
initgroups = False
tmp_upload_dir = None
strip_header_spaces = False

# Проксі та безпека
secure_scheme_headers = {
    'X-FORWARDED-PROTOCOL': 'ssl',
    'X-FORWARDED-PROTO': 'https',
    'X-FORWARDED-SSL': 'on'
}
forwarded_allow_ips = '*'
proxy_allow_ips = '*'
proxy_protocol = False

# Логування
accesslog = '-'
errorlog = '-'
loglevel = 'debug'
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s"'
logger_class = 'gunicorn.glogging.Logger'
capture_output = True
enable_stdio_inheritance = True
disable_redirect_access_to_syslog = False
syslog = False
syslog_addr = 'udp://localhost:514'
syslog_prefix = None
syslog_facility = 'user'
logconfig = None
logconfig_dict = {}

# Процес
wsgi_app = 'meditation_app.wsgi:application'
proc_name = None
default_proc_name = 'meditation_app.wsgi:application'
pythonpath = None
paste = None
reload = False
reload_engine = 'auto'
reload_extra_files = []
preload_app = True
daemon = False
raw_env = []
pidfile = None

# SSL налаштування
keyfile = None
certfile = None
ssl_version = 2
cert_reqs = 0
ca_certs = None
suppress_ragged_eofs = True
do_handshake_on_connect = False
ciphers = None

# Статистика
statsd_host = None
dogstatsd_tags = ''
statsd_prefix = ''

# Системні налаштування
sendfile = None
reuse_port = False
spew = False
raw_paste_global_conf = [] 