# Generated by Django 4.1 on 2024-01-27 18:36

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('nlp_processor', '0010_similararticlepair_average_count_diff'),
    ]

    operations = [
        migrations.RenameField(
            model_name='similararticlepair',
            old_name='average_count_diff',
            new_name='avg_count_diff',
        ),
    ]
