import os

# Основні налаштування
bind = f"0.0.0.0:{os.getenv('PORT', '8080')}"
workers = 1  # Зменшуємо кількість воркерів
worker_class = 'sync'  # Використовуємо простіший воркер
timeout = 30

# Налаштування логування
accesslog = '-'
errorlog = '-'
loglevel = 'info'

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

def worker_exit(server, worker):
    try:
        from django.db import connections
        for conn in connections.all():
            conn.close()
    except:
        pass 