# Generated by Django 5.1.1 on 2024-10-17 09:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0003_video_title'),
    ]

    operations = [
        migrations.AddField(
            model_name='course',
            name='slug',
            field=models.SlugField(default='default-slug', max_length=500, unique=True),
        ),
    ]