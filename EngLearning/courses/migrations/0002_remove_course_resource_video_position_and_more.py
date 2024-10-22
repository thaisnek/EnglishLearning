# Generated by Django 5.1.1 on 2024-10-15 14:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='course',
            name='resource',
        ),
        migrations.AddField(
            model_name='video',
            name='position',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='lesson',
            name='position',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]
