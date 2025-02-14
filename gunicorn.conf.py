import multiprocessing
import os
import signal

# Основні налаштування
bind = f"0.0.0.0:{os.getenv('PORT', '8080')}"
workers = 2
worker_class = 'gthread'
threads = 2
timeout = 30
keepalive = 2

# Налаштування логування
accesslog = '-'
errorlog = '-'
loglevel = 'info'
capture_output = True

# Налаштування для проксі
forwarded_allow_ips = '*'
proxy_allow_ips = '*'

# Налаштування процесу
proc_name = 'meditation_app'
wsgi_app = 'meditation_app.wsgi:application'

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
def on_starting(server):
    server.log.info("Starting Meditation App")
    # Встановлюємо обробник сигналу SIGTERM
    signal.signal(signal.SIGTERM, lambda signo, frame: handle_term_signal(server))

def handle_term_signal(server):
    server.log.info("Received SIGTERM. Performing graceful shutdown...")
    # Закриваємо з'єднання з базою даних
    try:
        from django.db import connections
        for conn in connections.all():
            conn.close()
    except:
        pass

def post_fork(server, worker):
    server.log.info(f"Worker spawned (pid: {worker.pid})")

def worker_exit(server, worker):
    try:
        from django.db import connections
        for conn in connections.all():
            conn.close()
    except:
        pass
    server.log.info(f"Worker exited (pid: {worker.pid})")

def worker_abort(worker):
    try:
        from django.db import connections
        for conn in connections.all():
            conn.close()
    except:
        pass
    worker.log.info(f"Worker aborted (pid: {worker.pid})") 