#!/bin/bash

# Встановлення порту за замовчуванням, якщо не вказано
PORT="${PORT:-8000}"
echo "Using port: $PORT"

# Виконання міграцій
echo "Running migrations..."
python manage.py migrate --noinput

# Запуск Gunicorn
echo "Starting Gunicorn..."
exec gunicorn meditation_app.wsgi:application \
    --bind "0.0.0.0:${PORT}" \
    --workers 2 \
    --threads 2 \
    --log-level debug \
    --access-logfile - \
    --error-logfile - \
    --capture-output \
    --enable-stdio-inheritance 