FROM python:3.13-slim

# Встановлення залежностей системи
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Встановлення робочої директорії
WORKDIR /app

# Копіювання файлів проекту
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Збирання статичних файлів
RUN python manage.py collectstatic --noinput

# Відкриття порту
EXPOSE 8000

# Запуск додатку
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "meditation_app.wsgi"] 