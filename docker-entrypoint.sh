#!/bin/bash

# Функція для правильного завершення процесів
cleanup() {
    echo "Отримано сигнал завершення..."
    kill -TERM "$child" 2>/dev/null
    wait "$child"
    exit 0
}

# Встановлення обробника сигналів
trap cleanup SIGTERM SIGINT

echo "Starting application setup..."

# Виведення діагностичної інформації
echo "Environment information:"
echo "PORT: $PORT"
echo "Current directory: $(pwd)"
echo "Python version: $(python --version)"
echo "Pip version: $(pip --version)"

# Виконання міграцій
echo "Running migrations..."
python manage.py migrate --noinput

# Запуск Gunicorn
echo "Starting Gunicorn..."
gunicorn meditation_app.wsgi:application \
    --bind "0.0.0.0:${PORT:-8080}" \
    --workers 2 \
    --threads 2 \
    --worker-class gthread \
    --worker-tmp-dir /dev/shm \
    --log-level debug \
    --access-logfile - \
    --error-logfile - \
    --capture-output \
    --enable-stdio-inheritance \
    --timeout 120 \
    --forwarded-allow-ips="*" \
    --proxy-protocol \
    --proxy-allow-ips="*" &

child=$!
wait "$child" 