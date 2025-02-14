from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator, MaxValueValidator

# Create your models here.

class BaseContent(models.Model):
    """
    Базова абстрактна модель для всього контенту в додатку.
    Містить спільні поля, які використовуються в усіх типах контенту.
    """
    title = models.CharField(_('Title'), max_length=200)
    description = models.TextField(_('Description'))
    image = models.ImageField(_('Image'), upload_to='content_images/', null=True, blank=True)
    video_url = models.URLField(_('Video URL'), null=True, blank=True)
    created_at = models.DateTimeField(_('Created at'), auto_now_add=True)
    rating = models.DecimalField(
        _('Rating'),
        max_digits=2,
        decimal_places=1,
        default=4.5,
        validators=[MinValueValidator(0), MaxValueValidator(5.0)]
    )
    author = models.CharField(_('Author'), max_length=100, default='Anonymous')

    class Meta:
        abstract = True

class MeditationTrack(BaseContent):
    """
    Модель для медитаційних треків.
    Включає аудіофайл та тривалість медитації.
    """
    audio_file = models.FileField(
        _('Audio File'),
        upload_to='meditation_tracks/',
        help_text=_('Upload MP3 or WAV file')
    )
    duration = models.IntegerField(
        _('Duration'),
        help_text=_('Duration in minutes'),
        validators=[MinValueValidator(1)]
    )

    class Meta:
        verbose_name = _('Meditation Track')
        verbose_name_plural = _('Meditation Tracks')

    def __str__(self):
        return f"{self.title} ({self.duration} min)"

class TopContent(BaseContent):
    """
    Модель для відображення найкращого контенту на головній сторінці.
    """
    featured = models.BooleanField(_('Featured'), default=False)
    
    class Meta:
        verbose_name = _('Top Content')
        verbose_name_plural = _('Top Content')

    def __str__(self):
        return f"{self.title} ({'Featured' if self.featured else 'Not Featured'})"

class Course(BaseContent):
    """
    Модель для навчальних курсів медитації.
    """
    duration_weeks = models.IntegerField(
        _('Duration in weeks'),
        help_text=_('Duration in weeks'),
        validators=[MinValueValidator(1)]
    )
    price = models.DecimalField(
        _('Price'),
        max_digits=10,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)]
    )
    
    class Meta:
        verbose_name = _('Course')
        verbose_name_plural = _('Courses')

    def __str__(self):
        return f"{self.title} ({self.duration_weeks} weeks)"

class Workshop(BaseContent):
    """
    Модель для воркшопів та майстер-класів.
    """
    date = models.DateTimeField(_('Date and Time'))
    location = models.CharField(_('Location'), max_length=200)
    price = models.DecimalField(
        _('Price'),
        max_digits=10,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)]
    )
    max_participants = models.IntegerField(
        _('Maximum Participants'),
        default=20,
        validators=[MinValueValidator(1)]
    )
    
    class Meta:
        verbose_name = _('Workshop')
        verbose_name_plural = _('Workshops')

    def __str__(self):
        return f"{self.title} ({self.date.strftime('%Y-%m-%d %H:%M')})"

class Group(BaseContent):
    """
    Модель для груп медитації.
    """
    members_count = models.IntegerField(
        _('Members Count'),
        default=0,
        validators=[MinValueValidator(0)]
    )
    is_private = models.BooleanField(_('Private Group'), default=False)
    
    class Meta:
        verbose_name = _('Group')
        verbose_name_plural = _('Groups')

    def __str__(self):
        return f"{self.title} ({'Private' if self.is_private else 'Public'})"

class Event(BaseContent):
    """
    Модель для подій та зустрічей.
    """
    date = models.DateTimeField(_('Date and Time'))
    location = models.CharField(_('Location'), max_length=200)
    is_online = models.BooleanField(_('Online Event'), default=False)
    max_participants = models.IntegerField(
        _('Maximum Participants'),
        default=100,
        validators=[MinValueValidator(1)]
    )
    
    class Meta:
        verbose_name = _('Event')
        verbose_name_plural = _('Events')

    def __str__(self):
        return f"{self.title} ({self.date.strftime('%Y-%m-%d %H:%M')})"

class UserProfile(models.Model):
    """
    Розширена модель профілю користувача.
    """
    GENDER_CHOICES = [
        ('M', _('Male')),
        ('F', _('Female')),
        ('O', _('Other')),
    ]
    
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='profile',
        verbose_name=_('User')
    )
    first_name = models.CharField(_('First Name'), max_length=100, blank=True)
    last_name = models.CharField(_('Last Name'), max_length=100, blank=True)
    birth_year = models.IntegerField(
        _('Birth Year'),
        null=True,
        blank=True,
        validators=[
            MinValueValidator(1900),
            MaxValueValidator(2100)
        ]
    )
    gender = models.CharField(
        _('Gender'),
        max_length=1,
        choices=GENDER_CHOICES
    )
    
    class Meta:
        verbose_name = _('User Profile')
        verbose_name_plural = _('User Profiles')

    def __str__(self):
        return f"{self.user.username}'s Profile"

    def get_full_name(self):
        """Повертає повне ім'я користувача."""
        return f"{self.first_name} {self.last_name}".strip() or self.user.username

class FavoriteMeditation(models.Model):
    """
    Модель для збереження улюблених медитацій користувача
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='favorite_meditations',
        verbose_name=_('User')
    )
    meditation = models.ForeignKey(
        MeditationTrack,
        on_delete=models.CASCADE,
        related_name='favorited_by',
        verbose_name=_('Meditation')
    )
    added_at = models.DateTimeField(_('Added at'), auto_now_add=True)

    class Meta:
        verbose_name = _('Favorite Meditation')
        verbose_name_plural = _('Favorite Meditations')
        unique_together = ['user', 'meditation']

    def __str__(self):
        return f"{self.user.username} - {self.meditation.title}"

class PageBackground(models.Model):
    """
    Модель для налаштування фону сторінок
    """
    PAGE_CHOICES = [
        ('home', _('Home Page')),
        ('tracks', _('Tracks Page')),
        ('courses', _('Courses Page')),
        ('workshops', _('Workshops Page')),
        ('groups', _('Groups Page')),
        ('events', _('Events Page')),
        ('favorites', _('Favorites Page')),
    ]
    
    THEME_CHOICES = [
        ('light', _('Light Theme')),
        ('dark', _('Dark Theme')),
    ]
    
    page = models.CharField(
        _('Page'),
        max_length=20,
        choices=PAGE_CHOICES,
        unique=True
    )
    theme = models.CharField(
        _('Theme'),
        max_length=10,
        choices=THEME_CHOICES,
        default='light'
    )
    background_image = models.ImageField(
        _('Background Image'),
        upload_to='page_backgrounds/',
        null=True,
        blank=True
    )
    background_video = models.FileField(
        _('Background Video'),
        upload_to='page_backgrounds/',
        null=True,
        blank=True,
        help_text=_('Upload MP4 or WebM file')
    )
    background_color = models.CharField(
        _('Background Color'),
        max_length=7,
        default='#FFFFFF',
        help_text=_('HEX color code (e.g. #FFFFFF)')
    )
    background_opacity = models.DecimalField(
        _('Background Opacity'),
        max_digits=3,
        decimal_places=2,
        default=1.0,
        validators=[MinValueValidator(0), MaxValueValidator(1.0)]
    )
    
    class Meta:
        verbose_name = _('Page Background')
        verbose_name_plural = _('Page Backgrounds')
        unique_together = ['page', 'theme']

    def __str__(self):
        return f"{self.get_page_display()} - {self.get_theme_display()}"
