# Generated by Django 4.1 on 2024-02-06 18:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('nlp_processor', '0013_alter_articlestatistics_fuzzy_hash'),
    ]

    operations = [
        migrations.AlterField(
            model_name='articlestatistics',
            name='fuzzy_hash',
            field=models.CharField(max_length=128, null=True),
        ),
    ]
