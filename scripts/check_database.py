import os
import sys
import django
from django.core.management import execute_from_command_line
from django.db import connection
from django.db.models import Count
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.validators import URLValidator

# Налаштування Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'meditation_app.settings')
django.setup()

# Імпортуємо моделі після налаштування Django
from meditation.models import (
    MeditationTrack, TopContent, Course, Workshop,
    Group, Event, UserProfile, FavoriteMeditation, Comment
)

def check_database_connection():
    """Перевірка з'єднання з базою даних"""
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT version();")
            version = cursor.fetchone()[0]
            print(f"\n✓ З'єднання з базою даних успішне")
            print(f"✓ Версія PostgreSQL: {version}")
    except Exception as e:
        print(f"✗ Помилка з'єднання з базою даних: {str(e)}")
        sys.exit(1)

def check_models_data():
    """Перевірка даних в моделях"""
    models = [
        (MeditationTrack, "Медитації"),
        (TopContent, "Рекомендований контент"),
        (Course, "Курси"),
        (Workshop, "Воркшопи"),
        (Group, "Групи"),
        (Event, "Події"),
        (UserProfile, "Профілі користувачів"),
        (FavoriteMeditation, "Улюблені медитації"),
        (Comment, "Коментарі")
    ]
    
    print("\nПеревірка даних в моделях:")
    for model, name in models:
        count = model.objects.count()
        print(f"\n{name}:")
        print(f"- Кількість записів: {count}")
        
        if count > 0:
            # Перевірка на NULL значення
            for field in model._meta.fields:
                if not field.null:
                    null_count = model.objects.filter(**{field.name: None}).count()
                    if null_count > 0:
                        print(f"✗ Знайдено {null_count} записів з NULL в полі {field.name}")

def check_file_paths():
    """Перевірка шляхів до файлів"""
    print("\nПеревірка шляхів до файлів:")
    
    # Перевірка медіа файлів
    for track in MeditationTrack.objects.all():
        if track.audio_file:
            if not track.audio_file.storage.exists(track.audio_file.name):
                print(f"✗ Аудіофайл не знайдено: {track.audio_file.name}")
        if track.image:
            if not track.image.storage.exists(track.image.name):
                print(f"✗ Зображення не знайдено: {track.image.name}")

def check_url_validity():
    """Перевірка валідності URL"""
    print("\nПеревірка URL-адрес:")
    validate = URLValidator()
    
    # Перевірка video_url
    for model in [MeditationTrack, TopContent, Course]:
        for obj in model.objects.exclude(video_url__isnull=True):
            try:
                validate(obj.video_url)
            except ValidationError:
                print(f"✗ Неправильний URL в {model.__name__}: {obj.video_url}")

def check_user_data():
    """Перевірка даних користувачів"""
    print("\nПеревірка даних користувачів:")
    
    # Перевірка профілів
    users_without_profiles = User.objects.filter(profile__isnull=True)
    if users_without_profiles.exists():
        print(f"✗ Користувачі без профілів: {users_without_profiles.count()}")
        for user in users_without_profiles:
            print(f"  - {user.username}")

def check_relationships():
    """Перевірка зв'язків між моделями"""
    print("\nПеревірка зв'язків між моделями:")
    
    # Перевірка коментарів
    orphaned_comments = Comment.objects.filter(meditation__isnull=True)
    if orphaned_comments.exists():
        print(f"✗ Коментарі без медитацій: {orphaned_comments.count()}")
    
    # Перевірка улюблених
    orphaned_favorites = FavoriteMeditation.objects.filter(meditation__isnull=True)
    if orphaned_favorites.exists():
        print(f"✗ Улюблені без медитацій: {orphaned_favorites.count()}")

def main():
    """Головна функція перевірки"""
    print("Початок діагностики бази даних...")
    
    check_database_connection()
    check_models_data()
    check_file_paths()
    check_url_validity()
    check_user_data()
    check_relationships()
    
    print("\nДіагностика завершена!")

if __name__ == "__main__":
    main() 