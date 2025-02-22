from django.core.management.base import BaseCommand
from django.conf import settings
import boto3
import os

class Command(BaseCommand):
    help = 'Завантажує animations.css до S3'

    def handle(self, *args, **options):
        if settings.AWS_ACCESS_KEY_ID and settings.AWS_SECRET_ACCESS_KEY:
            s3 = boto3.client(
                's3',
                aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                region_name=settings.AWS_S3_REGION_NAME
            )
            
            # Шлях до animations.css в проекті
            css_path = os.path.join(settings.BASE_DIR, 'static', 'meditation', 'css', 'animations.css')
            
            try:
                # Завантаження файлу в S3
                with open(css_path, 'rb') as file:
                    s3.upload_fileobj(
                        file,
                        settings.AWS_STORAGE_BUCKET_NAME,
                        'static/meditation/css/animations.css',
                        ExtraArgs={
                            'ContentType': 'text/css',
                            'ACL': 'public-read',
                            'CacheControl': 'public, max-age=31536000'
                        }
                    )
                self.stdout.write(
                    self.style.SUCCESS('Successfully uploaded animations.css to S3')
                )
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'Failed to upload animations.css: {str(e)}')
                )
        else:
            self.stdout.write(
                self.style.WARNING('AWS credentials not configured')
            ) 