# Generated by Django 4.1 on 2024-01-26 12:00

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('nlp_processor', '0005_similararticlepair'),
    ]

    operations = [
        migrations.RenameField(
            model_name='similararticlepair',
            old_name='similarity_score',
            new_name='hash_similarity_score',
        ),
    ]
