# Generated by Django 5.1.1 on 2024-10-21 02:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0010_remove_lesson_serial_number'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='lesson',
            name='is_preview',
        ),
        migrations.AddField(
            model_name='video',
            name='is_preview',
            field=models.BooleanField(default=False),
        ),
    ]
