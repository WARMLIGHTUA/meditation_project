#!/usr/bin/env python
import os
import sys
import boto3
import datetime
import subprocess
from pathlib import Path
import logging
import pytz

# Налаштування логування
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('backup.log')
    ]
)
logger = logging.getLogger(__name__)

# Конфігурація
BACKUP_DIR = Path('backups')
DB_BACKUP_FILENAME = 'db_backup_{}.sql'
MEDIA_BACKUP_FILENAME = 'media_backup_{}.tar.gz'
TIMEZONE = 'Europe/Kiev'

def get_database_url():
    """Отримання URL бази даних з Railway"""
    try:
        db_url = os.environ.get('DATABASE_URL')
        if not db_url:
            raise ValueError("DATABASE_URL не знайдено в змінних середовища")
        return db_url
    except Exception as e:
        logger.error(f"Помилка отримання DATABASE_URL: {e}")
        sys.exit(1)

def create_backup_dir():
    """Створення директорії для бекапів"""
    try:
        BACKUP_DIR.mkdir(exist_ok=True)
        logger.info(f"Створено директорію для бекапів: {BACKUP_DIR}")
    except Exception as e:
        logger.error(f"Помилка створення директорії для бекапів: {e}")
        sys.exit(1)

def backup_database(db_url):
    """Створення бекапу бази даних"""
    try:
        timestamp = datetime.datetime.now(pytz.timezone(TIMEZONE)).strftime('%Y%m%d_%H%M%S')
        backup_file = BACKUP_DIR / DB_BACKUP_FILENAME.format(timestamp)
        
        # Парсинг URL бази даних
        from urllib.parse import urlparse
        url = urlparse(db_url)
        
        # Створення змінних середовища для pg_dump
        env = os.environ.copy()
        env['PGPASSWORD'] = url.password
        
        # Виконання pg_dump
        command = [
            'pg_dump',
            '-h', url.hostname,
            '-p', str(url.port),
            '-U', url.username,
            '-d', url.path[1:],  # Видаляємо початковий /
            '-F', 'c',  # Формат custom
            '-f', str(backup_file)
        ]
        
        subprocess.run(command, env=env, check=True)
        logger.info(f"Створено бекап бази даних: {backup_file}")
        return backup_file
    except Exception as e:
        logger.error(f"Помилка створення бекапу бази даних: {e}")
        return None

def backup_media():
    """Створення бекапу медіафайлів"""
    try:
        timestamp = datetime.datetime.now(pytz.timezone(TIMEZONE)).strftime('%Y%m%d_%H%M%S')
        backup_file = BACKUP_DIR / MEDIA_BACKUP_FILENAME.format(timestamp)
        
        # Створення архіву медіафайлів
        command = [
            'tar',
            '-czf',
            str(backup_file),
            'media',
            'mediafiles'
        ]
        
        subprocess.run(command, check=True)
        logger.info(f"Створено бекап медіафайлів: {backup_file}")
        return backup_file
    except Exception as e:
        logger.error(f"Помилка створення бекапу медіафайлів: {e}")
        return None

def upload_to_s3(file_path):
    """Завантаження бекапу в S3"""
    try:
        s3 = boto3.client(
            's3',
            aws_access_key_id=os.environ.get('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.environ.get('AWS_SECRET_ACCESS_KEY'),
            region_name=os.environ.get('AWS_S3_REGION_NAME', 'eu-central-1')
        )
        
        bucket = os.environ.get('AWS_STORAGE_BUCKET_NAME')
        key = f'backups/{file_path.name}'
        
        s3.upload_file(str(file_path), bucket, key)
        logger.info(f"Завантажено бекап в S3: {key}")
        
        # Видалення локального файлу після завантаження
        file_path.unlink()
        logger.info(f"Видалено локальний файл: {file_path}")
    except Exception as e:
        logger.error(f"Помилка завантаження в S3: {e}")

def cleanup_old_backups():
    """Видалення старих бекапів з S3"""
    try:
        s3 = boto3.client(
            's3',
            aws_access_key_id=os.environ.get('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.environ.get('AWS_SECRET_ACCESS_KEY'),
            region_name=os.environ.get('AWS_S3_REGION_NAME', 'eu-central-1')
        )
        
        bucket = os.environ.get('AWS_STORAGE_BUCKET_NAME')
        
        # Отримання списку всіх бекапів
        response = s3.list_objects_v2(
            Bucket=bucket,
            Prefix='backups/'
        )
        
        if 'Contents' in response:
            # Сортування за датою
            backups = sorted(
                response['Contents'],
                key=lambda x: x['LastModified']
            )
            
            # Залишаємо тільки останні 5 бекапів кожного типу
            db_backups = [b for b in backups if 'db_backup' in b['Key']]
            media_backups = [b for b in backups if 'media_backup' in b['Key']]
            
            # Видалення старих бекапів
            for backup in db_backups[:-5] + media_backups[:-5]:
                s3.delete_object(
                    Bucket=bucket,
                    Key=backup['Key']
                )
                logger.info(f"Видалено старий бекап: {backup['Key']}")
    except Exception as e:
        logger.error(f"Помилка очищення старих бекапів: {e}")

def main():
    """Головна функція"""
    try:
        logger.info("Початок процесу бекапу")
        
        # Створення директорії для бекапів
        create_backup_dir()
        
        # Бекап бази даних
        db_url = get_database_url()
        db_backup = backup_database(db_url)
        if db_backup:
            upload_to_s3(db_backup)
        
        # Бекап медіафайлів
        media_backup = backup_media()
        if media_backup:
            upload_to_s3(media_backup)
        
        # Очищення старих бекапів
        cleanup_old_backups()
        
        logger.info("Процес бекапу завершено успішно")
    except Exception as e:
        logger.error(f"Помилка в процесі бекапу: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main() 