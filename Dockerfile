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

# Копіювання та встановлення залежностей
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копіювання файлів проекту
COPY . .

# Змінні середовища
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    DJANGO_SETTINGS_MODULE=meditation_app.settings \
    PORT=8080 \
    WEB_CONCURRENCY=2

# Створення та налаштування entrypoint
COPY ./docker-entrypoint.sh /docker-entrypoint.sh
RUN chmod +x /docker-entrypoint.sh

# Збирання статичних файлів
RUN python manage.py collectstatic --noinput

# Відкриття порту
EXPOSE 8080

# Передача змінних середовища з Railway
ARG DATABASE_URL
ENV DATABASE_URL=$DATABASE_URL

ARG DJANGO_SECRET_KEY
ENV DJANGO_SECRET_KEY=$DJANGO_SECRET_KEY

ARG DJANGO_DEBUG
ENV DJANGO_DEBUG=$DJANGO_DEBUG

ARG ENVIRONMENT_NAME
ENV ENVIRONMENT_NAME=$ENVIRONMENT_NAME

ARG GUNICORN_LOG_LEVEL
ENV GUNICORN_LOG_LEVEL=$GUNICORN_LOG_LEVEL

# Запуск додатку
ENTRYPOINT ["/docker-entrypoint.sh"] 