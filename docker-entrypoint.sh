#!/bin/bash

# Функція для правильного завершення процесів
cleanup() {
    echo "Отримано сигнал завершення..."
    echo "Закриваю з'єднання з базою даних..."
    
    # Використовуємо Python замість psql для закриття з'єднань
    python << END
import os
import django
from django.db import connections
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'meditation_app.settings')
django.setup()
for conn in connections.all():
    conn.close()
END
    
    echo "Очікування завершення активних з'єднань (10 секунд)..."
    sleep 10
    echo "Перевірка активних процесів..."
    ps aux | grep gunicorn
    echo "Завершую Gunicorn (PID: $child)..."
    kill -TERM "$child" 2>/dev/null
    echo "Очікування завершення Gunicorn..."
    wait "$child"
    echo "Додаток успішно завершено"
    exit 0
}

# Встановлення обробника сигналів
trap cleanup SIGTERM SIGINT SIGQUIT SIGHUP

echo "Starting application setup..."

# Виведення всіх змінних середовища
echo "All environment variables:"
env | sort

# Виведення діагностичної інформації
echo "Environment information:"
echo "PORT: $PORT"
echo "Current directory: $(pwd)"
echo "Python version: $(python --version)"
echo "Pip version: $(pip --version)"
echo "Django settings module: ${DJANGO_SETTINGS_MODULE:-Not set}"
echo "Environment name: ${ENVIRONMENT_NAME:-Not set}"
echo "Django debug mode: ${DJANGO_DEBUG:-Not set}"
echo "Gunicorn log level: ${GUNICORN_LOG_LEVEL:-info}"
echo "Gunicorn config file exists: $(test -f ./gunicorn.conf.py && echo 'Yes' || echo 'No')"
echo "Gunicorn config contents:"
cat ./gunicorn.conf.py

# Очікування DATABASE_URL
max_attempts=5
attempt=1
while [ -z "$DATABASE_URL" ] && [ $attempt -le $max_attempts ]; do
    echo "Attempt $attempt: Waiting for DATABASE_URL to be set..."
    env | grep -i "database\|db\|pg"
    sleep 5
    attempt=$((attempt + 1))
done

if [ -z "$DATABASE_URL" ]; then
    echo "ERROR: DATABASE_URL is not set after $max_attempts attempts!"
    echo "Available database-related variables:"
    env | grep -i "database\|db\|pg"
    exit 1
fi

echo "Database URL type: $(echo $DATABASE_URL | cut -d: -f1)"

# Перевірка доступності бази даних
echo "Checking database connection..."
python << END
import sys
import time
import os
from urllib.parse import urlparse
import psycopg2

db_url = os.getenv('DATABASE_URL')
url = urlparse(db_url)

for i in range(5):
    try:
        conn = psycopg2.connect(
            dbname=url.path[1:],
            user=url.username,
            password=url.password,
            host=url.hostname,
            port=url.port
        )
        conn.close()
        print(f"Database connection successful to {url.hostname}:{url.port}")
        sys.exit(0)
    except psycopg2.OperationalError as e:
        print(f"Attempt {i+1}: Database connection failed - {str(e)}")
        if i < 4:
            time.sleep(5)
sys.exit(1)
END

if [ $? -ne 0 ]; then
    echo "Failed to connect to database after 5 attempts"
    echo "Check if the database service is properly configured in Railway"
    exit 1
fi

# Виконання міграцій
echo "Running migrations..."
python manage.py migrate --noinput

# Збір статичних файлів
echo "Collecting static files..."
python manage.py collectstatic --noinput

# Запуск Gunicorn з розширеним логуванням
echo "Starting Gunicorn with config from ./gunicorn.conf.py..."
echo "Gunicorn command: gunicorn meditation_app.wsgi:application -c ./gunicorn.conf.py"
gunicorn meditation_app.wsgi:application -c ./gunicorn.conf.py --log-level=debug --access-logfile=- --error-logfile=- &
child=$!

# Очікування завершення процесу
wait "$child" 