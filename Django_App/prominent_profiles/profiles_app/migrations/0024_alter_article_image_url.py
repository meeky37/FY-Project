# Generated by Django 4.1 on 2024-02-06 18:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('profiles_app', '0023_alter_article_headline_alter_article_url'),
    ]

    operations = [
        migrations.AlterField(
            model_name='article',
            name='image_url',
            field=models.CharField(blank=True, max_length=500, null=True),
        ),
    ]
