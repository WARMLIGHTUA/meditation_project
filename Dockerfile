FROM python:3.11-slim

# Встановлення залежностей системи
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
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
    PYTHONDONTWRITEBYTECODE=1

# Створення скрипту для запуску
COPY ./docker-entrypoint.sh /docker-entrypoint.sh
RUN chmod +x /docker-entrypoint.sh

# Збирання статичних файлів
RUN python manage.py collectstatic --noinput

# Відкриття порту
EXPOSE 8000

# Запуск додатку через entrypoint скрипт
ENTRYPOINT ["/docker-entrypoint.sh"] 