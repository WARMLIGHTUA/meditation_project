#!/bin/bash

# Функція для правильного завершення процесів
cleanup() {
    echo "Отримано сигнал завершення..."
    echo "Закриваю з'єднання з базою даних..."
    python manage.py dbshell <<< "SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname = current_database() AND pid <> pg_backend_pid();"
    echo "Завершую Gunicorn..."
    kill -TERM "$child" 2>/dev/null
    wait "$child"
    echo "Додаток успішно завершено"
    exit 0
}

# Встановлення обробника сигналів
trap cleanup SIGTERM SIGINT SIGQUIT

echo "Starting application setup..."

# Виведення діагностичної інформації
echo "Environment information:"
echo "PORT: $PORT"
echo "Current directory: $(pwd)"
echo "Python version: $(python --version)"
echo "Pip version: $(pip --version)"
echo "Database URL: ${DATABASE_URL:-Not set}"
echo "Django settings module: ${DJANGO_SETTINGS_MODULE:-Not set}"

# Перевірка доступності бази даних
echo "Checking database connection..."
python << END
import sys
import time
import psycopg2
from urllib.parse import urlparse
url = urlparse("${DATABASE_URL}")
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
        print("Database connection successful")
        sys.exit(0)
    except psycopg2.OperationalError as e:
        print(f"Attempt {i+1}: Database connection failed - {str(e)}")
        if i < 4:
            time.sleep(5)
sys.exit(1)
END

if [ $? -ne 0 ]; then
    echo "Failed to connect to database after 5 attempts"
    exit 1
fi

# Виконання міграцій
echo "Running migrations..."
python manage.py migrate --noinput

# Запуск Gunicorn
echo "Starting Gunicorn..."
exec gunicorn meditation_app.wsgi:application -c ./gunicorn.conf.py

child=$!
wait "$child" 