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
echo "Django settings module: ${DJANGO_SETTINGS_MODULE:-Not set}"
echo "Environment name: ${ENVIRONMENT_NAME:-Not set}"
echo "Django debug mode: ${DJANGO_DEBUG:-Not set}"
echo "Gunicorn log level: ${GUNICORN_LOG_LEVEL:-Not set}"

# Перевірка наявності змінних середовища PostgreSQL
if [ -z "$PGHOST" ] || [ -z "$PGPORT" ] || [ -z "$PGUSER" ] || [ -z "$PGPASSWORD" ] || [ -z "$PGDATABASE" ]; then
    echo "ERROR: Required PostgreSQL environment variables are not set!"
    echo "PGHOST: ${PGHOST:-Not set}"
    echo "PGPORT: ${PGPORT:-Not set}"
    echo "PGUSER: ${PGUSER:-Not set}"
    echo "PGDATABASE: ${PGDATABASE:-Not set}"
    echo "DATABASE_URL type: $(echo $DATABASE_URL | cut -d: -f1)"
    exit 1
fi

# Перевірка доступності бази даних
echo "Checking database connection..."
python << END
import sys
import time
import os
import psycopg2

for i in range(5):
    try:
        conn = psycopg2.connect(
            dbname=os.getenv('PGDATABASE'),
            user=os.getenv('PGUSER'),
            password=os.getenv('PGPASSWORD'),
            host=os.getenv('PGHOST'),
            port=os.getenv('PGPORT')
        )
        conn.close()
        print(f"Database connection successful to {os.getenv('PGHOST')}:{os.getenv('PGPORT')}")
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

# Запуск Gunicorn
echo "Starting Gunicorn..."
echo "Using log level: ${GUNICORN_LOG_LEVEL:-info}"
exec gunicorn meditation_app.wsgi:application -c ./gunicorn.conf.py

child=$!
wait "$child" 