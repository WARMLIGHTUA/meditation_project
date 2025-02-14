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
graceful_timeout = 30
keepalive = 2
limit_request_line = 4094
limit_request_fields = 100
limit_request_field_size = 8190

# Процес
wsgi_app = 'meditation_app.wsgi:application'
reload = False
reload_engine = 'auto'
reload_extra_files = []
preload_app = True
daemon = False
raw_env = []
pidfile = None

# Системні налаштування
sendfile = None
reuse_port = False
spew = False

def worker_exit(server, worker):
    from django.db import connections
    for conn in connections.all():
        conn.close() 