# Meditation App

Meditation App - це веб-додаток для медитації, створений на Django. Додаток підтримує три мови (українська, англійська, французька) та надає можливість прослуховування медитаційних треків, участі в групах, відвідування воркшопів та подій.

## Функціональність

- 🎵 Медитаційні треки з аудіо
- 👥 Групи медитації
- 📚 Навчальні курси
- 🎯 Воркшопи
- 📅 Події (онлайн та офлайн)
- ❤️ Збереження улюблених медитацій
- 🌍 Багатомовність (UK, EN, FR)
- 🌓 Темна/світла тема

## Технології

- Python 3.8+
- Django 5.0
- Bootstrap 5
- JavaScript
- HTML5/CSS3
- SQLite (розробка) / PostgreSQL (продакшн)

## Встановлення

1. Клонуйте репозиторій:
```bash
git clone https://github.com/your-username/meditation-app.git
cd meditation-app
```

2. Створіть віртуальне середовище та активуйте його:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

3. Встановіть залежності:
```bash
pip install -r requirements.txt
```

4. Виконайте міграції:
```bash
python manage.py migrate
```

5. Створіть суперкористувача:
```bash
python manage.py createsuperuser
```

6. Запустіть сервер розробки:
```bash
python manage.py runserver
```

7. Скомпілюйте переклади:
```bash
python manage.py compilemessages
```

## Налаштування

1. Створіть файл `.env` в корені проекту та додайте необхідні змінні середовища:
```
DJANGO_SECRET_KEY=your-secret-key
DJANGO_DEBUG=True
DJANGO_ALLOWED_HOSTS=localhost 127.0.0.1
```

## Розробка

- Додавання нових перекладів:
```bash
python manage.py makemessages -l uk -l en -l fr
```

- Збірка статичних файлів:
```bash
python manage.py collectstatic
```

## Ліцензія та використання

Всі права на цей програмний продукт захищені. Використання та розповсюдження дозволяється лише з письмового дозволу власника авторських прав. Для отримання дозволу на використання звертайтесь: meditaciya4@gmail.com

Детальні умови використання дивіться у файлі [LICENSE](LICENSE). 