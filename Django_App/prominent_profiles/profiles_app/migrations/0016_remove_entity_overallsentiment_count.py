# Generated by Django 4.1 on 2024-01-05 12:35

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('profiles_app', '0015_alter_entity_overallsentiment_count'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='entity',
            name='overallsentiment_count',
        ),
    ]
