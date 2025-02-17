from django.core.management.base import BaseCommand
from django.db import connection
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.validators import URLValidator
from meditation.models import (
    MeditationTrack, TopContent, Course, Workshop,
    Group, Event, UserProfile, FavoriteMeditation, Comment
)

class Command(BaseCommand):
    help = 'Перевірка бази даних на наявність проблем'

    def handle(self, *args, **options):
        self.stdout.write("Початок діагностики бази даних...")
        
        self.check_database_connection()
        self.check_models_data()
        self.check_file_paths()
        self.check_url_validity()
        self.check_user_data()
        self.check_relationships()
        
        self.stdout.write(self.style.SUCCESS("\nДіагностика завершена!"))

    def check_database_connection(self):
        """Перевірка з'єднання з базою даних"""
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT version();")
                version = cursor.fetchone()[0]
                self.stdout.write(self.style.SUCCESS(f"\n✓ З'єднання з базою даних успішне"))
                self.stdout.write(self.style.SUCCESS(f"✓ Версія PostgreSQL: {version}"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"✗ Помилка з'єднання з базою даних: {str(e)}"))

    def check_models_data(self):
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
        
        self.stdout.write("\nПеревірка даних в моделях:")
        for model, name in models:
            count = model.objects.count()
            self.stdout.write(f"\n{name}:")
            self.stdout.write(f"- Кількість записів: {count}")
            
            if count > 0:
                # Перевірка на NULL значення
                for field in model._meta.fields:
                    if not field.null:
                        null_count = model.objects.filter(**{field.name: None}).count()
                        if null_count > 0:
                            self.stdout.write(
                                self.style.WARNING(f"✗ Знайдено {null_count} записів з NULL в полі {field.name}")
                            )

    def check_file_paths(self):
        """Перевірка шляхів до файлів"""
        self.stdout.write("\nПеревірка шляхів до файлів:")
        
        # Перевірка медіа файлів
        for track in MeditationTrack.objects.all():
            if track.audio_file:
                if not track.audio_file.storage.exists(track.audio_file.name):
                    self.stdout.write(
                        self.style.WARNING(f"✗ Аудіофайл не знайдено: {track.audio_file.name}")
                    )
            if track.image:
                if not track.image.storage.exists(track.image.name):
                    self.stdout.write(
                        self.style.WARNING(f"✗ Зображення не знайдено: {track.image.name}")
                    )

    def check_url_validity(self):
        """Перевірка валідності URL"""
        self.stdout.write("\nПеревірка URL-адрес:")
        validate = URLValidator()
        
        # Перевірка video_url
        for model in [MeditationTrack, TopContent, Course]:
            for obj in model.objects.exclude(video_url__isnull=True):
                try:
                    validate(obj.video_url)
                except ValidationError:
                    self.stdout.write(
                        self.style.WARNING(f"✗ Неправильний URL в {model.__name__}: {obj.video_url}")
                    )

    def check_user_data(self):
        """Перевірка даних користувачів"""
        self.stdout.write("\nПеревірка даних користувачів:")
        
        # Перевірка профілів
        users_without_profiles = User.objects.filter(profile__isnull=True)
        if users_without_profiles.exists():
            self.stdout.write(
                self.style.WARNING(f"✗ Користувачі без профілів: {users_without_profiles.count()}")
            )
            for user in users_without_profiles:
                self.stdout.write(f"  - {user.username}")

    def check_relationships(self):
        """Перевірка зв'язків між моделями"""
        self.stdout.write("\nПеревірка зв'язків між моделями:")
        
        # Перевірка коментарів
        orphaned_comments = Comment.objects.filter(meditation__isnull=True)
        if orphaned_comments.exists():
            self.stdout.write(
                self.style.WARNING(f"✗ Коментарі без медитацій: {orphaned_comments.count()}")
            )
        
        # Перевірка улюблених
        orphaned_favorites = FavoriteMeditation.objects.filter(meditation__isnull=True)
        if orphaned_favorites.exists():
            self.stdout.write(
                self.style.WARNING(f"✗ Улюблені без медитацій: {orphaned_favorites.count()}")
            ) 