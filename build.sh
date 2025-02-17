#!/bin/bash

# Завантаження змінних з .env файлу, якщо він існує
if [ -f .env ]; then
    echo "Завантаження змінних з .env файлу..."
    source .env
fi

# Функція для встановлення значення за замовчуванням
get_env_value() {
    local var_name=$1
    local default_value=$2
    local value=${!var_name:-$default_value}
    echo $value
}

# Встановлення значень за замовчуванням
DJANGO_SETTINGS_MODULE=$(get_env_value "DJANGO_SETTINGS_MODULE" "meditation_app.settings")
DJANGO_DEBUG=$(get_env_value "DJANGO_DEBUG" "False")
DJANGO_LOG_LEVEL=$(get_env_value "DJANGO_LOG_LEVEL" "INFO")
DJANGO_ADMIN_ENABLED=$(get_env_value "DJANGO_ADMIN_ENABLED" "True")
PORT=$(get_env_value "PORT" "8080")
PYTHONUNBUFFERED=$(get_env_value "PYTHONUNBUFFERED" "1")
GUNICORN_WORKERS=$(get_env_value "GUNICORN_WORKERS" "2")
GUNICORN_THREADS=$(get_env_value "GUNICORN_THREADS" "4")
GUNICORN_TIMEOUT=$(get_env_value "GUNICORN_TIMEOUT" "120")
GUNICORN_MAX_REQUESTS=$(get_env_value "GUNICORN_MAX_REQUESTS" "1000")
GUNICORN_MAX_REQUESTS_JITTER=$(get_env_value "GUNICORN_MAX_REQUESTS_JITTER" "50")
GUNICORN_LOG_LEVEL=$(get_env_value "GUNICORN_LOG_LEVEL" "info")
ENVIRONMENT_NAME=$(get_env_value "ENVIRONMENT_NAME" "production")
APP_STATIC_URL=$(get_env_value "APP_STATIC_URL" "static")
WHITENOISE_MANIFEST_STRICT=$(get_env_value "WHITENOISE_MANIFEST_STRICT" "False")

# Перевірка наявності обов'язкових змінних
required_vars=(
    "DJANGO_SECRET_KEY"
    "DATABASE_URL"
    "ALLOWED_HOSTS"
    "CSRF_TRUSTED_ORIGINS"
    "AWS_ACCESS_KEY_ID"
    "AWS_SECRET_ACCESS_KEY"
    "AWS_STORAGE_BUCKET_NAME"
    "AWS_S3_REGION_NAME"
    "DJANGO_SUPERUSER_USERNAME"
    "DJANGO_SUPERUSER_EMAIL"
    "DJANGO_SUPERUSER_PASSWORD"
)

for var in "${required_vars[@]}"; do
    if [ -z "${!var}" ]; then
        echo "Помилка: Змінна $var не встановлена"
        exit 1
    fi
done

echo "Початок збірки Docker образу..."

# Збірка Docker образу з усіма build arguments
docker build \
    --build-arg DJANGO_SECRET_KEY="$DJANGO_SECRET_KEY" \
    --build-arg DJANGO_DEBUG="$DJANGO_DEBUG" \
    --build-arg DJANGO_SETTINGS_MODULE="$DJANGO_SETTINGS_MODULE" \
    --build-arg DJANGO_LOG_LEVEL="$DJANGO_LOG_LEVEL" \
    --build-arg DJANGO_ADMIN_ENABLED="$DJANGO_ADMIN_ENABLED" \
    --build-arg ALLOWED_HOSTS="$ALLOWED_HOSTS" \
    --build-arg CSRF_TRUSTED_ORIGINS="$CSRF_TRUSTED_ORIGINS" \
    --build-arg DATABASE_URL="$DATABASE_URL" \
    --build-arg DB_LOG_LEVEL="$DB_LOG_LEVEL" \
    --build-arg APP_STATIC_URL="$APP_STATIC_URL" \
    --build-arg WHITENOISE_MANIFEST_STRICT="$WHITENOISE_MANIFEST_STRICT" \
    --build-arg AWS_ACCESS_KEY_ID="$AWS_ACCESS_KEY_ID" \
    --build-arg AWS_SECRET_ACCESS_KEY="$AWS_SECRET_ACCESS_KEY" \
    --build-arg AWS_STORAGE_BUCKET_NAME="$AWS_STORAGE_BUCKET_NAME" \
    --build-arg AWS_S3_REGION_NAME="$AWS_S3_REGION_NAME" \
    --build-arg GUNICORN_WORKERS="$GUNICORN_WORKERS" \
    --build-arg GUNICORN_THREADS="$GUNICORN_THREADS" \
    --build-arg GUNICORN_TIMEOUT="$GUNICORN_TIMEOUT" \
    --build-arg GUNICORN_MAX_REQUESTS="$GUNICORN_MAX_REQUESTS" \
    --build-arg GUNICORN_MAX_REQUESTS_JITTER="$GUNICORN_MAX_REQUESTS_JITTER" \
    --build-arg GUNICORN_LOG_LEVEL="$GUNICORN_LOG_LEVEL" \
    --build-arg ENVIRONMENT_NAME="$ENVIRONMENT_NAME" \
    --build-arg PORT="$PORT" \
    --build-arg PYTHONUNBUFFERED="$PYTHONUNBUFFERED" \
    --build-arg DJANGO_SUPERUSER_USERNAME="$DJANGO_SUPERUSER_USERNAME" \
    --build-arg DJANGO_SUPERUSER_EMAIL="$DJANGO_SUPERUSER_EMAIL" \
    --build-arg DJANGO_SUPERUSER_PASSWORD="$DJANGO_SUPERUSER_PASSWORD" \
    -t meditation-app:latest \
    .

build_status=$?

if [ $build_status -eq 0 ]; then
    echo "Збірка Docker образу успішно завершена!"
    echo "Тег образу: meditation-app:latest"
else
    echo "Помилка при збірці Docker образу!"
    exit $build_status
fi 