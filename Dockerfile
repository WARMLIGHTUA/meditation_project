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
    PYTHONDONTWRITEBYTECODE=1 \
    PORT=8000

# Збирання статичних файлів
RUN python manage.py collectstatic --noinput

# Відкриття порту
EXPOSE 8000

# Запуск додатку
CMD gunicorn meditation_app.wsgi:application --bind 0.0.0.0:$PORT --workers 2 --threads 2 --log-level debug --access-logfile - --error-logfile - 