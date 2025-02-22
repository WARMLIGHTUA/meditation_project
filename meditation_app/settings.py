"""
Django settings for meditation_app project.

Generated by 'django-admin startproject' using Django 5.0.2.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.0/ref/settings/
"""

import os
from pathlib import Path
import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration
from sentry_sdk.integrations.logging import LoggingIntegration
from sentry_sdk.integrations.redis import RedisIntegration
import logging
import dj_database_url
from storages.backends.s3boto3 import S3Boto3Storage

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.environ.get('DJANGO_DEBUG', 'False') == 'True'

ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', '').split(',')
CSRF_TRUSTED_ORIGINS = os.environ.get('CSRF_TRUSTED_ORIGINS', '').split(',')

# Налаштування Sentry
def traces_sampler(sampling_context):
    if sampling_context.get("parent_sampled") is False:
        return 0
    
    path = sampling_context.get("wsgi_environ", {}).get("PATH_INFO", "")
    
    if path.startswith(("/health", "/static", "/media")):
        return 0
    
    if path.startswith("/admin"):
        return 0.5
        
    return float(os.environ.get("SENTRY_TRACES_SAMPLE_RATE", "0.1"))

sentry_logging = LoggingIntegration(
    level=logging.INFO,
    event_level=logging.ERROR
)

# Підготовка інтеграцій для Sentry
sentry_integrations = [
    DjangoIntegration(),
    sentry_logging,
]

# Додаємо Redis інтеграцію тільки якщо Redis доступний
try:
    import redis
    from sentry_sdk.integrations.redis import RedisIntegration
    sentry_integrations.append(RedisIntegration())
except ImportError:
    pass

sentry_sdk.init(
    dsn=os.environ.get('SENTRY_DSN'),
    integrations=sentry_integrations,
    traces_sample_rate=float(os.environ.get('SENTRY_TRACES_SAMPLE_RATE', '0.1')),
    profiles_sample_rate=float(os.environ.get('SENTRY_PROFILES_SAMPLE_RATE', '0.1')),
    send_default_pii=True,
    release=os.environ.get('RAILWAY_GIT_COMMIT_SHA', 'development'),
    environment=os.environ.get('ENVIRONMENT_NAME', 'development'),
    traces_sampler=traces_sampler,
    ignore_errors=[
        'django.exceptions.DisallowedHost',
    ],
    max_breadcrumbs=50,
)

# Application definition
INSTALLED_APPS = [
    'modeltranslation',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'whitenoise.runserver_nostatic',
    'meditation.apps.MeditationConfig',
    'crispy_forms',
    'crispy_bootstrap4',
    'storages',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# Налаштування WhiteNoise
WHITENOISE_USE_FINDERS = True
WHITENOISE_MANIFEST_STRICT = False
WHITENOISE_ALLOW_ALL_ORIGINS = True

# Безпека
if not DEBUG:
    SECURE_SSL_REDIRECT = True
    CSRF_COOKIE_SECURE = True
    SESSION_COOKIE_SECURE = True
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

ROOT_URLCONF = 'meditation_app.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'meditation.context_processors.page_background',
            ],
        },
    },
]

WSGI_APPLICATION = 'meditation_app.wsgi.application'

# Database
# Спочатку спробуємо використати DATABASE_URL
database_url = os.environ.get('DATABASE_URL')
if database_url:
    DATABASES = {
        'default': dj_database_url.config(
            default=database_url,
            conn_max_age=60,
            conn_health_checks=True,
            ssl_require=True,
            engine='django.db.backends.postgresql'
        )
    }
    # Додаємо додаткові налаштування PostgreSQL
    DATABASES['default']['OPTIONS'] = {
        'client_encoding': 'UTF8',
        'application_name': 'meditation_app',
        'sslmode': 'require',
        'keepalives': 1,
        'keepalives_idle': 30,
        'keepalives_interval': 10,
        'keepalives_count': 5
    }
else:
    # Якщо DATABASE_URL не встановлено, використовуємо окремі змінні
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': os.environ.get('PGDATABASE', 'railway'),
            'USER': os.environ.get('PGUSER', 'postgres'),
            'PASSWORD': os.environ.get('PGPASSWORD', ''),
            'HOST': os.environ.get('PGHOST', 'localhost'),
            'PORT': os.environ.get('PGPORT', '5432'),
            'OPTIONS': {
                'client_encoding': 'UTF8',
                'application_name': 'meditation_app',
                'sslmode': 'require',
                'keepalives': 1,
                'keepalives_idle': 30,
                'keepalives_interval': 10,
                'keepalives_count': 5
            }
        }
    }

