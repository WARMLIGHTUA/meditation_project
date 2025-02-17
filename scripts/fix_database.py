import os
import sys
import django
from django.db import connection, transaction
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.files.storage import default_storage

# Налаштування Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'meditation_app.settings')
django.setup()

# Імпортуємо моделі після налаштування Django
from meditation.models import (
    MeditationTrack, TopContent, Course, Workshop,
    Group, Event, UserProfile, FavoriteMeditation, Comment
)

def fix_null_values():
    """Виправлення NULL значень в обов'язкових полях"""
    print("\nВиправлення NULL значень...")
    
    models = [MeditationTrack, TopContent, Course, Workshop, Group, Event]
    default_values = {
        'title': 'Без назви',
        'description': 'Опис відсутній',
        'author': 'Анонім',
        'rating': 4.5,
    }
    
    for model in models:
        with transaction.atomic():
            for field in model._meta.fields:
                if not field.null:
                    # Встановлюємо значення за замовчуванням для NULL полів
                    null_objects = model.objects.filter(**{field.name: None})
                    if null_objects.exists():
                        print(f"Виправлення {null_objects.count()} записів в {model.__name__}.{field.name}")
                        for obj in null_objects:
                            setattr(obj, field.name, default_values.get(field.name, ''))
                            obj.save()

def fix_file_paths():
    """Виправлення шляхів до файлів"""
    print("\nВиправлення шляхів до файлів...")
    
    with transaction.atomic():
        for track in MeditationTrack.objects.all():
            # Перевірка аудіофайлів
            if track.audio_file and not default_storage.exists(track.audio_file.name):
                print(f"Видалення посилання на відсутній аудіофайл: {track.audio_file.name}")
                track.audio_file = None
            
            # Перевірка зображень
            if track.image and not default_storage.exists(track.image.name):
                print(f"Видалення посилання на відсутнє зображення: {track.image.name}")
                track.image = None
            
            track.save()

def fix_invalid_urls():
    """Виправлення неправильних URL"""
    print("\nВиправлення неправильних URL...")
    
    models = [MeditationTrack, TopContent, Course]
    for model in models:
        with transaction.atomic():
            for obj in model.objects.exclude(video_url__isnull=True):
                try:
                    # Спроба виправити URL
                    if not obj.video_url.startswith(('http://', 'https://')):
                        print(f"Виправлення URL в {model.__name__}: {obj.video_url}")
                        obj.video_url = f"https://{obj.video_url}"
                        obj.save()
                except ValidationError:
                    print(f"Видалення неправильного URL в {model.__name__}: {obj.video_url}")
                    obj.video_url = None
                    obj.save()

def fix_user_profiles():
    """Створення відсутніх профілів користувачів"""
    print("\nСтворення профілів користувачів...")
    
    with transaction.atomic():
        users_without_profiles = User.objects.filter(profile__isnull=True)
        for user in users_without_profiles:
            print(f"Створення профілю для користувача: {user.username}")
            UserProfile.objects.create(
                user=user,
                first_name=user.first_name or '',
                last_name=user.last_name or '',
                gender='O'  # Other як значення за замовчуванням
            )

def fix_orphaned_records():
    """Видалення записів-сиріт"""
    print("\nВидалення записів-сиріт...")
    
    with transaction.atomic():
        # Видалення коментарів без медитацій
        orphaned_comments = Comment.objects.filter(meditation__isnull=True)
        if orphaned_comments.exists():
            print(f"Видалення {orphaned_comments.count()} коментарів-сиріт")
            orphaned_comments.delete()
        
        # Видалення улюблених без медитацій
        orphaned_favorites = FavoriteMeditation.objects.filter(meditation__isnull=True)
        if orphaned_favorites.exists():
            print(f"Видалення {orphaned_favorites.count()} улюблених-сиріт")
            orphaned_favorites.delete()

def main():
    """Головна функція виправлення"""
    print("Початок виправлення проблем в базі даних...")
    
    try:
        fix_null_values()
        fix_file_paths()
        fix_invalid_urls()
        fix_user_profiles()
        fix_orphaned_records()
        
        print("\nВиправлення успішно завершено!")
    except Exception as e:
        print(f"\n✗ Помилка під час виправлення: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main() 