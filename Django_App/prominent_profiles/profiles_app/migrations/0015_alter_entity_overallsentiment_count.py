# Generated by Django 4.1 on 2024-01-05 12:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('profiles_app', '0014_entity_overallsentiment_count'),
    ]

    operations = [
        migrations.AlterField(
            model_name='entity',
            name='overallsentiment_count',
            field=models.IntegerField(default=0),
        ),
    ]
