# Generated by Django 4.1 on 2023-12-29 15:26

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('profiles_app', '0010_alter_article_similar_articles'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='article',
            name='similar_articles',
        ),
    ]