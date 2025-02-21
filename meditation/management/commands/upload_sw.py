from django.core.management.base import BaseCommand
from django.conf import settings
import boto3
import os

class Command(BaseCommand):
    help = 'Uploads sw.js to S3 root'

    def handle(self, *args, **options):
        if settings.AWS_ACCESS_KEY_ID and settings.AWS_SECRET_ACCESS_KEY:
            s3 = boto3.client(
                's3',
                aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                region_name=settings.AWS_S3_REGION_NAME
            )
            
            # Шлях до sw.js в проекті
            sw_path = os.path.join(settings.BASE_DIR, 'static', 'sw.js')
            
            try:
                # Завантаження файлу в корінь бакета
                with open(sw_path, 'rb') as file:
                    s3.upload_fileobj(
                        file,
                        settings.AWS_STORAGE_BUCKET_NAME,
                        'sw.js',
                        ExtraArgs={
                            'ContentType': 'application/javascript',
                            'ACL': 'public-read',
                            'CacheControl': 'no-cache, no-store, must-revalidate',
                            'Expires': '0',
                            'Metadata': {
                                'Access-Control-Allow-Origin': '*',
                                'Access-Control-Allow-Methods': 'GET, OPTIONS',
                                'Access-Control-Allow-Headers': 'Origin, X-Requested-With, Content-Type, Accept'
                            }
                        }
                    )
                self.stdout.write(
                    self.style.SUCCESS('Successfully uploaded sw.js to S3')
                )
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'Failed to upload sw.js: {str(e)}')
                )
        else:
            self.stdout.write(
                self.style.WARNING('AWS credentials not configured')
            ) 