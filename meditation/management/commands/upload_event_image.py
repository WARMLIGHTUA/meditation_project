from django.core.management.base import BaseCommand
from django.conf import settings
import boto3
import os

class Command(BaseCommand):
    help = 'Завантажує зображення за замовчуванням для подій до S3'

    def handle(self, *args, **options):
        if settings.AWS_ACCESS_KEY_ID and settings.AWS_SECRET_ACCESS_KEY:
            s3 = boto3.client(
                's3',
                aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                region_name=settings.AWS_S3_REGION_NAME
            )
            
            # Шлях до зображення за замовчуванням
            image_path = 'static/meditation/default-event.jpg'
            local_path = os.path.join(settings.BASE_DIR, 'static', 'meditation', 'default-event.jpg')
            
            try:
                # Завантаження файлу в S3
                with open(local_path, 'rb') as file:
                    s3.upload_fileobj(
                        file,
                        settings.AWS_STORAGE_BUCKET_NAME,
                        image_path,
                        ExtraArgs={
                            'ContentType': 'image/jpeg',
                            'ACL': 'public-read',
                            'CacheControl': 'public, max-age=31536000',
                            'ContentDisposition': 'inline',
                            'Metadata': {
                                'Access-Control-Allow-Origin': '*',
                                'Access-Control-Allow-Methods': 'GET, HEAD',
                                'Access-Control-Allow-Headers': 'Origin, X-Requested-With, Content-Type, Accept'
                            }
                        }
                    )
                    
                    # Встановлюємо публічні права доступу для об'єкта
                    s3.put_object_acl(
                        ACL='public-read',
                        Bucket=settings.AWS_STORAGE_BUCKET_NAME,
                        Key=image_path
                    )
                    
                self.stdout.write(
                    self.style.SUCCESS('Successfully uploaded default event image to S3')
                )
            except FileNotFoundError:
                self.stdout.write(
                    self.style.ERROR(f'File not found: {local_path}')
                )
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'Failed to upload default event image: {str(e)}')
                ) 