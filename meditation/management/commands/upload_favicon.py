from django.core.management.base import BaseCommand
from django.conf import settings
import boto3
import os

class Command(BaseCommand):
    help = 'Завантажує favicon.ico до S3'

    def handle(self, *args, **options):
        if settings.AWS_ACCESS_KEY_ID and settings.AWS_SECRET_ACCESS_KEY:
            s3 = boto3.client(
                's3',
                aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                region_name=settings.AWS_S3_REGION_NAME
            )
            
            # Шлях до favicon.ico
            icon_path = os.path.join(settings.BASE_DIR, 'static', 'meditation', 'icons', 'favicon.ico')
            s3_path = 'static/meditation/icons/favicon.ico'
            
            try:
                # Створюємо директорію, якщо вона не існує
                os.makedirs(os.path.dirname(icon_path), exist_ok=True)
                
                # Якщо favicon.ico не існує, створюємо його з placeholder
                if not os.path.exists(icon_path):
                    import requests
                    response = requests.get('https://picsum.photos/32/32')
                    with open(icon_path, 'wb') as f:
                        f.write(response.content)
                
                # Завантаження файлу в S3
                with open(icon_path, 'rb') as file:
                    s3.upload_fileobj(
                        file,
                        settings.AWS_STORAGE_BUCKET_NAME,
                        s3_path,
                        ExtraArgs={
                            'ContentType': 'image/x-icon',
                            'ACL': 'public-read',
                            'CacheControl': 'max-age=31536000,public,immutable'
                        }
                    )
                self.stdout.write(
                    self.style.SUCCESS('Successfully uploaded favicon.ico to S3')
                )
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'Failed to upload favicon.ico: {str(e)}')
                ) 