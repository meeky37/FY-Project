# Generated by Django 4.1 on 2023-12-29 14:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('profiles_app', '0003_article_similar_articles'),
    ]

    operations = [
        migrations.AddField(
            model_name='article',
            name='tfidf_vector',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
