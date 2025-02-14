import os

# Базові налаштування
bind = f"0.0.0.0:{os.getenv('PORT', '8080')}"
workers = 2
worker_class = 'gthread'
threads = 2
worker_tmp_dir = '/dev/shm'
chdir = '/app'

# Таймаути
timeout = 120
graceful_timeout = 30
keepalive = 2

# Логування
accesslog = '-'
errorlog = '-'
loglevel = 'debug'
capture_output = True
enable_stdio_inheritance = True
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s"'

# Проксі та безпека
forwarded_allow_ips = '*'
proxy_allow_ips = '*'
secure_scheme_headers = {
    'X-FORWARDED-PROTOCOL': 'ssl',
    'X-FORWARDED-PROTO': 'https',
    'X-FORWARDED-SSL': 'on'
}

# Процес
wsgi_app = 'meditation_app.wsgi:application'
reload = False

# Системні налаштування
user = 0
group = 0
umask = 0
initgroups = False

def on_starting(server):
    server.log.info("Starting Meditation App")

def worker_exit(server, worker):
    from django.db import connections
    for conn in connections.all():
        conn.close()

# Налаштування для статистики
statsd_host = os.getenv('STATSD_HOST', None)
statsd_prefix = 'meditation_app'

# SSL налаштування
keyfile = None
certfile = None
ssl_version = 2
cert_reqs = 0
ca_certs = None
suppress_ragged_eofs = True
do_handshake_on_connect = False
ciphers = None

# Налаштування користувача
default_proc_name = 'meditation_app.wsgi:application' 