#!/bin/bash

# Функція для правильного завершення процесів
cleanup() {
    echo "Отримано сигнал завершення..."
    
    # Створюємо тимчасовий Python-скрипт для закриття з'єднань
    cat > cleanup.py << 'EOF'
import os
import sys
import django
from django.db import connections

try:
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'meditation_app.settings')
    django.setup()
    
    # Закриваємо всі з'єднання з базою даних
    for conn in connections.all():
        try:
            conn.close()
            print(f"Закрито з'єднання: {conn}")
        except Exception as e:
            print(f"Помилка при закритті з'єднання: {e}")
    
    print("Всі з'єднання з базою даних успішно закриті")
    sys.exit(0)
except Exception as e:
    print(f"Помилка при закритті з'єднань: {e}")
    sys.exit(1)
EOF

    # Виконуємо скрипт закриття з'єднань
    echo "Закриваю з'єднання з базою даних..."
    python cleanup.py
    
    echo "Очікування завершення активних з'єднань (5 секунд)..."
    sleep 5
    
    # Завершуємо процес Gunicorn
    if [ -n "$child" ]; then
        echo "Завершую Gunicorn (PID: $child)..."
        kill -TERM "$child" 2>/dev/null
        
        # Очікуємо завершення процесу
        wait "$child" 2>/dev/null
        
        # Перевіряємо, чи процес все ще існує
        if kill -0 "$child" 2>/dev/null; then
            echo "Примусово завершую процес..."
            kill -9 "$child" 2>/dev/null
        fi
    fi
    
    # Видаляємо тимчасовий файл
    rm -f cleanup.py
    
    echo "Додаток успішно завершено"
    exit 0
}

# Встановлення обробника сигналів
trap cleanup SIGTERM SIGINT SIGQUIT SIGHUP

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
echo "Gunicorn log level: ${GUNICORN_LOG_LEVEL:-info}"

# Перевірка доступності бази даних
echo "Checking database connection..."
python << END
import sys
import time
import os
from urllib.parse import urlparse
import psycopg2

db_url = os.getenv('DATABASE_URL')
if not db_url:
    print("ERROR: DATABASE_URL is not set!")
    sys.exit(1)

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
    exit 1
fi

# Виконання міграцій
echo "Running migrations..."
python manage.py migrate --noinput

# Створення суперкористувача
echo "Creating superuser..."
python manage.py createsuperuser --noinput || echo "Superuser already exists or creation failed."

# Збір статичних файлів
echo "Collecting static files..."
python manage.py collectstatic --noinput

# Запуск Gunicorn
echo "Starting Gunicorn..."
gunicorn meditation_app.wsgi:application \
    --bind 0.0.0.0:${PORT:-8080} \
    --workers ${GUNICORN_WORKERS:-2} \
    --threads ${GUNICORN_THREADS:-4} \
    --timeout ${GUNICORN_TIMEOUT:-120} \
    --max-requests ${GUNICORN_MAX_REQUESTS:-1000} \
    --max-requests-jitter ${GUNICORN_MAX_REQUESTS_JITTER:-50} \
    --log-level ${GUNICORN_LOG_LEVEL:-debug} \
    --access-logfile - \
    --error-logfile - &

child=$!

# Очікування завершення процесу
wait "$child"