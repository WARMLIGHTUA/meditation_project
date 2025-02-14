# Generated by Django 5.0.2 on 2025-02-11 10:44

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='MeditationTrack',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200)),
                ('description', models.TextField()),
                ('audio_file', models.FileField(upload_to='meditation_tracks/')),
                ('duration', models.IntegerField(help_text='Duration in seconds')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
    ]
