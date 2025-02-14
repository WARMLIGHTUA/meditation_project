#!/bin/bash
set -e

# Встановлення порту за замовчуванням, якщо не вказано
if [ -z "$PORT" ]; then
    export PORT=8000
fi
echo "Environment PORT: $PORT"

# Виконання міграцій
echo "Running migrations..."
python manage.py migrate --noinput

# Перевірка доступності порту
echo "Checking port $PORT availability..."
if ! /bin/nc -z localhost $PORT; then
    echo "Port $PORT is available"
else
    echo "Warning: Port $PORT might be in use"
fi

# Запуск Gunicorn
echo "Starting Gunicorn on port $PORT..."
exec gunicorn meditation_app.wsgi:application \
    --bind "0.0.0.0:$PORT" \
    --workers 2 \
    --threads 2 \
    --log-level debug \
    --access-logfile - \
    --error-logfile - \
    --capture-output \
    --enable-stdio-inheritance \
    --timeout 120 