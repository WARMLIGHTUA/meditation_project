# Базовий образ
FROM python:3.11-slim

# Встановлення залежностей системи
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    procps \
    && rm -rf /var/lib/apt/lists/*

# Встановлення робочої директорії
WORKDIR /app

# Оновлення pip та встановлення базових інструментів
RUN pip install --no-cache-dir --upgrade pip setuptools wheel

# Створення необхідних директорій
RUN mkdir -p /app/static /app/staticfiles /app/mediafiles

# Копіювання та встановлення залежностей
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копіювання файлів проекту
COPY . .

# Встановлення змінних середовища
ENV DJANGO_SECRET_KEY=${DJANGO_SECRET_KEY:-'django-insecure-default-key-change-in-production'} \
    DJANGO_DEBUG=${DJANGO_DEBUG:-'False'} \
    DJANGO_SETTINGS_MODULE=${DJANGO_SETTINGS_MODULE:-'meditation_app.settings'} \
    DJANGO_LOG_LEVEL=${DJANGO_LOG_LEVEL:-'INFO'} \
    DJANGO_ADMIN_ENABLED=${DJANGO_ADMIN_ENABLED:-'True'} \
    ALLOWED_HOSTS=${ALLOWED_HOSTS:-'localhost,127.0.0.1'} \
    CSRF_TRUSTED_ORIGINS=${CSRF_TRUSTED_ORIGINS:-'http://localhost,http://127.0.0.1'} \
    DB_LOG_LEVEL=${DB_LOG_LEVEL:-'INFO'}

# База даних
ENV PGDATABASE=${PGDATABASE:-'railway'} \
    PGUSER=${PGUSER:-'postgres'} \
    PGPASSWORD=${PGPASSWORD:-'postgres'} \
    PGHOST=${PGHOST:-'db'} \
    PGPORT=${PGPORT:-'5432'} \
    DATABASE_URL=${DATABASE_URL:-'postgresql://postgres:postgres@db:5432/railway?sslmode=require'}

# Статичні файли
ENV APP_STATIC_URL=${APP_STATIC_URL:-'static/'} \
    WHITENOISE_MANIFEST_STRICT=${WHITENOISE_MANIFEST_STRICT:-'False'}

# AWS налаштування
ENV AWS_ACCESS_KEY_ID=${AWS_ACCESS_KEY_ID:-''} \
    AWS_SECRET_ACCESS_KEY=${AWS_SECRET_ACCESS_KEY:-''} \
    AWS_STORAGE_BUCKET_NAME=${AWS_STORAGE_BUCKET_NAME:-'meditation-app-storage'} \
    AWS_S3_REGION_NAME=${AWS_S3_REGION_NAME:-'eu-north-1'}

# Gunicorn налаштування
ENV GUNICORN_WORKERS=${GUNICORN_WORKERS:-'2'} \
    GUNICORN_THREADS=${GUNICORN_THREADS:-'4'} \
    GUNICORN_TIMEOUT=${GUNICORN_TIMEOUT:-'120'} \
    GUNICORN_MAX_REQUESTS=${GUNICORN_MAX_REQUESTS:-'1000'} \
    GUNICORN_MAX_REQUESTS_JITTER=${GUNICORN_MAX_REQUESTS_JITTER:-'50'} \
    GUNICORN_LOG_LEVEL=${GUNICORN_LOG_LEVEL:-'info'}

# Середовище
ENV ENVIRONMENT_NAME=${ENVIRONMENT_NAME:-'development'} \
    PORT=${PORT:-'8080'} \
    PYTHONUNBUFFERED=${PYTHONUNBUFFERED:-'1'}

# Суперкористувач Django
ENV DJANGO_SUPERUSER_USERNAME=${DJANGO_SUPERUSER_USERNAME:-'admin'} \
    DJANGO_SUPERUSER_EMAIL=${DJANGO_SUPERUSER_EMAIL:-'admin@example.com'} \
    DJANGO_SUPERUSER_PASSWORD=${DJANGO_SUPERUSER_PASSWORD:-'admin'}

# Створення та налаштування entrypoint
COPY ./docker-entrypoint.sh /docker-entrypoint.sh
RUN chmod +x /docker-entrypoint.sh

# Відкриття порту
EXPOSE ${PORT:-8080}

# Запуск додатку
ENTRYPOINT ["/docker-entrypoint.sh"]