# Додаємо налаштування для автоматичного закриття з'єднань
CONN_MAX_AGE = 60
CONN_HEALTH_CHECKS = True

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {
            'min_length': 10,
        }
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
LANGUAGE_CODE = 'uk'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

LANGUAGES = [
    ('uk', 'Українська'),
    ('en', 'English'),
    ('fr', 'Français'),
]

LOCALE_PATHS = [
    os.path.join(BASE_DIR, 'locale'),
]

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),
]

# AWS S3 налаштування
if os.environ.get('ENVIRONMENT_NAME') == 'production':
    AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')
    AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')
    AWS_STORAGE_BUCKET_NAME = os.environ.get('AWS_STORAGE_BUCKET_NAME')
    AWS_S3_REGION_NAME = os.environ.get('AWS_S3_REGION_NAME')
    AWS_S3_FILE_OVERWRITE = False
    AWS_DEFAULT_ACL = 'public-read'
    AWS_S3_SIGNATURE_VERSION = 's3v4'
    AWS_S3_ADDRESSING_STYLE = 'virtual'
    AWS_S3_VERIFY = True
    AWS_QUERYSTRING_AUTH = False
    AWS_S3_OBJECT_PARAMETERS = {
        'CacheControl': 'max-age=86400,public',
        'ACL': 'public-read'
    }
    
    # Налаштування для статичних та медіа файлів
    AWS_S3_CUSTOM_DOMAIN = f'{AWS_STORAGE_BUCKET_NAME}.s3.{AWS_S3_REGION_NAME}.amazonaws.com'
    
    # Окремі класи для статичних та медіа файлів
    class StaticStorage(S3Boto3Storage):
        location = 'static'
        default_acl = 'public-read'
        file_overwrite = True
        querystring_auth = False
        custom_domain = AWS_S3_CUSTOM_DOMAIN
        object_parameters = {
            'CacheControl': 'max-age=86400,public',
            'ACL': 'public-read'
        }
    
    class MediaStorage(S3Boto3Storage):
        location = 'media'
        default_acl = 'public-read'
        file_overwrite = False
        querystring_auth = False
        custom_domain = AWS_S3_CUSTOM_DOMAIN
        object_parameters = {
            'CacheControl': 'max-age=86400,public',
            'ACL': 'public-read'
        }
        
    class ServiceWorkerStorage(S3Boto3Storage):
        location = ''  # корінь бакета
        default_acl = 'public-read'
        file_overwrite = True
        querystring_auth = False
        custom_domain = AWS_S3_CUSTOM_DOMAIN
        object_parameters = {
            'CacheControl': 'no-cache, no-store, must-revalidate',
            'ACL': 'public-read',
            'ContentType': 'application/javascript'
        }
    
    # Використовуємо окремі класи для зберігання
    STATICFILES_STORAGE = 'meditation_app.settings.StaticStorage'
    DEFAULT_FILE_STORAGE = 'meditation_app.settings.MediaStorage'
    SERVICE_WORKER_STORAGE = 'meditation_app.settings.ServiceWorkerStorage'
    
    # URL для статичних та медіа файлів
    STATIC_URL = f'https://{AWS_S3_CUSTOM_DOMAIN}/static/'
    MEDIA_URL = f'https://{AWS_S3_CUSTOM_DOMAIN}/media/'
else:
    STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
    DEFAULT_FILE_STORAGE = 'django.core.files.storage.FileSystemStorage'
    MEDIA_URL = '/media/'
    MEDIA_ROOT = os.path.join(BASE_DIR, 'mediafiles')

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Crispy Forms
CRISPY_TEMPLATE_PACK = 'bootstrap4'

# Логування
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
        'file': {
            'class': 'logging.FileHandler',
            'filename': 'django.log',
        },
    },
    'root': {
        'handlers': ['console', 'file'],
        'level': os.environ.get('DJANGO_LOG_LEVEL', 'INFO'),
    },
}