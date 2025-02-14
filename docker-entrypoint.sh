#!/bin/bash
set -e

# Виведення інформації про змінні середовища
echo "Environment variables:"
echo "PORT: $PORT"
echo "DJANGO_SETTINGS_MODULE: $DJANGO_SETTINGS_MODULE"

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

# Запуск Gunicorn з файлом конфігурації
echo "Starting Gunicorn with config file..."
exec gunicorn meditation_app.wsgi:application -c gunicorn.conf.py 