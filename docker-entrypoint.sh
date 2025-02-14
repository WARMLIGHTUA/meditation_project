#!/bin/bash
set -e

echo "Starting application setup..."

# Виведення всіх змінних середовища
echo "All environment variables:"
env | sort

echo "Current working directory: $(pwd)"
echo "Files in current directory:"
ls -la

# Виконання міграцій
echo "Running migrations..."
python manage.py migrate --noinput

echo "Starting Gunicorn..."
exec gunicorn meditation_app.wsgi:application \
    --bind "0.0.0.0:${PORT:-8080}" \
    --workers 2 \
    --threads 2 \
    --log-level debug \
    --access-logfile - \
    --error-logfile - \
    --capture-output \
    --enable-stdio-inheritance \
    --timeout 120 