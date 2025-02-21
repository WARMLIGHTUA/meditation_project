from django.core.management.base import BaseCommand
from django.conf import settings
import boto3
import json
import os

class Command(BaseCommand):
    help = 'Configures CORS for S3 bucket'

    def handle(self, *args, **options):
        if settings.AWS_ACCESS_KEY_ID and settings.AWS_SECRET_ACCESS_KEY:
            s3 = boto3.client(
                's3',
                aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                region_name=settings.AWS_S3_REGION_NAME
            )
            
            try:
                # Читаємо конфігурацію CORS з файлу
                cors_path = os.path.join(settings.BASE_DIR, 's3_cors.json')
                with open(cors_path, 'r') as file:
                    cors_configuration = json.load(file)

                # Застосовуємо конфігурацію CORS до бакета
                s3.put_bucket_cors(
                    Bucket=settings.AWS_STORAGE_BUCKET_NAME,
                    CORSConfiguration={
                        'CORSRules': cors_configuration
                    }
                )
                
                self.stdout.write(
                    self.style.SUCCESS('Successfully configured CORS for S3 bucket')
                )
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'Failed to configure CORS: {str(e)}')
                )
        else:
            self.stdout.write(
                self.style.WARNING('AWS credentials not configured')
            ) 