# Generated by Django 4.1 on 2024-02-06 18:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('profiles_app', '0021_article_similar_rejection'),
    ]

    operations = [
        migrations.AlterField(
            model_name='article',
            name='headline',
            field=models.CharField(max_length=500, null=True),
        ),
    ]
