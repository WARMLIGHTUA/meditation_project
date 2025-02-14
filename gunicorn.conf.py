import os
import multiprocessing

# Базові налаштування
bind = f"0.0.0.0:{os.getenv('PORT', '8080')}"
workers = 2
worker_class = 'gthread'
threads = 2
timeout = 120
graceful_timeout = 30
keepalive = 2

# Логування
accesslog = '-'
errorlog = '-'
loglevel = os.getenv('GUNICORN_LOG_LEVEL', 'info')
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(L)s'

# Проксі та безпека
forwarded_allow_ips = '*'
proxy_allow_ips = '*'
proxy_protocol = True

# Додатково
wsgi_app = 'meditation_app.wsgi:application'
reload = False
preload_app = True

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

# Налаштування для статистики
statsd_host = os.getenv('STATSD_HOST', None)
statsd_prefix = 'meditation_app'

# Обробники подій
def on_starting(server):
    server.log.info("Starting Meditation App")

def worker_exit(server, worker):
    from django.db import connections
    for conn in connections.all():
        conn.close() 